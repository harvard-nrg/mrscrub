<img width="100" alt="logo" src="https://github.com/harvard-nrg/mrscrub/blob/main/ext/logo.png">

Mr. Scrub: de-identify those DICOMs
===================================
Mr. Scrub (or "MR scrub") is a command line tool to scrub identifying 
information from DICOM files. 

> [!WARNING]  
> Siemens makes use of [Other Byte String](https://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.2.html) 
> private headers e.g., CSA Image Header Info `(0029, 1010)` and CSA Series Header Info `(0029, 1020)`. These 
> "binary blobs" are known to contain dates and UID references that embed dates. At this moment, MR Scrub does 
> not offer a complete solution for scrubbing these types of headers.

## Table of contents
1. [Documentation](#documentation)
2. [Installation](#installation)
3. [De-identification profiles](#de-identification-profiles)
4. [Usage](#usage)

## Documentation
There's more detailed documentation at [mrscrub.readthedocs.io](https://mrscrub.readthedocs.io).

## Installation
Just `pip`

```bash
python -m pip install mrscrub
```

## De-identification profiles
De-identification profiles determine which DICOM fields should be scubbed and 
how they should be scrubbed. You can find an example de-identifictation profile 
[here](https://github.com/harvard-nrg/mrscrub/blob/main/mrscrub/configs/PBN_v2.0.yaml).
``mrscrub`` ships with a few profiles by default, which you can load with

```bash
scrub.py -c NAME [args]
```

or you can create one yourself and pass the file name at the command line 

```bash
scrub.py -c ./profile.yaml [args]
```

## Usage
For a simple example, load up one of the saved de-identification profiles 
along with an `-i|--input` directory (of DICOM files) and an `-o|--output` 
directory where you want to save the scrubbed files

```bash
scrub.py -c PBN_v2.0 -i <input dir> -o <output dir>
```

