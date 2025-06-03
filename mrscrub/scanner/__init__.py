import os
import re
import logging
import pydicom
import mrscrub.dicom
from pathlib import Path
from pydicom.uid import generate_uid

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, path):
        self.path = path
        self.studies = dict()
        self.num_dicoms = 0
        self.uid_mapping = None

    def scan(self, recursive=False):
        for path in self.walk(recursive):
            try:
                ds = pydicom.dcmread(path)
            except IsADirectoryError as e:
                logger.debug(f'not a dicom file {path.name}')
            except pydicom.errors.InvalidDicomError as e:
                logger.debug(f'not a dicom file {path.name}')
            # maintain mapping of uids to randomly generated uids
            if not self.uid_mapping:
                self.uid_mapping = UIDMap(ds.StudyInstanceUID)
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
    def __init__(self, study_instance_uid):
        self._study = ScrubbedUID(study_instance_uid)

    def add(self, ds):
        series_number = ds.SeriesNumber
        if series_number not in self:
            # this uid must remain constant across the study
            self[series_number] = {
                self._study.uid: self._study
            }
        for tag in mrscrub.dicom.tags.ALL_UIDS:
            if tag in ds:
                uid = ds[tag].value
                self[series_number].setdefault(uid, ScrubbedUID(uid))
            if tag in ds.file_meta:
                uid = ds.file_meta[tag].value
                self[series_number].setdefault(uid, ScrubbedUID(uid))

class ScrubbedUID:
    def __init__(self, uid):
        self.uid = uid
        self.generated = generate_uid()

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

