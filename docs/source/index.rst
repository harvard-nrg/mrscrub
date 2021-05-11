.. Mr. Scrub documentation master file, created by
   sphinx-quickstart on Wed May 12 08:27:27 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mr. Scrub's documentation!
=====================================
Mr. Scrub (or "MR scrub") is a simple command line tool to scrub away identifying 
information from DICOM files ::

    python -m pip install mrscrub
    scrub.py -c profile.yaml -i ./dicoms -o ./scrubbed

.. toctree::
   :maxdepth: 3

   installation
   usage
   profiles


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
