Guide to install the XACC package with tnqvm-exatn accelerator and qcor compiler
-----
1 - Import Docker image with xacc framework installed 

$ docker run --security-opt seccomp=unconfined --init -it -p 3000:3000 xacc/xacc

You can navigate to localhost:3000 in your web browser or attach the docker container to your local IDE 

In home/dev/:

2 - Install qcor using qcor_install.sh script

$ chmod +x qcor_install.sh 

$ ./qcor_install.sh

This will install it in /usr/local/aide-qc/qcor

3 - Install exatn  (this will install it in $HOME/.exatn)

$ apt-get update

$ apt-get install gcc-8 g++-8 gfortran-8 libblas-dev liblapack-dev libopenmpi-dev libopenblas-dev

$ python3 -m pip install --upgrade cmake

$ git clone --recursive https://github.com/ornl-qci/exatn.git

$ cd exatn

$ git submodule init

$ git submodule update --init --recursive

$ mkdir build && cd build

cmake .. -DCMAKE_BUILD_TYPE=Release -DEXATN_BUILD_TESTS=TRUE -DBLAS_LIB=OPENBLAS -DBLAS_PATH=/usr/lib/x86_64-linux-gnu/openblas-pthread

    (Optional)
  * For execution on NVIDIA GPU:
  -DENABLE_CUDA=True

    You can adjust the NVIDIA GPU compute capability like this:

    -DCUDA_ARCH_BIN=70

    For GPU execution via very recent CUDA versions with the GNU compiler:

    -DCUDA_HOST_COMPILER=<PATH_TO_CUDA_COMPATIBLE_GNU_C++_COMPILER>

    If you want to leverage NVIDIA cuQuantum framework, set these:

    -DCUTENSOR=TRUE 

    -DCUTENSOR_PATH=<PATH_TO_CUTENSOR_ROOT>

    -DCUQUANTUM=TRUE 

    -DCUQUANTUM_PATH=<PATH_TO_CUQUANTUM_ROOT>

    Note that you will need to install cuTensor and cuQuantum from their Linux tar archives provided by NVIDIA. Additionally, after installing cuTensor, copy all cuTensor dynamic libraries (.so) from <CUTENSOR_ROOT>/lib/<CUDA_VERSION> to <CUTENSOR_ROOT>/lib.

  * For multi-node execution via MPI:

    -DMPI_LIB=<MPI_CHOICE> 

    -DMPI_ROOT_DIR=<PATH_TO_MPI_ROOT>

    where the choices are OPENMPI or MPICH. Note that the OPENMPI choice also covers its derivatives, for example Spectrum MPI. The MPICH choice
    also covers its derivatives, for example Cray-MPICH. You may also need to set 
    -DMPI_BIN_PATH=<PATH_TO_MPI_BINARIES> in case they are in a different location.

$ make install

4 - Install tnqvm in /usr/local/aideqc/qcor 

$ git clone --recursive https://github.com/ornl-qci/tnqvm.git  (remove and re-clone it if already in /home/dev)

$ cd tnqvm

$ mkdir build && cd build 

$ cmake .. -DXACC_DIR=/usr/local/aideqc/qcor -DEXATN_DIR=$HOME/.exatn -DCMAKE_INSTALL_PREFIX=/usr/local/aideqc/qcor 

$ make install

Make sure to set PYTHONPATH as: (can add it to .bashrc)

$ export PYTHONPATH=/usr/local/aideqc/qcor:/root/.xacc 

You may need to install some Python packages to run the files in `XACC\` (e.g., $ pip install -U scikit-learn scipy matplotlib)
