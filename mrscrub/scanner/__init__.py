import os
import re
import logging
import pydicom
import mrscrub.dicom
from pathlib import Path
from collections import defaultdict
from pydicom.uid import generate_uid

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, path):
        self.path = path
        self.studies = dict()
        self.num_dicoms = 0
        self.uid_mapping = UIDMap()

    def scan(self, recursive=False):
        for path in self.walk(recursive):
            try:
                ds = pydicom.dcmread(path)
            except IsADirectoryError as e:
                logger.debug(f'not a dicom file {path.name}')
            except pydicom.errors.InvalidDicomError as e:
                logger.debug(f'not a dicom file {path.name}')
            # maintain mapping of uids to randomly generated uids
            self.uid_mapping.add(ds)
            # track study
            studyuid = ds.StudyInstanceUID
            if studyuid not in self.studies:
                self.studies[studyuid] = Study(studyuid)
            study = self.studies[studyuid]
            # track series
            seriesuid = ds.SeriesInstanceUID
            seriesnumber = int(ds.SeriesNumber)
            if seriesuid not in study.series:
                series = Series(seriesuid, seriesnumber)
                study.add(series)
            series = study.series[seriesuid]
            # track instance
            instanceuid = ds.SOPInstanceUID
            instancenumber = ds.InstanceNumber
            if instanceuid not in series.instances:
                instance = Instance(instanceuid, instancenumber, path)
                series.add(instance)
                self.num_dicoms += 1

    def walk(self, recursive=False):
        if recursive:
            for root, dirs, files in self.path.walk():
                for path in files:
                    yield Path(root, path)
        else:
            for path in self.path.iterdir():
                if path.is_file():
                    yield path

class UIDMap(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instances = defaultdict(dict)

    def add(self, ds):
        series_number = ds.SeriesNumber
        instance_number = ds.InstanceNumber
        if series_number not in self:
            self[series_number] = dict()
        for tag in mrscrub.dicom.tags.ALL_UIDS:
            if tag in ds:
                uid = ds[tag].value
                self[series_number].setdefault(uid, ScrubbedUID(uid))
            if tag in ds.file_meta:
                uid = ds.file_meta[tag].value
                self[series_number].setdefault(uid, ScrubbedUID(uid))

        # used for an optimization trick
        if not instance_number in self._instances[series_number]:
            self._instances[series_number][instance_number] = list()
        for tag in mrscrub.dicom.tags.INSTANCE_UIDS:
            if tag in ds:
                uid = ds[tag].value
                self._instances[series_number][instance_number].append(uid)
            if tag in ds.file_meta:
                uid = ds.file_meta[tag].value
                self._instances[series_number][instance_number].append(uid)

    def get_future_uids(self, series, start):
        result = list()
        for instance_number, uids in iter(self._instances[series].items()):
            if instance_number > start:
                result += uids
        return result

class ScrubbedUID:
    def __init__(self, uid):
        self.uid = uid
        self.generated = generate_uid()
        self.pattern = re.compile(uid.encode('ascii'))

class Study:
    def __init__(self, uid):
        self.uid = uid
        self.series = dict()

    def add(self, series):
        self.series[series.uid] = series

class Series:
    def __init__(self, uid, number):
        self.uid = uid
        self.number = number
        self.instances = dict()

    def add(self, instance):
        uid = instance.uid
        self.instances[uid] = instance

class Instance:
    def __init__(self, uid, number, path):
        self.uid = uid
        self.number = number
        self.path = path

