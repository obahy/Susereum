import fnmatch
import json
import os
import re
import shutil
import socket
import sys
from subprocess import Popen
from pandas import read_csv, concat
from constants import CLEAN_UP_SM_FILES, SOURCE_METER_JAVA_PATH, SOURCE_METER_PYTHON_PATH, \
    CLASS_KEEP_COL, METHOD_KEEP_COL, CLEAN_UP_REPO_FILES, FOLDER, TMP_DIR

"""Source Meter Wrapper.

Given a valid GitHub repository URL or system path to a project, and a path where to store results, this module 
automates the analysis of a project and consolidation of pre-specified metrics.

Example:
    To run the module:

        $ python sourceMeterWrapper.py <(GitHub Project Repo) | (Path to Project)> < Path where to store results >
"""


def exec_metric_analysis(project_dir, project_name, project_type, results_dir):
    """Executes Source Meter Analysis on the project at 'project_dir'.

        Args:
            project_dir (str): The path to the directory containing the project's source files.
            project_name (str):  The name of the project to be analyzed.
            project_type (str): The type of the project to be analyzed ("java"/"python").
            results_dir (str): The path where to store the results
        """
    run_cmd = [SOURCE_METER_PYTHON_PATH,
               "-projectBaseDir:" + project_dir,
               "-projectName:" + project_name,
               "-resultsDir:" + results_dir,
               "-runMetricHunter:false",
               "-runFaultHunter:false",
               "-runDCF:false",
               "-runMET:true",
               "-runPylint:false"
               ] if project_type == "python" else \
        [SOURCE_METER_JAVA_PATH,
         "-projectBaseDir=" + project_dir,
         "-projectName=" + project_name,
         "-resultsDir=" + results_dir,
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
    w = open('debug.txt', 'w')
    w.write(str(run_cmd))
    w.close()
    Popen(run_cmd).wait()


def consolidate_metrics(project_name, project_type, results_dir):
    """Creates a 'metrics.csv' file containing a subset of Source Meter-generated metrics at both Class/Method levels.
        Clears Source Meter-generated files to free disk space, depending on the value of 'CLEAN_UP_SM_FILES'
        in 'constants.py'.

        Args:
            project_name (str):  The name of the analyzed project.
            project_type (str): The type for the analyzed project ("java"/"python").
            results_dir (str): The path where to store the results
        """
    # Consolidate Source Meter Metrics
    sc_results_dir = os.path.join(results_dir, project_name, "java" if project_type == "java" else "python")
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
    tmp_f['Path'] = tmp_f['Path'] \
        .apply(lambda x: str(x)).apply(lambda x: x.split(os.path.sep)[len(x.split(os.path.sep)) - 1])
    # Insert 'Type of Smell' column
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
    result.to_csv(os.path.join(results_dir, project_name + ".csv"), index=False)

    # Clean up excess Source Meter files
    if CLEAN_UP_SM_FILES:
        clear_dir(os.path.join(results_dir, project_name))


def clear_dir(directory):
    """Clears a given directory.

    Args:
        directory (str): The path to the directory to be removed.
    """
    shutil.rmtree(directory)


def get_project_name(directory):
    """Returns the name of the project, given the path to the directory of the project.

    Args:
        directory (str): The path to the directory of the project.
    Returns:
        str: The name of the project.
    """
    proj_name_tokens = directory.split(os.path.sep)
    return proj_name_tokens[len(proj_name_tokens) - 1]


def get_project_type(directory):
    """Returns the type of the project, either "java" or "python", based on the file extensions in 'directory'.

    Args:
        directory (str): The path to the directory of the project.
    Returns:
        str: "java" or "python"
    """
    java_files = [os.path.join(dirpath, f)
                  for dirpath, dirnames, files in os.walk(directory) for f in fnmatch.filter(files, '*.java')]
    python_files = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(directory) for f in fnmatch.filter(files, '*.py')]
    return "java" if len(java_files) and len(java_files) > len(python_files) else "python"


def add_inits(proj_dir):
    """This function is used when projects of type "python" are going to be analyzed. Source Meter assumes
    that each directory for a Python project contains __init__.py files. Because of this, f a directory contains .py
    files and the directory does not contain an __init__.py file, Source Meter will ignore it. To counter this, and
    ensure that all .py files are analyzed, we traverse all subdirectories and ensure that __init__.py exists. Adding
    it where it is not needed has no side effects, as Source Meter will only consider .py files.

    Args:
        proj_dir (str): The path of the project, whose subdirectories will have __init__.py added.
    """
    for root, dirs, files in os.walk(proj_dir):
        f = open(root + os.sep + '__init__.py', 'w')
        f.write('')
        f.close()


