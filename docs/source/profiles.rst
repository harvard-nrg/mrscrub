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
          - hex group code
          - hex element code
          action:
            action-name: value

Here's a quick overview of what we're looking at

* ``dicom``
    * ``fields``: a list of fields to de-identify
        * ``name``: a name for the field (your choice)
        * ``tag``: a DICOM tag (2 hex values)
        * ``action``
            * ``action-name``: the  `action <#actions>`_ you want to apply

Actions
-------
There are several ``actions`` you can apply to any DICOM field.

replace-with
^^^^^^^^^^^^
If you want your de-identification policy to replace ``PatientName`` 
``(0010,0010)`` with a new string (or an empty string ``''``), you can use the 
``replace-with`` action ::

    dicom:
      fields:
        - name: PatientName
          tag:
          - 0x0010
          - 0x0010
          action:
            replace-with: 'a new string'

By default, no action is performed if the targeted DICOM tag doesn't exist. 
However, if you'd like to create the missing tag before assignining the 
replacement value, you can add ``create: true`` ::

    dicom:
      fields:
        - name: PatientName
          tag:
          - 0x0010
          - 0x0010
          action:
            replace-with: 'a new string'
            create: true

new-uid
^^^^^^^
Removing dates is doable using ``replace-with``, but UIDs within a DICOM data 
set can also contain dates. To reassign ``SOPInstanceUID`` ``(0008,0018)`` for 
example, you can use the ``new-uid`` action ::

    dicom:
      fields
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
Sometimes you may want to delete a field entirely. For example, to delete the 
Siemens CSA header ``(0029,1020)``, you can use the ``delete`` action ::

    dicom:
      fields
        - name: Unknown
          tag:
          - 0x0029
          - 0x1020
          action:
            delete: true

Templating
----------
``scrub.py`` can find and replace template strings within your 
de-identification profile before the profile is applied to your data set.

.. note::
   Template strings must be surrounded by curly braces ``{...}``

Let's assume you want to add the text ``Project:MyProjectName`` to the 
``PatientComments`` ``(0010,4000)`` field for every DICOM file in your data 
set. However, you know beforehand that different data sets may need different 
project names. You could maintain a separate copy of your de-identification 
profile for each project name, or use template strings ::

    dicom:
      fields
        - name: StudyComments
            tag:
            - 0x0010
            - 0x4000
            action:
                replace-with: Project:{project}

If your de-identification profile contains template strings, you can use 
``scrub.py --replace`` to replace those strings with a custom value ::

    scrub.py --replace project=MyProjectName

You can use any number of template strings within your de-identification 
profile and provide the corresponding key/value pair to ``--replace``, each 
one separated by a single space ::

    scub.py --replace key1=value1 key2=value2 key3=value3

Example
-------
You can find an example de-identification profile 
`here <https://github.com/harvard-nrg/mrscrub/blob/main/mrscrub/configs/SSBC_v1.0.yaml>`_.
