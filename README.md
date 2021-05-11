<img width="100" alt="logo" src="https://github.com/harvard-nrg/mrscrub/blob/main/ext/logo.png">

Mr. Scrub: de-identify those DICOMs
===================================
Mr. Scrub (or "MR scrub") is a command line tool to scrub away identifying 
information from DICOM files.

## Table of contents
1. [Documentation](#documentation)
2. [Installation](#installation)
3. [De-identification profiles](#de-identification-profiles)
4. [Usage](#usage)

## Documentation
There's much more detailed documentation at [mrscrub.readthedocs.io](https://mrscrub.readthedocs.io).

## Installation
Just `pip`

```bash
python -m pip install mrscrub
```

## De-identification profiles
De-identification profiles determine which DICOM fields should be scubbed and 
how. You can find an example profile [here](https://github.com/harvard-nrg/mrscrub/blob/main/mrscrub/configs/SSBC_v1.0.yaml).
``mrscrub`` ships with some profiles by default, which you can load with

```bash
scrub.py -c NAME [args]
```

or you can create one yourself and pass in the file name 

```bash
scrub.py -c ./profile.yaml [args]
```

## Usage
For a simple example, load up one of the saved de-identification profiles 
along with an `-i|--input` directory (of DICOM files) and an `-o|--output` 
directory where you want to save the scrubbed files

```bash
scrub.py -c SSBC_v1.0 -i <input dir> -o <output dir>
```

