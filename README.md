# GeoGridFusion 

This repo contains utilities to allow for the storage of user downloaded geospatial weather data by providing a local datastore for storage and spatial queries, supporting large-scale analyses without the need for high-performance computing (HPC) resources.

<!-- <table>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/NREL/GeoGridFusion/blob/master/LICENSE.md">
    <img src="https://img.shields.io/pypi/l/pvlib.svg" alt="license" />
    </a>
</td>
</tr>
<tr> -->
  <!-- <td>Publications</td>
  <td>
     <a href="https://doi.org/10.5281/zenodo.8088578"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.8088578.svg" alt="DOI"></a>
  </td> -->
<!-- </tr>
<tr> -->
  <!-- <td>Documentation</td>
  <td>
	<a href='https://PVDegradationTools.readthedocs.io'>
	    <img src='https://readthedocs.org/projects/pvdegradationtools/badge/?version=stable' alt='Documentation Status' />
	</a> -->
  <!-- </td> -->
<!-- </tr>
<tr>
  <td>Build status</td>
  <td>
   <a href="https://github.com/NREL/PVDegradationTools/actions/workflows/pytest.yml?query=branch%3Amain">
      <img src="https://github.com/NREL/PVDegradationTools/actions/workflows/pytest.yml/badge.svg?branch=main" alt="GitHub Actions Testing Status" />
   </a>
   <a href="https://codecov.io/gh/NREL/PVDegradationTools" >
   <img src="https://codecov.io/gh/NREL/PVDegradationTools/graph/badge.svg?token=4I24S8BTG7"/>
   </a>
  </td>
</tr> -->
<!-- </table> -->

Tutorials
=========

### Locally

You can also run the tutorial locally in a virtual environment, i.e., `venv` or
[miniconda](https://docs.conda.io/en/latest/miniconda.html).

1. Create and activate a new environment, e.g., on Mac/Linux terminal with `venv`:
   ```
   python -m venv geogridfusion
   . geogridfusioon/bin/activate
   ```
   or with `conda`:
   ```
   conda create -n geogridfusion
   conda activate geogridfustion
   ```

1. Install `pvdeg` into the new environment with `pip`:
   ```
   python -m pip install geogridfusion
   ```

1. Start a Jupyter session:

   ```
   jupyter notebook
   ```

1. Use the file explorer in Jupyter lab to browse to `tutorials`
   and start the first Tutorial.


Documentation
=============

Documentation is available in [ReadTheDocs](https://GeoGridFusion.readthedocs.io) where you can find more details on the API functions.

Not available yet

Installation
============

Install with:

    pip install geogridstore

For developer installation, clone the repository, navigate to the folder location and install as:

    pip install -e .[all]


License
=======

<!-- [BSD 3-clause](https://github.com/NREL/PVDegradationTools/blob/main/LICENSE.md) -->
Not available yet


Contributing
=======

We welcome contributiosn to this software, but please read the copyright license agreement (cla-1.0.md), with instructions on signing it in sign-CLA.md. For questions, email us.


Getting support
===============

If you suspect that you may have discovered a bug or if you'd like to
change something about pvdeg, then please make an issue on our
[GitHub issues page](hhttps://github.com/NREL/GeoGridFusion/issues).


Citing
======

If you use this functions in a published work, please cite:  

   Ford, Tobin. NREL GitHub 2025, Software Record SWR-25-19

And/or the specific release from Zenodo:
