import os

SOURCE_METER_DIR_NAME = "SourceMeter-8.2.0-x64-linux"

FOLDER = os.path.dirname(os.path.abspath(__file__))
SOURCE_METER_JAVA_PATH = os.path.join(FOLDER, "..", SOURCE_METER_DIR_NAME, "Java", "SourceMeterJava")
SOURCE_METER_PYTHON_PATH = os.path.join(FOLDER, "..", SOURCE_METER_DIR_NAME, "Python", "SourceMeterPython")

CLASS_KEEP_COL = ['Name', 'LOC', 'CD', 'CBO', 'NOI']
METHOD_KEEP_COL = ['Name', 'Path', 'LOC', 'NUMPAR', 'CD']

CLEAN_UP_SM_FILES = True                     # Delete Source Meter-created metrics after script execution?
CLEAN_UP_REPO_FILES = True                   # Delete GitHub repo files that are cloned by sourceMeterWrapper.py?

TMP_DIR = os.path.join(FOLDER, "..", 'tmp')  # The temp directory where projects can be cloned.
