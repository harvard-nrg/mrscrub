import os
import zlib
import pytest
import shutil
import mrscrub
import pydicom
import tempfile
import subprocess as sp

DIR = os.path.dirname(__file__)
DICOMS = os.path.join(DIR, 'dicoms')
CONFIGS = os.path.join(os.path.dirname(mrscrub.__file__), 'configs')

class Empty:
    value = None

def crc(f):
    prev = 0
    for line in open(f, 'rb'):
        prev = zlib.crc32(line, prev)
    return '%X' % (prev & 0xFFFFFFFF)

def test_ssbc():
    tmpdir = tempfile.mkdtemp()
    cmd = [
        'scrub.py',
        '-c', 'SSBC_v1.0',
        '-i', os.path.join(DICOMS, 'harvard-ssbc'),
        '-o', tmpdir
    ]
    sp.check_output(cmd)
    for f in os.listdir(tmpdir):
        fullfile = os.path.join(tmpdir, f)
        ds = pydicom.read_file(fullfile)
        assert not ds.get((0x0008, 0x0050), Empty()).value
        assert (0x0029, 0x1020) not in ds
        assert not ds.get((0x0020, 0x0010), Empty()).value
        assert not ds.get((0x0010, 0x21b0), Empty()).value
        assert not ds.get((0x0008, 0x1080), Empty()).value
        assert not ds.get((0x0010, 0x2110), Empty()).value
        assert not ds.get((0x0010, 0x1081), Empty()).value
        assert not ds.get((0x0040, 0x3001), Empty()).value
        assert not ds.get((0x0008, 0x009d), Empty()).value
        assert not ds.get((0x0008, 0x009c), Empty()).value
        assert not ds.get((0x0010, 0x2150), Empty()).value
        assert not ds.get((0x0038, 0x0300), Empty()).value
        assert not ds.get((0x0010, 0x2160), Empty()).value
        assert not ds.get((0x0010, 0x1050), Empty()).value
        assert not ds.get((0x0010, 0x0021), Empty()).value
        assert not ds.get((0x0010, 0x21d0), Empty()).value
        assert not ds.get((0x0010, 0x2000), Empty()).value
        assert not ds.get((0x0010, 0x1090), Empty()).value
        assert not ds.get((0x0010, 0x1080), Empty()).value
        assert not ds.get((0x0008, 0x1060), Empty()).value
        assert not ds.get((0x0010, 0x2180), Empty()).value
        assert not ds.get((0x0010, 0x1000), Empty()).value
        assert not ds.get((0x0010, 0x1002), Empty()).value
        assert not ds.get((0x0010, 0x1001), Empty()).value
        assert not ds.get((0x0010, 0x1040), Empty()).value
        assert not ds.get((0x0010, 0x0035), Empty()).value
        assert not ds.get((0x0010, 0x0030), Empty()).value
        assert not ds.get((0x0010, 0x0033), Empty()).value
        assert not ds.get((0x0010, 0x1005), Empty()).value
        assert not ds.get((0x0010, 0x0032), Empty()).value
        assert not ds.get((0x0010, 0x4000), Empty()).value
        assert not ds.get((0x0010, 0x0034), Empty()).value
        assert not ds.get((0x0010, 0x0020), Empty()).value
        assert not ds.get((0x0010, 0x0050), Empty()).value
        assert not ds.get((0x0010, 0x1060), Empty()).value
        assert not ds.get((0x0010, 0x0010), Empty()).value
        assert not ds.get((0x0010, 0x0101), Empty()).value
        assert not ds.get((0x0010, 0x21f0), Empty()).value
        assert not ds.get((0x0010, 0x2203), Empty()).value
        assert not ds.get((0x0010, 0x1020), Empty()).value
        assert not ds.get((0x0010, 0x1021), Empty()).value
        assert not ds.get((0x0038, 0x0500), Empty()).value
        assert not ds.get((0x0010, 0x2155), Empty()).value
        assert not ds.get((0x0010, 0x2154), Empty()).value
        assert not ds.get((0x0008, 0x1052), Empty()).value
        assert not ds.get((0x0008, 0x1050), Empty()).value
        assert not ds.get((0x0038, 0x0100), Empty()).value
        assert not ds.get((0x4008, 0x0114), Empty()).value
        assert not ds.get((0x0008, 0x1048), Empty()).value
        assert not ds.get((0x0008, 0x1049), Empty()).value
        assert not ds.get((0x0008, 0x1062), Empty()).value
        assert not ds.get((0x0010, 0x21c0), Empty()).value
        assert not ds.get((0x0032, 0x1030), Empty()).value
        assert not ds.get((0x0010, 0x1100), Empty()).value
        assert not ds.get((0x0008, 0x0092), Empty()).value
        assert not ds.get((0x0008, 0x0096), Empty()).value
        assert not ds.get((0x0008, 0x0090), Empty()).value
        assert not ds.get((0x0008, 0x0094), Empty()).value
        assert not ds.get((0x0010, 0x2152), Empty()).value
        assert not ds.get((0x0040, 0x1400), Empty()).value
        assert not ds.get((0x0032, 0x1032), Empty()).value
        assert not ds.get((0x0032, 0x1031), Empty()).value
        assert not ds.get((0x0010, 0x2299), Empty()).value
        assert not ds.get((0x0010, 0x2297), Empty()).value
        assert not ds.get((0x0010, 0x2298), Empty()).value
        assert not ds.get((0x0040, 0x000b), Empty()).value
        assert not ds.get((0x0040, 0x0006), Empty()).value
        assert not ds.get((0x0010, 0x21a0), Empty()).value
        assert not ds.get((0x0038, 0x0050), Empty()).value
        assert ds.get((0x0008, 0x0012)).value == '19900101'
        assert ds.get((0x0008, 0x0020)).value == '19900101'
        assert ds.get((0x0008, 0x0021)).value == '19900101'
        assert ds.get((0x0008, 0x0022)).value == '19900101'
        assert ds.get((0x0008, 0x0023)).value == '19900101'
        assert ds.get((0x0040, 0x0244)).value == '19900101'
        assert not ds.get((0x0002, 0x0003), Empty()).value
        assert str(ds.get((0x0008, 0x0018)).value).startswith('1.2.826.0.1.3680043.8.498')
        assert str(ds.get((0x0020, 0x000d)).value).startswith('1.2.826.0.1.3680043.8.498')
        assert str(ds.get((0x0020, 0x000e)).value).startswith('1.2.826.0.1.3680043.8.498')
        assert str(ds.get((0x0020, 0x0052)).value).startswith('1.2.826.0.1.3680043.8.498')
        assert ds.get((0x0040, 0x0253)).value == '19900101'
        assert ds.get((0x0029, 0x1009)).value == '19900101'
        assert ds.get((0x0029, 0x1019)).value == '19900101'
        assert not ds.get((0x0012, 0x0063), Empty()).value
        for item in ds.RequestAttributesSequence:
            assert not item.get((0x0040, 0x1001), Empty()).value

