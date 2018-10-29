import fnmatch
import os
import shlex
import shutil
from subprocess import Popen
from pandas import read_csv, concat
from constants import RESULTS_DIR, SOURCE_METER_JAVA_PATH, SOURCE_METER_PYTHON_PATH, JAVA_SAMPLE_PROJ_DIR, \
    PYTHON_SAMPLE_PROJ_DIR, CLASS_KEEP_COL, METHOD_KEEP_COL, POSIX, DIR_SEPARATOR

clean_up_sm_files = True                    # Delete Source Meter-created metrics after script execution?
testing_java = False                        # Test Java project? If 'False', will test Python project
testing_python = not testing_java


def exec_metric_analysis(project_dir, project_name, project_type):
    run_cmd = [SOURCE_METER_PYTHON_PATH,
               "-projectBaseDir:" + project_dir,
               "-projectName:" + project_name,
               "-resultsDir:" + RESULTS_DIR,
               "-runMetricHunter:false",
               "-runFaultHunter:false",
               "-runDCF:false",
               "-runMET:true",
               "-runPylint:false"
               ] if project_type == "python" else \
        [SOURCE_METER_JAVA_PATH,
         "-projectBaseDir=" + project_dir,
         "-projectName=" + project_name,
         "-resultsDir=" + RESULTS_DIR,
         "-runAndroidHunter=false"
         "-runMetricHunter=false",
         "-runFaultHunter=false",
         "-runVulnerabilityHunter=false",
         "-runRTEHunter=false",
         "-runDCF=false",
         "-runMET=true",
         "-runFB=false",
         "-runPMD=true"
         ]
    Popen(run_cmd).wait() if POSIX else Popen(shlex.split(run_cmd, posix=POSIX)).wait()


def consolidate_metrics(project_name):
    # Consolidate Source Meter Metrics
    sc_results_dir = os.path.join(RESULTS_DIR, project_name, "java" if testing_java else "python")
    latest_results_path = os.path.join(sc_results_dir, os.listdir(sc_results_dir)[0])
    class_file = os.path.join(latest_results_path, project_name + "-Class.csv")
    methods_file = os.path.join(latest_results_path, project_name + "-Method.csv")

    # Read class-level metrics and keep only certain columns
    tmp_f = read_csv(class_file)[CLASS_KEEP_COL]
    # Insert 'Level' column
    tmp_f.insert(0, 'Type of Smell', 'Class')
    # Insert Method-Level Columns and set value to '-'
    curr_column = len(CLASS_KEEP_COL) + 1
    for metric in set(METHOD_KEEP_COL) - set(CLASS_KEEP_COL):
        tmp_f.insert(curr_column, metric, '-')
        curr_column += 1
    class_portion = tmp_f

    # Read method-level metrics, keep only certain columns, and rename 'Path' column to 'Class'
    tmp_f = read_csv(methods_file)[METHOD_KEEP_COL]
    # Make every row in column 'Class' contain only the last token (class name) when splitting with DIR_SEPARATOR
    tmp_f['Path'] = tmp_f['Path']\
        .apply(lambda x: str(x)).apply(lambda x: x.split(DIR_SEPARATOR)[len(x.split(DIR_SEPARATOR)) - 1])
    # Insert 'Level' column
    tmp_f.insert(0, 'Type of Smell', 'Method')
    # Insert Class-Level Columns and set value to '-'
    curr_column = len(METHOD_KEEP_COL) + 1
    for metric in set(CLASS_KEEP_COL) - set(METHOD_KEEP_COL):
        tmp_f.insert(curr_column, metric, '-')
        curr_column += 1
    method_portion = tmp_f

    result = concat([class_portion, method_portion], sort=False)
    result = result.rename(columns={'LOC': 'Lines of Code',
                                    'CD': 'Comment-to-Code Ratio',
                                    'CBO': 'Number of Directly-Used Elements',
                                    'NOI': 'Number of Outgoing Invocations',
                                    'Path': 'Name of Owner Class',
                                    'NUMPAR': 'Number of Parameters'
                                    })
    result.to_csv(os.path.join(RESULTS_DIR, project_name, "metrics.csv"), index=False)

    # Clean up excess Source Meter files
    if clean_up_sm_files:
        clear_dir(sc_results_dir)


def clear_dir(directory):
    shutil.rmtree(directory)


def get_project_name(directory):
    proj_name_tokens = directory.split(DIR_SEPARATOR)
    return proj_name_tokens[len(proj_name_tokens) - 1]


def get_project_type(directory):
    java_files = [os.path.join(dirpath, f)
                  for dirpath, dirnames, files in os.walk(directory) for f in fnmatch.filter(files, '*.java')]
    python_files = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(directory) for f in fnmatch.filter(files, '*.py')]
    return "java" if len(java_files) and len(java_files) > len(python_files) else "python"


if __name__ == "__main__":
    proj_dir = JAVA_SAMPLE_PROJ_DIR if testing_java else PYTHON_SAMPLE_PROJ_DIR

    proj_name = get_project_name(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, get_project_type(proj_dir))
    consolidate_metrics(proj_name)
