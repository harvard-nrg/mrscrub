import re

SiemensCSA = (0x0029, 0x1020)

def parse_csa(ds):
    result = dict()
    if SiemensCSA not in ds:
        header = ', '.join(f'0x{val:04x}' for val in SiemensCSA)
        raise NoCSAHeaderError(f'could not find ({header}) in {ds.SOPInstanceUID}')
    bytearr = ds[SiemensCSA].value
    value = bytearr.decode(errors='ignore')
    match = re.search(r'### ASCCONV BEGIN.*?###(.*)### ASCCONV END ###', value, re.DOTALL)
    if not match:
      raise NoASCCONVError('could not find ASCCONV section in {ds.SOPInstanceUID}')
    ascconv = match.group(1).strip()
    for line in ascconv.split('\n'):
        match = re.match(r'(.*?)\s+=\s+(.*)', line)
        key,value = match.groups()
        result[key] = value.strip('"')
    return result

class NoCSAHeaderError(Exception):
    pass

class NoASCCONVError(Exception):
    pass
