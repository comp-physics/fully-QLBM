### Fully quantum algorithm for mesoscale fluid simulations with application to partial differential equations

<p align="center"> 
<a href="https://lbesson.mit-license.org/">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" />
</a>
<a href="http://doi.org/10.1116/5.0217675">
  <img src="http://img.shields.io/badge/DOI-10.1116/5.0217675-B31B1B.svg" />
</a>
</p>

Archival repository for reproducing the paper,
`Full paper reference: Kocherla, S., Song, Z., Chrit, F. E., Gard, B., Dumitrescu, E. F., Alexeev, A., & Bryngelson, S. H. (2024). Fully quantum algorithm for lattice Boltzmann methods with application to partial differential equations. AVS Quantum Science, 6, 033806.`, which can be cited as
```bibtex
@article{kocherla24,
  author = {Kocherla, S. and Song, Z. and Chrit, F. E. and Gard, B. and Dumitrescu, E. F. and Alexeev, A. and Bryngelson, S. H.},
  title = {Fully quantum algorithm for lattice {B}oltzmann methods with application to partial differential equations},
  doi = {10.1116/5.0217675},
  year = {2024},
  volume = {6},
  pages = {033806},
  journal = {AVS Quantum Science},
}
```

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

