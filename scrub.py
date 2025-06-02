#!/usr/bin/env python3

import os
import re
import sys
import time
import json
import yaml
import logging
import pydicom
import mrscrub
import tempfile
import mrscrub.dicom
from tqdm import tqdm
import argparse as ap
import mrscrub.configs
from pathlib import Path
from mrscrub.scanner import Scanner
from mrscrub.scanner import ScrubbedUID
from pydicom.datadict import dictionary_VR

logger = logging.getLogger(os.path.basename(__file__))

def main():
    parser = ap.ArgumentParser()
    parser.register('action', 'version', VersionAction)
    parser.add_argument('-i', '--input', type=Path, required=True)
    parser.add_argument('-o', '--output', type=Path, default='deidentified')
    parser.add_argument('-c', '--config', type=Path, default='PBN_v2.0')
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.add_argument('--scrub-csa-headers', action='store_true')
    parser.add_argument('--version', nargs=0, action='version')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    tic = time.time()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    # search for and load configuration file
    config = load_config_file(args.config)

    # scan input directory
    args.output.mkdir(parents=True, exist_ok=True)
    logger.info(f'scanning input directory {args.input} ...')
    scanner = Scanner(args.input)
    scanner.scan(recursive=args.recursive)

    rewrite_uids = True
    num_instances = 0

    # start crawling over files
    logger.info(f'de-identifying {scanner.num_dicoms} dicom files')
    pbar = tqdm(total=scanner.num_dicoms)
    for _,study in iter(scanner.studies.items()):
        for _,series in iter(study.series.items()):
            for _,instance in iter(series.instances.items()):
                num_instances += 1
                pbar.update(1)
                ds = pydicom.dcmread(instance.path)
                # update uids
                if rewrite_uids:
                    mapping = scanner.uid_mapping[series.number]
                    update_uids(ds, mapping)
                    update_referenced_uids(ds, mapping)
                    if args.scrub_csa_headers:
                        if ds.SeriesDescription == 'PhoenixZIPReport':
                            for mapping in scanner.uid_mapping.values():
                                update_csa_headers(ds, mapping)
                        else:
                            update_csa_headers(ds, mapping)
                for field in config['dicom']['fields']:
                    name = field['name']
                    tag = tuple(field['tag'])
                    if 'action' not in field:
                        continue
                    action = field['action']
                    create = field['action'].get('create', False)
                    if 'replace-with' in action:
                        replacement = action['replace-with']
                        if name == 'RequestedProcedureID':
                            for item in ds.get('RequestAttributesSequence', list()):
                                if tag in item:
                                    item[tag].value = replacement
                        if tag in ds:
                            ds[tag].value = replacement
                        elif create:
                            ds.add_new(tag, dictionary_VR(tag), replacement)
                    elif 'replace-sub' in action:
                        pattern = action['replace-sub']['pattern']
                        replace_with = action['replace-sub']['replace-with']
                        if tag in ds:
                            original = ds[tag].value
                            if tag in mrscrub.dicom.tags.CSA:
                                pattern = pattern.encode('ascii')
                                replace_with = replace_with.encode('ascii')
                            replace = re.sub(
                                pattern,
                                replace_with,
                                original).strip()
                            ds[tag].value = replace
                        elif create:
                            ds.add_new(tag, dictionary_VR(tag), replace_with)
                    elif 'delete' in action:
                        if name == 'RequestedProcedureID':
                            for item in ds.get('RequestAttributesSequence', list()):
                                if tag in item:
                                    del item[tag]
                        if tag in ds:
                            del ds[tag]

                # save scrubbed file to deidentified file name
                study_uid = ds['StudyInstanceUID'].value
                series_number = ds['SeriesNumber'].value
                instance_number = ds['InstanceNumber'].value
                prefix = f'{study_uid}-{series_number}-{instance_number}-'
                handle, fullfile = tempfile.mkstemp(prefix=prefix, dir=args.output, suffix='.dcm')
                os.close(handle)
                basename = Path(fullfile).name
                saveas = Path(args.output, basename)
                logger.debug(f'saving {saveas}')
                ds.save_as(saveas)

    # done
    pbar.close()
    toc = time.time() - tic
    logger.info(f'processed {num_instances} files in {toc} secs')

def update_uids(ds, mapping):
    for tag in mrscrub.dicom.tags.ALL_UIDS:
        if tag in ds:
            uid = ds[tag].value
            mapping.setdefault(uid, ScrubbedUID(uid))
            ds[tag].value = mapping[uid].generated
        if tag in ds.file_meta:
            uid = ds.file_meta[tag].value
            ds.file_meta[tag].value = mapping[uid].generated

def update_referenced_uids(ds, mapping):
    for item in ds.get('SourceImageSequence', list()):
        uid = item.ReferencedSOPInstanceUID
        mapping.setdefault(uid, ScrubbedUID(uid))
        item.ReferencedSOPInstanceUID = mapping[uid].generated

    for item in ds.get('ReferencedImageSequence', list()):
        uid = item.ReferencedSOPInstanceUID
        mapping.setdefault(uid, ScrubbedUID(uid))
        item.ReferencedSOPInstanceUID = mapping[uid].generated

def update_csa_headers(ds, mapping, ignore=None):
    if not ignore:
        ignore = list()
    for tag in mrscrub.dicom.tags.CSA:
        if tag not in ds:
            continue
        for uid, mapped_uid in iter(mapping.items()):
            if uid in ignore:
                continue
            replace = 'X' * len(uid)
            ds[tag].value = ds[tag].value.replace(
                uid.encode('ascii'),
                replace.encode('ascii')
            )

def scrub_csa_string(ds, s):
    for tag in mrscrub.dicom.tags.CSA:
        if tag not in ds:
            continue
        replace = 'X' * len(s)
        ds[tag].value = ds[tag].value.replace(
            s.encode('ascii'),
            replace.encode('ascii')
        )

def load_config_file(name):
    config = None
    confdir = Path(mrscrub.configs.__file__).parent
    search = [
        name,
        Path(confdir, name),
        Path(confdir, f'{name}.yaml'),
    ]
    for path in search:
        if path.exists():
            config = path
            break
    if not config:
        logger.critical(f'could not find configuration file {name}')
        sys.exit(1)
    logger.info(f'loading configuration file {config}')
    with open(config, 'r') as fo:
        content = fo.read()
    return yaml.load(content, Loader=yaml.FullLoader)

class VersionAction(ap.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(mrscrub.version())
        parser.exit()

if __name__ == '__main__':
    main()

