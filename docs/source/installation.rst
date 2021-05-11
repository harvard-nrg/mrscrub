Installation
============
If you're already familiar with Python, just use ``pip`` ::

    pip install mrscrub

macOS
-----
.. note::
   This installation process has been tested on macOS Catalina and Big Sur

I recommend installing Python 3 either by installing `Apple Xcode <https://apps.apple.com/us/app/xcode/id497799835?mt=12>`_
or by installing the very excellent `Homebrew <https://brew.sh>`_ package manager 
and running ``brew install python``.

Once you have Python 3 installed, open a terminal and execute the following 
command to install ``mrscrub`` :: 

    python3 -m pip install --user mrscrub

.. note::
   This will install ``scrub.py`` into ``~/Library/Python/3.9/bin/``. You'll 
   want to add this to your ``PATH`` with the following command ::

        export PATH="~/Library/Python/3.9/bin:$PATH"

CentOS
------
.. note::
   This installation process has been tested on CentOS 7.9

To install ``mrscrub``, open a terminal and execute the following command ::

    python3 -m pip install --user mrscrub

Ubuntu
------
.. note::
   This installation process has been tested on Ubuntu 21.04 LTS

Recent versions of Ubuntu come preinstalled with ``python3`` but not ``pip``
(or not always). To install ``pip``, open a terminal and execute the following 
commands ::

        sudo apt-get update
        sudo apt-get install python3-pip

Now, to install ``mrscrub``, open a terminal and execute the following 
command ::

    python3 -m pip install --user mrscrub

Windows
-------
.. note::
   This installation process has been tested on Windows 10 Enterprise

To install Python on Windows, open the Microsoft Store and search for Python
or click `this link <https://www.microsoft.com/store/productId/9P7QFQMJRFP7>`_. 
Install the latest version, which should be version 3.9 or higher.

Now, open Windows PowerShell and execute the following command to create a 
virtual environment ::

   python -m venv mrscrub

Now activate your virtual environment ::

   mrscrub\Scripts\activate

If you encounter the error ::

    mrscrub\Scripts\activate : File C:\Users\<user>\mrscrub\Scripts\Activate.ps1 
    cannot be loaded because running scripts is disabled on this system

You'll need to launch Windows PowerShell again as an administrator and set the 
system execution policy to ``remotesigned``. Execute the following command and 
choose ``[Y] Yes`` when asked to accept the new policy ::

    set-executionpolicy remotesigned

After you've successfully activated your virtual environment, install 
``mrscrub`` with the following command ::

   pip install mrscrub

