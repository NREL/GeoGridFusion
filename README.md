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
<tr>
  <td>Documentation</td>
  <td>
	<a href='https://geogridfusion.readthedocs.io'>
	    <img src='https://readthedocs.org/projects/pvdegradationtools/badge/?version=stable' alt='Documentation Status' />
	</a>
  </td>
</tr>

<tr>
  <td>Build status</td>
  <td>
   <a href="https://github.com/NREL/GeoGridFusion/actions/workflows/pytest.yml?query=branch%3Amain">
      <img src="https://github.com/NREL/GeoGridFusion/actions/workflows/pytest.yml/badge.svg?branch=main" alt="GitHub Actions Testing Status" />
   </a>
   <!-- <a href="https://codecov.io/gh/NREL/PVDegradationTools" >
   <img src="https://codecov.io/gh/NREL/PVDegradationTools/graph/badge.svg?token=4I24S8BTG7"/>
   </a> -->
  </td>
</tr> 
</table>


Documentation
=============

Documentation is available in [ReadTheDocs](https://GeoGridFusion.readthedocs.io) where you can find more details on the API functions.


# Installation

GeoGridFusion utilizes PostgreSQL to store geospatial data. If you do not already have postgres, you will need to install it. If you do not have admin privileges you will have to follow the steps below, rather than using the installer.

## Installing PostgreSQL without Admin

### Download binaries  
[Source](https://www.enterprisedb.com/download-postgresql-binaries)

### Extract binaries
Extract the PostgreSQL binaries to ``C:\Users\{username}\AppData\Roaming\``

{username} is the name of your user account. You must be logged into this user to have full rights for all files below ``C:\Users\{username}\``

Once the binaries are extracted, you should have a directory named pgsql in the ``C:\Users\tford\AppData\Roaming directory``.

### Add PostgreSQL to User Environment Variables

To tell the operating system where the binaries are located, we must add the files to the User Environment Variables. 

Add the directory C:\Users\{username}\AppData\Roaming\pgsql\bin to the User Environment Variables for {username}. 

    windows 11 instructions
    --------------------------
    1) search and open "Edit environment variables for your account"
    2) Once Environmental Variables window is open, select "Path" in the User variables for {username} box and click "Edit".
    3) Click "New" and add the directory containing the binaries (i.e. C:\Users\{username}\AppData\Roaming\pgsql\bin)
    4) Click "Ok" on the Edit environment variable window
    5) Click "Ok" on the Environment Variables window

### Check PostgreSQL version

To verify that PostgreSQL has ben installed correctly, we can run the following command from the command prompt.

    postgres -V

If you get a which displays a version number then you have installed PostgreSQL.

    C:\Users\tford> postgres -V
    postgres (PostgreSQL) 17.4


### Verify GeoGridFusion Startup

Start a python environment which has geogridfusion installed. This can be a python interactive shell or jupyter notebook, etc. Run the following code block to see if we can connect to the database.

    # >>> represents a line of python, other lines are output from the program

    >>> import geogridfusion
    >>> conn = geogridfusion.start()
    Starting Postgres subprocess...
    PostgreSQL connection established after 3.22 seconds.

    >>> conn
    <connection object at 0x0000020A67C76460; dsn: 'dbname=postgres user=postgres host=localhost port=5432', closed: 0>

If geogridfusion.start() returns a connection object then we have successfully connected to the postgres server.


## Install Spatial Extensions (PostGIS)

### Download and move files

Download a postgis binary bundle from [osgeo source](https://download.osgeo.org/postgis/windows/).

#### Automatic Install

**Simple script coming soon that will do this for us (no manual copying)**

#### Manual Install Instructions

Unzip it and copy the files as described below. 


| Source (PostGIS ZIP)                | Destination (PostgreSQL)                                      |
|------------------------------------|----------------------------------------------------------------|
| lib\*.dll                          | C:\Users\YourName\PostgreSQL\lib\                           |
| share\extension\*                  | C:\Users\YourName\PostgreSQL\share\extension\              |
| share\postgis\* (if it exists)     | C:\Users\YourName\PostgreSQL\share\postgis\                |
| bin\* (optional tools)             | C:\Users\YourName\PostgreSQL\bin\                          |

### Create Tables

The final step in setting up the database is creating the tables that will store our data. We can do this by running ``initialize_tables``. Now you will be ready to use geogridfusion.

    import geogridfusion

    conn = geogridfusion.start()
    geogridfusion.initialize_tables(conn=conn)

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