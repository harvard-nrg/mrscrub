import os
import pydicom
import logging

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, indir, sort=True):
        self.indir = os.path.expanduser(indir)
        self.studies = dict()

    def scan(self, sort=True):
        for f in os.listdir(self.indir):
            fullfile = os.path.join(self.indir, f)
            try:
                dcm = pydicom.read_file(fullfile)
            except pydicom.errors.InvalidDicomError as e:
                logger.debug('not dicom %s', f)
            # study
            studyuid = dcm.StudyInstanceUID
            if studyuid not in self.studies:
                self.studies[studyuid] = Study(studyuid)
            study = self.studies[studyuid]
            # series
            seriesuid = dcm.SeriesInstanceUID
            seriesnumber = int(dcm.SeriesNumber)
            if seriesuid not in study.series:
                series = Series(seriesuid, seriesnumber)
                study.add(series)
            series = study.series[seriesuid]
            # instance
            instanceuid = dcm.SOPInstanceUID
            instancenumber = dcm.InstanceNumber
            if instanceuid not in series.instances:
                instance = Instance(instanceuid, fullfile)
                series.add(instance)

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
    def __init__(self, uid, filename):
        self.uid = uid
        self.filename = filename
        
