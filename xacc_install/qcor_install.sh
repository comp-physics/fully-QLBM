#!/bin/bash
set -e
export use_brew=false
if [ "$1" == "--use-brew" ]; then
   export use_brew=true
fi

if [ "$1" == "-qcs" ]; then
    # This is for installing aide-qc stack on 
    # Rigetti QCS JupyterLab IDE. Does not require :)
    
    # pull down llvm and xacc deb packages
    wget https://raw.githubusercontent.com/aide-qc/deploy/master/xacc/debian/focal/xacc-1.0.0.deb    
    wget https://raw.githubusercontent.com/aide-qc/deploy/master/clang_syntax_handler/debian/focal/LLVM-12.0.0git-Linux.deb
    dpkg -x xacc-1.0.0.deb $HOME/.aideqc_install 
    dpkg -x LLVM-12.0.0git-Linux.deb $HOME/.aideqc_install     
    python3 -m pip install cmake ipopo --user 

    git clone https://github.com/ornl-qci/qcor
    cd qcor && mkdir build && cd build
    CC=gcc CXX=g++ cmake .. -DLLVM_ROOT=$HOME/.aideqc_install/usr/local/aideqc/llvm \
                            -DXACC_DIR=$HOME/.aideqc_install/usr/local/aideqc/qcor \
                            -DMLIR_DIR=$HOME/.aideqc_install/usr/local/aideqc/llvm/lib/cmake/mlir \
                            -DCMAKE_CXX_FLAGS="-D__STDC_FORMAT_MACROS" 
    make -j4 install
    cd ../../ && rm -rf qcor *.deb 
    
    echo ""
    echo "AIDE-QC installed on Rigetti QCS."
    echo ""
    echo "Your QCOR install location is "
    echo "$HOME/.aideqc_install/usr/local/aideqc/qcor"
    echo ""
    echo "Export your PATH to include the qcor binary executable location:"
    echo "export PATH=\$PATH:$HOME/.aideqc_install/usr/local/aideqc/qcor/bin"
    echo ""
    echo "To use the Python API, please run the following (and add to your .bashrc or .bash_profile)"
    echo "export PYTHONPATH=\$PYTHONPATH:$HOME/.aideqc_install/usr/local/aideqc/qcor"
    echo ""
    exit 0
fi

export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=false
UNAME=$(uname | tr "[:upper:]" "[:lower:]")
# If Linux, try to determine specific distribution
if [ "$UNAME" == "linux" ]; then
    # If available, use LSB to identify distribution
    if [ -f /etc/lsb-release -o -d /etc/lsb-release.d ]; then
        export DISTRO=$(lsb_release -i | cut -d: -f2 | sed s/'^\t'//)
    # Otherwise, use release info file
    else
        export DISTRO=$(ls -d /etc/[A-Za-z]*[_-][rv]e[lr]* | grep -v "lsb" | cut -d'/' -f3 | cut -d'-' -f1 | cut -d'_' -f1)
    fi
fi

# For everything else (or if above failed), just use generic identifier
[ "$DISTRO" == "" ] && export DISTRO=$UNAME

# if Ubuntu, install lapack
if [ "$DISTRO" == "Ubuntu" ]; then
    apt-get update -y && apt-get install -y wget gnupg lsb-release curl liblapack-dev git gcc g++
    if [ "$use_brew" == "false" ]; then
       wget -qO- https://aide-qc.github.io/deploy/aide_qc/debian/PUBLIC-KEY.gpg | apt-key add -
       if [ ! -e "/etc/apt/sources.list.d/aide-qc.list" ]; then
          wget -qO- "https://aide-qc.github.io/deploy/aide_qc/debian/$(lsb_release -cs)/aide-qc.list" | tee -a /etc/apt/sources.list.d/aide-qc.list
       fi
       apt-get update
       apt-get install -y qcor
       if [ "$?" -eq "0" ]; then
          echo "AIDE-QC installed via apt-get."
          echo ""
          echo ""
          echo "Your XACC and QCOR install location is "
          echo "/usr/local/aideqc/qcor"
          echo ""
          echo "To use the Python API, please run the following (and add to your .bashrc)"
          echo "export PYTHONPATH=$PYTHONPATH:/usr/local/aideqc/qcor"
          exit 0
       else
          echo "Could not install via apt-get, will try Homebrew."
          read -p "Would you like to try the Homebrew install?? " -n 1 -r
          echo    # (optional) move to a new line
          if [[ $REPLY =~ ^[Nn]$ ]]
          then
            exit 1
          fi
       fi
    else
       echo "Skipping apt-get install, will try homebrew at user request (--use-brew)."

       # If this is 18.04, then need to install special build-essential with glibc 2.29
       export ubuntu_distro=$(lsb_release -cs)
       if [ $ubuntu_distro == "bionic" ]; then
           apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
           echo "deb http://ftp.us.debian.org/debian testing main contrib non-free" | tee -a /etc/apt/sources.list
           apt-get update && apt-get install -y build-essential || true
       else
           echo "Ubuntu distro was not bionic, it was $ubuntu_distro"
       fi
    fi

elif [[ $DISTRO == "fedora"* ]]; then
    dnf update -y && dnf install -y gcc gcc-c++ lapack-devel git
fi

if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Installing it now..."
    CI=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

# May be possible that brew is not in PATH after install
if ! command -v brew &> /dev/null
then
   if [ "$UNAME" == "darwin" ]; then 
      echo "Could not find brew in PATH, setting up environment for Mac OS X."
      echo 'eval $(/usr/local/bin/brew shellenv)' >> $HOME/.bash_profile
      eval $(/usr/local/bin/brew shellenv)
   else 
      echo "Could not find brew in PATH, setting up homebrew environment for Linux."
      echo 'eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)' >> $HOME/.bashrc
      eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
   fi
fi 

# If we still can't find brew, then we should fail
if ! command -v brew &> /dev/null
then 
   echo "Still unable to locate Homebrew. Install manually, instructions at https://brew.sh"
   exit 1
fi

brew tap aide-qc/deploy
brew install qcor
python3 -m pip install --user ipopo cmake 
qcor -rebuild-pch
echo "AIDE-QC installed via Homebrew."
echo ""
echo ""
echo "Your XACC install location is "
brew --prefix xacc 
echo ""
echo "Your QCOR install location is "
brew --prefix qcor
echo ""
echo "To use the Python API, please run the following (and add to your .bashrc or .bash_profile)"
echo "export PYTHONPATH=$PYTHONPATH:$(brew --prefix xacc):$(brew --prefix qcor)"
