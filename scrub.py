#!/Users/tokeefe/venv/bin/python

import os
import time
import json
import yaml
import logging
import pydicom
import mrscrub
import tempfile
import argparse as ap
import mrscrub.configs
from mrscrub.scanner import Scanner
from pydicom.uid import generate_uid
from pydicom.tag import Tag
from pydicom.datadict import dictionary_VR

logger = logging.getLogger(os.path.basename(__file__))

def main():
    parser = ap.ArgumentParser()
    parser.register('action', 'version', VersionAction)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', default='deidentified')
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('-r', '--replace', nargs='*', action=ParseReplace)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--version', nargs=0, action='version')
    args = parser.parse_args()

    tic = time.time()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    args.input = os.path.expanduser(args.input)
    args.output = os.path.expanduser(args.output)

    # read and render config profile (look for config within package first)
    confdir = os.path.dirname(mrscrub.configs.__file__)
    conf = os.path.join(confdir, '{0}.yaml'.format(args.config))
    if os.path.exists(conf):
        args.config = conf
    logger.info('loading config %s', args.config)
    with open(os.path.expanduser(args.config), 'r') as fo:
        content = fo.read()
    if args.replace:
        content = content.format_map(SafeDict(args.replace))
    config = yaml.load(content, Loader=yaml.FullLoader)

    # scan input directory
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    logger.info('scanning input directory %s ...', args.input)
    scanner = Scanner(args.input)
    scanner.scan()

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
                ds = pydicom.dcmread(instance.filename)
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
                            ds.file_meta[tag].value = new_msi_uid
                        elif name == 'FrameOfReferenceUID' and tag in ds:
                            ds[tag].value = new_for_uid
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
                handle,fullfile = tempfile.mkstemp(prefix=prefix, dir=args.output, suffix='.dcm')
                os.close(handle)
                basename = os.path.basename(fullfile)
                saveas = os.path.join(args.output, basename)
                logger.debug(f'saving {saveas}')
                ds.save_as(saveas)
    # done
    toc = time.time() - tic
    logger.info(f'finished in {toc} secs')

def update_referenced_uids(ds, instance_uids_map):
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

class VersionAction(ap.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(mrscrub.version())
        parser.exit()

class ParseReplace(ap.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            try:
                k,v = value.split('=')
            except ValueError as e:
                logger.warning('problem parsing --replace value %s', value)
                pass
            getattr(namespace, self.dest)[k] = v

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

if __name__ == '__main__':
    main()

