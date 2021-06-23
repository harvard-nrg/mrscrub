#!/Users/tokeefe/venv/bin/python

import os
import time
import yaml
import logging
import pydicom
import argparse as ap
import mrscrub.configs
from mrscrub.scanner import Scanner
from pydicom.uid import generate_uid

logger = logging.getLogger(os.path.basename(__file__))

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', default='deidentified')
    parser.add_argument('-c', '--config', default='deidentified')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    tic = time.time()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG    
    logging.basicConfig(level=level)

    args.input = os.path.expanduser(args.input)
    args.output = os.path.expanduser(args.output)

    # scan input directory
    if not os.path.exists(args.output):
        os.makedirs(args.output)    
    logger.info('scanning input directory %s ...', args.input)
    scanner = Scanner(args.input)
    scanner.scan()

    # load config (look for config within package first)
    confdir = os.path.dirname(mrscrub.configs.__file__)
    conf = os.path.join(confdir, '{0}.yaml'.format(args.config))
    if os.path.exists(conf):
        args.config = conf
    logger.info('loading config %s', args.config)
    with open(os.path.expanduser(args.config), 'r') as fo:
        config = yaml.load(fo, Loader=yaml.FullLoader)

    # check if rewriting SOP Instance UIDs
    rewrite_instance_uids = False
    for field in config['dicom']['fields']:
        if field['name'] == 'SOPInstanceUID':
            rewrite_instance_uids = True

    # start crawling over files
    logger.info('de-identifying...')
    instance_uids_map = dict()
    for _,study in iter(scanner.studies.items()):
        new_msi_uid = generate_uid() # MediaSOPInstanceUID
        new_study_uid = generate_uid() # StudyInstanceUID
        for _,series in iter(study.series.items()):
            new_series_uid = generate_uid() # SeriesInstanceUID
            new_for_uid = generate_uid() # FrameOfReferenceUID
            for instance_uid,instance in iter(series.instances.items()):
                ds = pydicom.read_file(instance.filename)
                # update referenced SOP Instance UIDs
                if rewrite_instance_uids:
                    if instance_uid not in instance_uids_map:
                        instance_uids_map[instance_uid] = generate_uid()
                    update_referenced_uids(ds, instance_uids_map)
                for field in config['dicom']['fields']:
                    name = field['name']
                    tag = tuple(field['tag'])
                    action = field['action']
                    # move along if tag does not exist
                    if tag not in ds and tag not in ds.file_meta:
                        continue
                    # process actions
                    if 'new-uid' in action:
                        if name == 'StudyInstanceUID':
                            ds[tag].value = new_study_uid
                        elif name == 'SeriesInstanceUID':
                            ds[tag].value = new_series_uid
                        elif name == 'SOPInstanceUID':
                            ds[tag].value = instance_uids_map[instance_uid]
                        elif name == 'MediaStorageSOPInstanceUID':
                            ds.file_meta[tag].value = new_msi_uid
                        elif name == 'FrameOfReferenceUID':
                            ds[tag].value = new_for_uid
                    elif 'replace-with' in action:
                        replacement = action['replace-with']
                        ds[tag].value = replacement
                    elif 'delete' in action:
                        del ds[tag]
                # save scrubbed file
                basename = os.path.basename(instance.filename)
                saveas = os.path.join(args.output, basename)
                logger.debug(f'saving {saveas}')
                ds.save_as(saveas)
    # done
    toc = time.time() - tic
    logger.info(f'finished in {toc} secs')

def update_referenced_uids(ds, instance_uids_map):
    if 'SourceImageSequence' in ds:
        for item in ds.SourceImageSequence:
            ref_sop_instance_uid = item.ReferencedSOPInstanceUID
            if ref_sop_instance_uid not in instance_uids_map:
                instance_uids_map[ref_sop_instance_uid] = generate_uid()
            item.ReferencedSOPInstanceUID = instance_uids_map[ref_sop_instance_uid]
    if 'ReferencedImageSequence' in ds:
        for item in ds.ReferencedImageSequence:
            ref_sop_instance_uid = item.ReferencedSOPInstanceUID
            if ref_sop_instance_uid not in instance_uids_map:
                instance_uids_map[ref_sop_instance_uid] = generate_uid()
            item.ReferencedSOPInstanceUID = instance_uids_map[ref_sop_instance_uid]

if __name__ == '__main__':
    main()

