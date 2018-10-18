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


def exec_metric_analysis():
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


def consolidate_metrics():
    # Consolidate Source Meter Metrics
    sc_results_dir = os.path.join(RESULTS_DIR, project_name, "java" if testing_java else "python")
    latest_results_path = os.path.join(sc_results_dir, os.listdir(sc_results_dir)[0])
    class_file = os.path.join(latest_results_path, project_name + "-Class.csv")
    methods_file = os.path.join(latest_results_path, project_name + "-Method.csv")

    # Read class-level metrics and keep only certain columns
    tmp_f = read_csv(class_file)[CLASS_KEEP_COL]
    # Insert 'Level' column
    tmp_f.insert(0, 'Level', 'Class')
    # Insert Method-Level Columns and set value to '-'
    curr_column = len(CLASS_KEEP_COL) + 1
    for metric in set(METHOD_KEEP_COL) - set(CLASS_KEEP_COL):
        tmp_f.insert(curr_column, metric if metric != "Path" else "Class", '-')
        curr_column += 1
    class_portion = tmp_f

    # Read method-level metrics, keep only certain columns, and rename 'Path' column to 'Class'
    tmp_f = read_csv(methods_file)[METHOD_KEEP_COL].rename(columns={'Path': 'Class'})
    # Make every row in column 'Class' contain only the last token (class name) when splitting with DIR_SEPARATOR
    tmp_f['Class'] = tmp_f['Class']\
        .apply(lambda x: str(x)).apply(lambda x: x.split(DIR_SEPARATOR)[len(x.split(DIR_SEPARATOR)) - 1])
    # Insert 'Level' column
    tmp_f.insert(0, 'Level', 'Method')
    # Insert Class-Level Columns and set value to '-'
    curr_column = len(METHOD_KEEP_COL) + 1
    for metric in set(CLASS_KEEP_COL) - set(METHOD_KEEP_COL):
        tmp_f.insert(curr_column, metric, '-')
        curr_column += 1
    method_portion = tmp_f

    result = concat([class_portion, method_portion], sort=False)
    result.to_csv(os.path.join(RESULTS_DIR, project_name, "metrics.csv"), index=False)

    # Clean up excess Source Meter files
    if clean_up_sm_files:
        shutil.rmtree(sc_results_dir)


if __name__ == "__main__":
    project_type = "java" if testing_java else "python"
    project_dir = JAVA_SAMPLE_PROJ_DIR if project_type == "java" else PYTHON_SAMPLE_PROJ_DIR

    # Get project name
    project_name_tokens = project_dir.split(DIR_SEPARATOR)
    project_name = project_name_tokens[len(project_name_tokens) - 1]

    exec_metric_analysis()
    consolidate_metrics()
