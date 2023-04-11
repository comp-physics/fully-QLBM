# QLBM algorithm solving diffusion equation using D1Q2 scheme on XACC framework (Section V) 
# Syntax: python3 QLBM_diffusion_D1Q2_xacc.py -qpu <qpu> -shots <#shots>
# qpu can be qpp, tnqvm[tnqvm-visitor:exatn-mps], etc.
import xacc
import sys, os, json, numpy as np
from qcor import *
from collections import Counter
import matplotlib.pyplot as plt
import time, math, pickle
from sklearn.metrics import mean_squared_error

# Alternative to the following two lines is to run
# from the IDE terminal: export PYTHONPATH=$PYTHONPATH:$HOME/.xacc
from pathlib import Path
sys.path.insert(1, str(Path.home()) + '/.xacc')

# D1Q2 lattice constants
D = 0.5    #diffusion constant
w = np.array([0.5, 0.5]) # weight coeffecients
cx = np.array([1, -1])   #lattice velocities
csq = 1   #square of sound speed
ux = 0.  # advection x-velocity

def compute_feq(rho, w, cx, ux, csq):
    feq = np.zeros((2,M))
    for i in range(2):
        feq[i] = w[i] * (1 + cx[i]*ux/csq) * rho
    return feq

def ini(x, w, cx, ux, csq):
    M = len(x)
    rho = np.ones(M)    #Gaussian distribution as initial density
    rho = 1/4 * np.exp(-(x-mu0)**2 / sigma0**2) + 1/2  
    feq = compute_feq(rho, w, cx, ux, csq)
    return feq, rho

def update_encoding(f):
    for k in range(M):
        for i in range(2):    
            amp0 = np.sqrt(1-f[i][k])
            amp1 = np.sqrt(f[i][k])
            theta[i+2*k] = 2*np.arccos(amp0)
    return theta

def _remove_space_underscore(bitstring):
    """Removes all spaces and underscores from bitstring"""
    return bitstring.replace(" ", "").replace("_", "")

def computeMarginalCounts(counts, indices):
    new_counts = Counter()
    for key, val in counts.items():
        new_key = "".join([_remove_space_underscore(key)[idx] for idx in indices])
        # new_key = "".join([_remove_space_underscore(key)[-idx - 1] for idx in indices])
        new_counts[new_key] += val
    return new_counts

def readOutProbas(counts, numberOfShots, M):
    qubit_counts = [computeMarginalCounts(counts, [qubit]) for qubit in range(2*M)]
    print(qubit_counts)

    for i in range(0, len(qubit_counts)):
        for k, v in qubit_counts[i].items():
            qubit_counts[i][k] /= numberOfShots

    #read post collision probabilities
    fout = np.zeros((2,M))
    for k in range(M):
        for i in range(2):
            fout[i][k] = qubit_counts[i+2*k]['1'] 
    return fout

def computeStreamingPattern(n):
    if (n >= 4):  #minimum for streaming is 2 sites, corresonding to 4qubits
        #first pair of qubits
        streamingPattern = [n-2, 3]
        for i in range(2,n-3):
            if i%2 == 0:  
                streamingPattern.extend([i-2, i+3])
        #last pair of qubits
        streamingPattern.extend([n-4,1])
    else:
        streamingPattern = []
    return streamingPattern

def _get_ordered_swap(permutation_in):
    permutation = list(permutation_in[:])
    swap_list = []
    for i, val in enumerate(permutation):
        if val != i:
            j = permutation.index(i)
            swap_list.append((i, j))
            permutation[i], permutation[j] = permutation[j], permutation[i]
    swap_list.reverse()
    return swap_list

# Classical implementation of QLBM algorithm
# number operators
n1 = np.array([[0, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 0, 0],
              [0, 0, 0, 1]])
n2 = np.array([[0, 0, 0, 0],
              [0, 0, 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]])
 
# collision operator  
C_Diffusion = np.array([[1, 0, 0, 0],
                      [0, (1+complex(0,1))/2 , (1-complex(0,1))/2 , 0],
                      [0, (1-complex(0,1))/2 , (1+complex(0,1))/2 , 0],
                      [0, 0, 0, 1]])


def classicalOneTimeStep(fc, M):
#     initial combined state
    initial_state = np.zeros((M, 4))
    for i in range(M):
        amp00 = np.sqrt( (1-fc[0][i]) * (1-fc[1][i]) ) # 2nd index = lattice site
        amp10 = np.sqrt( (1-fc[0][i]) * fc[1][i] )
        amp01 = np.sqrt( (1-fc[1][i]) * fc[0][i] )
        amp11 = np.sqrt( fc[0][i] * fc[1][i] )
        initial_state[i][0] = amp00
        initial_state[i][1] = amp01
        initial_state[i][2] = amp10
        initial_state[i][3] = amp11
    
#     post-collision state (4xlattice_sites)
    post_collision_state = C_Diffusion.dot(initial_state.conjugate().transpose())
   # post-collision distribution
    post_collision_distribution = np.zeros((2, M))
    for i in range(M):
        post_collision_distribution[0][i] = post_collision_state.conjugate().transpose()[i].dot(n1.dot( post_collision_state.transpose()[i]))
        post_collision_distribution[1][i] = post_collision_state.conjugate().transpose()[i].dot(n2.dot( post_collision_state.transpose()[i]))

#     streaming step
    fc[0][1:M] = post_collision_distribution[0][0:M-1]
    fc[1][0:M-1] = post_collision_distribution[1][1:M]

#      periodic BC
    fc[0][0] = fc[0][M-1]
    fc[1][M-1] = fc[1][0]

    return fc

# Define the kernel
@qjit
def oneTimeStep(q : qreg, theta: List[float], M: int, swapList:List[Tuple[int, int]]):
    for i in range(q.size()):
        Ry(q[i], theta[i])
    # collision 
    for k in range(M):
        CX(q[0+2*k],q[1+2*k])
        U(q[0+2*k], np.pi/2, 0, np.pi)
        U(q[1+2*k], 0, 0, np.pi/4)
        CX(q[1+2*k],q[0+2*k])
        U(q[0+2*k], 0, 0, -np.pi/4)
        CX(q[1+2*k],q[0+2*k])
        U(q[0+2*k], 0, 0, np.pi/4)
        U(q[0+2*k], np.pi/2, 0, np.pi)
        CX(q[0+2*k],q[1+2*k])
    # quantum streaming
    for i, j in swapList:
        Swap(q[i], q[j])
    # measurement
    for i in range(q.size()):
        Measure(q[i])

# Simulation parameters 
L = 4  # domain length 
M = L+1  # number of lattice sites (from 0 to L)
n = 2*M   # number of qubits
x = np.array(range(M)) # 1D lattice
numberOfShots = int(sys.argv[4])  # number of shots
maxT = 1   # number of time steps
#initial condition: gaussian distribution
sigma0 = L/10  # mean
mu0 = int(np.ceil(L/2)) # variance

# Initialization
fini, rho = ini(x, w, cx, ux, csq)
fq_quantum = fini.copy()
fClassical = fini.copy()
theta = np.ones(n) #rotation angles of each qubit for encoding step

# Main loop
for t in range(1,maxT+1):
    print('t = ', t)
    # quantum implementation, quantum streaming
    theta = update_encoding(fq_quantum)
    swapList = _get_ordered_swap(np.array(computeStreamingPattern(n)))      # list of qubits to swap to implement quantum streaming
    q = qalloc(n)  #allocate n qubits
    oneTimeStep(q, theta, M, swapList)
    counts = q.counts()
    fq_quantum = readOutProbas(counts, numberOfShots, M)  # from counts to probabilities
    #periodic BC
    fq_quantum[0][0] = fq_quantum[0][M-1]
    fq_quantum[1][M-1] = fq_quantum[1][0]
    rhoq_quantum = fq_quantum[0] + fq_quantum[1]
    #classical implementation
    fClassical = classicalOneTimeStep(fClassical, M)
    rhoClassical = fClassical[0] + fClassical[1]
print('Done')    

MSE = mean_squared_error(rhoClassical, rhoq_quantum)
RMSE = math.sqrt(MSE)
print("RMSE of quantum solution with quantum streaming:\n", RMSE)

plt.plot(x, rhoq_quantum,'s', markersize = 6, markerfacecolor='none')
plt.plot(x, rhoClassical, 'k')
plt.legend(['quantum - quantum streaming', 'classical']) 
plt.xlabel('Lattice site')
plt.ylabel('Density')
