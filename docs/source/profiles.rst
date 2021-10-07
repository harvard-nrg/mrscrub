De-idenfication Profiles
========================
De-identification profiles define which fields ``mrscrub`` should modify and how. These profiles 
should be written in `YAML <https://yaml.org/>`_.

Overview
--------
The general structure of a de-identification profile is ::

    dicom:
      fields:
        - name: FieldName
          tag:
          - group code (hex)
          - element code (hex)
          action:
            action-name: value

Here's a quick overview of what we're looking at

* ``dicom``
    * ``fields``: a list of fields to de-identify
        * ``name``: a name for the field (you decide)
        * ``tag``: a DICOM tag (2 hex values)
        * ``action``
            * ``action-name``: the  `action <#actions>`_ you want to apply

Actions
-------
There are several *actions* you can apply to a DICOM field. These are best explained 
with an example.

replace-with
^^^^^^^^^^^^
If you want your de-identification policy to replace ``PatientName`` 
``(0010,0010)`` with an empty string, you would use the ``replace-with`` 
action ::

    dicom:
        fields:
          - name: PatientName
            tag:
            - 0x0010
            - 0x0010
            action:
                replace-with: ''

new-uid
^^^^^^^
Removing dates is doable with ``replace-with`` for some DICOM fields, but UIDs 
can also contain dates. To reassign ``SOPInstanceUID`` ``(0008,0018)`` for 
example, you would use the ``new-uid`` action ::

    dicom:
      fields
        - name: PatientName
            tag:
            - 0x0010
            - 0x0010
            action:
                replace-with: ''
        - name: SOPInstanceUID
          tag:
          - 0x0008
          - 0x0018
          action:
            new-uid: true

.. note::
   Note that replacing ``SOPInstanceUID`` will also trigger the replacement of 
   any ``ReferencedSOPInstanceUID`` instances within ``SourceImageSequence`` or 
   ``ReferencedImageSequence``.

delete
^^^^^^
Sometimes you may want to delete a field entirely. For example, if you wanted 
to delete the Siemens CSA header ``(0029,1020)`` you would use the ``delete`` 
action ::

    dicom:
      fields
        - name: PatientName
            tag:
            - 0x0010
            - 0x0010
            action:
                replace-with: ''
        - name: SOPInstanceUID
          tag:
          - 0x0008
          - 0x0018
          action:
            new-uid: true
        - name: Unknown
          tag:
          - 0x0029
          - 0x1020
          action:
            delete: true

Templating
----------
``mrscrub`` includes the ability to find and replace template strings within 
your de-identification profile before the profile is applied to your data set. 
This functionality is best illustrated with an example.

Suppose you wanted to add custom text ``Project:ProjectName`` to the Study 
Comments field ``(0010,4000)`` for every DICOM file in your data set. However, 
you know ahead of time that each data will need a different ``ProjectName``. 
You could maintain a separate copy of your de-identification profile for each 
``ProjectName``, or use template strings ::

    dicom:
      fields
        - name: StudyComments
            tag:
            - 0x0010
            - 0x4000
            action:
                replace-with: Project:{project}

If your de-identification profile contains template strings, you can use the 
``scrub.py --replace`` argument to replace those strings with a custom 
value ::

    scrub.py --replace project=MyProjectName

You can use any number of template strings within your de-identification profile 
and provide the corresponding key/value pair to ``--replace``, each one 
separated by a single space ::

    scub.py --replace key1=value1 key2=value2 key3=value3

Example
-------
You can find an example de-identification profile 
`here <https://github.com/harvard-nrg/mrscrub/blob/main/mrscrub/configs/SSBC_v1.0.yaml>`_.
