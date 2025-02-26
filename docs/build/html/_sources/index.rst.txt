.. pvdeg documentation master file, created by
   sphinx-quickstart on Thu Jan 18 15:25:51 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. .. image:: ../../tutorials_and_tools/pvdeg_logo.png
..    :width: 500

.. .. image:: ../_static/logo-vectors/PVdeg-Logo-Horiz-Color.svg


Welcome to GeoGridFusion!
==============================================================

GeoGridFusion enables scientists, researchers, and users to develop living stores 
of data relevant to their projects; make scientific computing outside of an HPC 
environment easier; enhances ease of reproducibility; stores geospatial data 
and interact with it lazily. Datasets grow overtime to suit users' needs.

.. The source code for pvdeg is hosted on `github <https://github.com/NREL/GeoGridFusion>`_. Please see the :ref:`installation` page for installation help.

See :ref:`tutorials` to learn how to use and experiment with various functionalities

.. .. image::  ./_static/grid-points-dir.svg.svg
.. image::  ./_static/grid-to-tree.svg.svg
   :alt: PVDeg-Flow diagram.


How the Model Works
===================

Coupled with pvdeg for weather download, GeoGridFusion re-maps and stores geospatial gridded weather/meteorological data.

It is meant to be a simple package that allows for the storage of geospatial data incrementally, allowing total stored data to grow overtime.
Enabling the execution of geospatial analyses beyond the confines of NREL's high-performance computing capabilities.

Citing GeoGridFusion
==========================

If you use this calculator in a published work, please cite:

.. code-block::

   Ford, Tobin. "GeoGridFusion" NREL Github 2025, Software Record SWR 25-19.

.. 
   Please also cite the DOI corresponding to the specific version that you used.
   DOIs are listed at Zenodo.org. `linked here <https://zenodo.org/records/13760911>`_

.. code-block::

   Martin Springer, Tobin Ford, Matt, MDKempe, Silvana Ovaitt, AidanWesley, joe karas, Mark Campanelli, Derek M Holsapple, and Kevin Anderson. “NREL/PVDegradationTools: 0.4.2.” Zenodo, 2024. doi:10.5281/zenodo.13760911.


.. toctree::
   :hidden:
   :titlesonly:

   user_guide/index
   api
   whatsnew/index

..
   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
