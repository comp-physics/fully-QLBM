Fully quantum algorithm for  lattice Boltzmann methods with application to partial differential equations
==========

Code for reproducing the results of the "Fully quantum algorithm for lattice Boltzmann methods with application to partial differential equations" paper, https://arxiv.org/abs/2305.07148.

_Authors: Fatima Ezahra Chrit, Sriharsha Kocherla, Bryan Gard, Eugene F. Dumitrescu, Alexander Alexeev, Spencer H. Bryngelson_

Files
-----
 * `code/`
   * `Qiskit/`
      * `QLBM_diffusion_D1Q2.ipynb`: QLBM algorithm solving diffusion equation using D1Q2 scheme (Section III and IV-A) 
      * `QLBM_Burgers_D1Q2.ipynb`: QLBM algorithm solving Burgers equation using D1Q2 scheme (Section III and IV-A) 
      * `QLBM_diffusion_D1Q3.ipynb`: QLBM algorithm solving diffusion equation using D1Q3 scheme (Section IV-B) 
      * `QLBM_diffusion_D1Q2_measurement_free.ipynb`: QLBM algorithm solving diffusion equation using D1Q2 scheme and IPE algorithm (Section IV-C)
   * `XACC/`
      * `QLBM_diffusion_D1Q2_xacc.py`: QLBM algorithm solving diffusion equation using D1Q2 scheme on XACC framework (Section V) 
 * `xacc_install/`
   * `Readme.md`: Guide to install the XACC package with tnqvm-exatn accelerator and qcor compiler
   * `qcor_install.sh`: Script to install qcor compiler

Run the code
-----
You'll need a working Python environment to run the code. To run the files in Qiskit/, you need to  install the Qiskit package (<https://qiskit.org/>). To run the files in xacc/, you need to install the XACC package with tnqvm-exatn accelerator (<https://xacc.readthedocs.io/en/latest/install.html>) and qcor compiler (<https://aide-qc.github.io/deploy/getting_started/>). 
One possible way to do that using Docker containers is given in `xacc_install/Readme.md`.

