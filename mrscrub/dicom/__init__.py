class Tags:
    CSA = {
        (0x0029, 0x1020): 'CSASeriesHeaderInfo',
        (0x0029, 0x1010): 'CSAImageHeaderInfo'
    }

    STUDY_UIDS = {
         (0x0020, 0x000d): 'StudyInstanceUID'
    }

    SERIES_UIDS = {
        (0x0020, 0x000e): 'SeriesInstanceUID',
        (0x0020, 0x0052): 'FrameOfReferenceUID'
    }

    INSTANCE_UIDS = {
        (0x0008, 0x0018): 'SOPInstanceUID',
        (0x0002, 0x0003): 'MediaStorageSOPInstanceUID'
    }

    ALL_UIDS = {
        **STUDY_UIDS,
        **SERIES_UIDS,
        **INSTANCE_UIDS
    }

tags = Tags()
