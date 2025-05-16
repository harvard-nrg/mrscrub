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
import argparse as ap
import mrscrub.dicom
import mrscrub.configs
from pathlib import Path
from mrscrub.scanner import Scanner
from pydicom.uid import generate_uid
from pydicom.tag import Tag
from pydicom.datadict import dictionary_VR

logger = logging.getLogger(os.path.basename(__file__))

def main():
    parser = ap.ArgumentParser()
    parser.register('action', 'version', VersionAction)
    parser.add_argument('-i', '--input', type=Path, required=True)
    parser.add_argument('-o', '--output', type=Path, default='deidentified')
    parser.add_argument('-c', '--config', type=Path, required=True)
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--version', nargs=0, action='version')
    args = parser.parse_args()

    tic = time.time()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    # search for configuration file
    confdir = Path(mrscrub.configs.__file__).parent
    search = [
        args.config,
        Path(confdir, args.config),
        Path(confdir, f'{args.config}.yaml'),
    ]
    for path in search:
        if path.exists():
            args.config = path
            break
    if not args.config.exists():
        logger.critical(f'could not find configuration file {args.config}')
        sys.exit(1)
    logger.info(f'loading configuration file {args.config}')
    with open(args.config, 'r') as fo:
        content = fo.read()
    config = yaml.load(content, Loader=yaml.FullLoader)

    # scan input directory
    args.output.mkdir(parents=True, exist_ok=True)
    logger.info(f'scanning input directory {args.input} ...')
    scanner = Scanner(args.input)
    scanner.scan(recursive=args.recursive)

    # check if user asked to rewrite SOP Instance UIDs
    rewrite_instance_uids = False
    for field in config['dicom']['fields']:
        if field['name'] == 'SOPInstanceUID':
            rewrite_instance_uids = True
            break

    # start crawling over files
    logger.info('de-identifying files now')
    instance_uids_map = dict()
    for _,study in iter(scanner.studies.items()):
        new_media_uid = generate_uid() # MediaSOPInstanceUID
        new_study_uid = generate_uid() # StudyInstanceUID
        for _,series in iter(study.series.items()):
            new_series_uid = generate_uid() # SeriesInstanceUID
            new_frame_uid = generate_uid() # FrameOfReferenceUID
            for instance_uid,instance in iter(series.instances.items()):
                ds = pydicom.dcmread(instance.path)
                # update referenced SOP Instance UIDs
                if rewrite_instance_uids:
                    if instance_uid not in instance_uids_map:
                        instance_uids_map[instance_uid] = generate_uid()
                    update_referenced_uids(ds, instance_uids_map)
                for field in config['dicom']['fields']:
                    name = field['name']
                    tag = tuple(field['tag'])
                    action = field['action']
                    create = field['action'].get('create', False)
                    if 'new-uid' in action:
                        if name == 'StudyInstanceUID' and tag in ds:
                            ds[tag].value = new_study_uid
                        elif name == 'SeriesInstanceUID' and tag in ds:
                            ds[tag].value = new_series_uid
                        elif name == 'SOPInstanceUID' and tag in ds:
                            ds[tag].value = instance_uids_map[instance_uid]
                        elif name == 'MediaStorageSOPInstanceUID' and tag in ds.file_meta:
                            ds.file_meta[tag].value = new_media_uid
                        elif name == 'FrameOfReferenceUID' and tag in ds:
                            ds[tag].value = new_frame_uid
                    elif 'replace-with' in action:
                        replacement = action['replace-with']
                        if name == 'RequestedProcedureID':
                            for item in ds.get('RequestAttributesSequence', list()):
                                if tag in item:
                                    item[tag].value = replacement
                        if tag in ds:
                            ds[tag].value = replacement
                        elif create:
                            ds.add_new(tag, dictionary_VR(tag), replacement)
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
    toc = time.time() - tic
    logger.info(f'finished in {toc} secs')

def update_referenced_uids(ds, instance_uids_map, update_csa=True):
    for item in ds.get('SourceImageSequence', list()):
        ref_sop_instance_uid = item.ReferencedSOPInstanceUID
        if ref_sop_instance_uid not in instance_uids_map:
            instance_uids_map[ref_sop_instance_uid] = generate_uid()
        item.ReferencedSOPInstanceUID = instance_uids_map[ref_sop_instance_uid]

    for item in ds.get('ReferencedImageSequence', list()):
        ref_sop_instance_uid = item.ReferencedSOPInstanceUID
        if ref_sop_instance_uid not in instance_uids_map:
            instance_uids_map[ref_sop_instance_uid] = generate_uid()
        item.ReferencedSOPInstanceUID = instance_uids_map[ref_sop_instance_uid]

    if update_csa:
        try:
            parsed = mrscrub.dicom.parse_csa(ds)
        except mrscrub.dicom.NoCSAHeaderError as e:
            logger.debug(e)
            return
        except mrscrub.dicom.NoASCCONVError as e:
            logger.warning(e)
            return

        for key,value in iter(parsed.items()):
            if not key.startswith('tReferenceImage'):
                continue
            ref_sop_instance_uid = value
            if ref_sop_instance_uid not in instance_uids_map:
                instance_uids_map[ref_sop_instance_uid] = generate_uid()
            ds[mrscrub.dicom.SiemensCSA].value = re.sub(
                ref_sop_instance_uid.encode(),
                instance_uids_map[ref_sop_instance_uid].encode(),
                ds[mrscrub.dicom.SiemensCSA].value
            )

class VersionAction(ap.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(mrscrub.version())
        parser.exit()

if __name__ == '__main__':
    main()

