import os
import pydicom
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, path):
        self.path = path
        self.studies = dict()

    def scan(self, recursive=False):
        for path in self.walk(recursive):
            try:
                dcm = pydicom.dcmread(path)
            except IsADirectoryError as e:
                logger.debug(f'not a dicom file {path.name}')
            except pydicom.errors.InvalidDicomError as e:
                logger.debug(f'not a dicom file {path.name}')
            # track study
            studyuid = dcm.StudyInstanceUID
            if studyuid not in self.studies:
                self.studies[studyuid] = Study(studyuid)
            study = self.studies[studyuid]
            # track series
            seriesuid = dcm.SeriesInstanceUID
            seriesnumber = int(dcm.SeriesNumber)
            if seriesuid not in study.series:
                series = Series(seriesuid, seriesnumber)
                study.add(series)
            series = study.series[seriesuid]
            # track instance
            instanceuid = dcm.SOPInstanceUID
            instancenumber = dcm.InstanceNumber
            if instanceuid not in series.instances:
                instance = Instance(instanceuid, path)
                series.add(instance)

    def walk(self, recursive=False):
        if recursive:
            for root, dirs, files in self.path.walk():
                for path in files:
                    yield Path(root, path)
        else:
            for path in self.path.iterdir():
                if path.is_file():
                    yield path

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
    def __init__(self, uid, path):
        self.uid = uid
        self.path = path
        