def analyze_from_repo(url, results_dir):
    """Clones GitHub project from 'url', executes Source Meter analysis, and consolidates metrics.

    Args:
         url (str): The URL of the GitHub repository containing the project to be analyzed.
         results_dir (str): The path where to store the results
    """
    proj_info = download_commit(url)
    proj_name = proj_info[0]
    proj_dir = proj_info[1]
    proj_type = get_project_type(proj_dir)
    if proj_type is "python":
        add_inits(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    if CLEAN_UP_REPO_FILES:
        clear_dir(TMP_DIR)
    print results_dir
    return results_dir


def analyze_from_path(proj_dir, results_dir):
    """Executes Source Meter analysis and consolidates metrics, given the path to the project.

        Args:
             proj_dir (str): The directory of the project to be analyzed.
             results_dir (str): The path where to store the results
    """
    if proj_dir[-1] == '/':
        proj_dir = proj_dir[:-1]
    proj_name = get_project_name(proj_dir)
    proj_type = get_project_type(proj_dir)
    if proj_type is "python":
        add_inits(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    print results_dir
    return results_dir


def download_commit(repo_url):
    """
    Uses the repo_url to determine if the url specifies a particular commit. If it the url specifies a commit, download
    the state of the repo at that commit inside a subdirectory in TMP_DIR with the repo name and sha. Otherwise, just
    clone the repo without specifying a commit.

    Args:
        repo_url (str): The url of the repo
            (ex. 'https://github.com/obahy/Susereum/commit/a91e025fcece69ba9fc1614cbe43977630c0eefc')
            (ex. 'https://github.com/obahy/Susereum.git')
            (ex. 'https://github.com/obahy/Susereum')
    Returns:
        A tuple containing (Project Name, Project Directory)
    """
    # TODO: use a domain name for the susereum server like susereum.com so that we don't have to hardcode server IP
    server_ip = "129.108.7.2"

    if '/commit' in repo_url:
        # print("repo_url testing: " + repo_url)
        # Parse repo name from commit url
        start_of_repo_name = re.search('https://github.com/[^/]+/',
                                       repo_url)  # [^/] skips all non '/' characters (skipping repo owner name)
        repo_name_and_after = repo_url[start_of_repo_name.end():]
        end_of_repo_name_index = repo_name_and_after.index('/')
        repo_name = repo_name_and_after[:end_of_repo_name_index]
        # print("repo_name: " + repo_name)

        # PARSING INFORMATION
        project_url = repo_url[:repo_url.index('/commit')]
        project_url += ".git"

        sha_index = repo_url.index('commit/') + len('commit/')
        commit_sha = repo_url[sha_index:]
    else:
        url_tokens = repo_url.split('/')
        repo_name = url_tokens[len(url_tokens) - 1].strip('.git')
        project_url = repo_url
        commit_sha = ''

    # Sends a ping to Google to see what this computer's public IP address is
    # TODO: Change the Susereum server to use a domain like susereum.com and check that instead
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()

    # Check if I am the server, if I am add credentials to the project_url before downloading the repo
    if my_ip == server_ip:
        # ADD SERVER CREDENTIALS TO GIT CLONE COMMAND
        f = open("susereumGitHubCredentials", "r")
        contents = f.read()
        contents = json.loads(contents)
        username = contents['username']
        password = contents['password']

        github_index = project_url.index('github.com/')
        right_of_url = project_url[github_index:]
        left_of_url = "https://" + username + ":" + password + "@"
        project_url = left_of_url + right_of_url
    return download_repo(repo_name, commit_sha, project_url)


def download_repo(repo_name, commit_sha, project_url):
    """
    This utility function downloads a commit at <repo_name><commit_sha>/<repo_name>

    Args:
        repo_name: The name of the repo to download
        commit_sha: The sha of the commit to be downloads
        project_url: The full project url including the commit sha and potentially GitHub credentials
    Returns:
        A tuple containing (Project Name, Project Directory)
    """
    unique_folder_name = repo_name + commit_sha
    if not os.path.isdir(TMP_DIR):
        os.mkdir(TMP_DIR)
    curr_dir = os.getcwd()
    os.chdir(TMP_DIR)
    if os.path.isdir(unique_folder_name):
        clear_dir(unique_folder_name)
    os.mkdir(unique_folder_name)
    os.chdir(unique_folder_name)
    clone_cmd = ['git', 'clone', project_url]
    Popen(clone_cmd).wait()
    os.chdir(repo_name)
    proj_path = os.path.dirname(os.path.abspath(repo_name))
    if commit_sha:
        checkout_cmd = ['git', 'checkout', commit_sha]
        Popen(checkout_cmd).wait()
    os.chdir(curr_dir)
    return repo_name, proj_path


def arg_type(arg):
    """Returns the type of argument, either "url" or "path".

    Args:
        arg (str): Either a URL to a GitHub repository or the system path to a project.
    """
    return "url" if "github.com" in arg else "path"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Error: Incorrect number of arguments. Usage should be:\n" \
              "$ python sourceMeterWrapper.py <(GitHub Project Repo) | (Path to Project)> " \
              "<Directory Where to Store Results>"
    elif arg_type(sys.argv[1]) is "url":
        analyze_from_repo(sys.argv[1], sys.argv[2])
    elif os.path.isdir(sys.argv[1]):
        analyze_from_path(sys.argv[1], sys.argv[2])
    else:
        print "Error: The passed argument is not a url and it is not a valid directory."
