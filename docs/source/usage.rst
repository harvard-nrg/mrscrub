Usage
=====
Before you can get started, you'll need a `de-identification profile <profiles.html>`_. 
You can load a built-in profile from the ``mrscrub`` package, or supply one of 
your own.

Arguments
---------
The main command line tool is ``scrub.py`` which accepts the following 
arguments

* ``-c|--config``: a built-in `de-identification profile <profiles.html>`_, or a custom one
* ``-i|--input``: directory of DICOM files
* ``-o|--output``: directory to save de-identified "scrubbed" files

Running
-------
The primary command line tool is ``scrub.py``

using a built-in profile
^^^^^^^^^^^^^^^^^^^^^^^^
To use a built-in de-identification profile, pass the name of the profile to 
the ``-c|--config`` argument. The following example uses the ``SSBC_v1.0`` 
profile ::

    scrub.py -c SSBC_v1.0 -i <input dir> -o <output dir>

using a custom profile
^^^^^^^^^^^^^^^^^^^^^^
To use a custom `de-identification profile <profiles.html>`_, pass the filename 
to the ``-c|--config`` argument. The following example assumes your profile was 
saved as ``./profile.yaml`` ::

    scrub.py -c ./profile.yaml -i <input dir> -o <output dir>

