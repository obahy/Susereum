import fnmatch
import os
import shlex
import shutil
import sys
from subprocess import Popen
from pandas import read_csv, concat
from constants import CLEAN_UP_SM_FILES, SOURCE_METER_JAVA_PATH, SOURCE_METER_PYTHON_PATH, \
    CLASS_KEEP_COL, METHOD_KEEP_COL, POSIX, DIR_SEPARATOR

import json
import socket
import re

"""Source Meter Wrapper.

Given a valid GitHub repository URL or system path to a project, this module automates the analysis and 
consolidation of pre-specified metrics.

Example:
    To run the module:

        $ python sourceMeterWrapper.py <(GitHub Project Repo) | (Path to Project)>
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
    Popen(run_cmd).wait() if POSIX else Popen(shlex.split(run_cmd, posix=POSIX)).wait()


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
    tmp_f['Path'] = tmp_f['Path']\
        .apply(lambda x: str(x)).apply(lambda x: x.split(DIR_SEPARATOR)[len(x.split(DIR_SEPARATOR)) - 1])
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
    proj_name_tokens = directory.split(DIR_SEPARATOR)
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


def analyze_from_repo(url, results_dir):
    """Clones GitHub project from 'url', executes Source Meter analysis, and consolidates metrics.

    Args:
         url (str): The URL of the GitHub repository containing the project to be analyzed.
         results_dir (str): The path where to store the results
    """
    url_tokens = url.split('/')
    proj_name = url_tokens[len(url_tokens) - 1].strip('.git')
    tmp_dir = os.path.join(os.getcwd(), "..", "tmp")
    if os.path.isdir(tmp_dir):
        clear_dir(tmp_dir)
    curr_dir = os.getcwd()
    os.makedirs(tmp_dir)
    clone_cmd = ["git", "clone", url]
    os.chdir(tmp_dir)
    Popen(clone_cmd).wait() if POSIX else Popen(shlex.split(clone_cmd, posix=POSIX)).wait()
    proj_dir = os.path.join(os.getcwd(), os.listdir(tmp_dir)[0])
    os.chdir(curr_dir)
    proj_type = get_project_type(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    clear_dir(tmp_dir)
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
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    print results_dir
    return results_dir

def download_commit(commit_url):
	"""Uses the commitURL to download the state of the repo at that commit.
	Creates a subdirectory in this script's directory with the repo name and sha
	then it clones the repo at a certain commit inside of that uniquely named dir.
	
		Args:
			commitURL (str): The url of the commit (ex. 'https://github.com/obahy/Susereum/commit/a91e025fcece69ba9fc1614cbe43977630c0eefc')
	"""
	server_ip = "129.108.7.2"    # TODO: use a domain name for the susereum server like susereum.com so that we don't have to hardcode server IP

	# Parse repo name from commit url
    start_of_repo_name = re.search('https://github.com/[^/]+/', commit_url) # [^/] skips all non '/' characters (skipping repo owner name)
    leftovers = commit_url[start_of_repo_name.end():]
    end_of_repo_name = leftovers.index('/')
    repo_name = leftovers[:endOfRepoName]

    # Sends a ping to Google to see what this computer's public IP address is
    # TODO: Change the Susereum server to use a domain like susereum.com and check that instead
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()

    # PARSING INFORMATION
    project_url = commit_url[:commit_url.index('/commit')]
    project_url += ".git"

    sha_index = commit_url.index('commit/') + len('commit/')
    commit_sha = commit_url[sha_ndex:]

    if(my_ip == server_ip):
        #print("I am the server")

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
        #print projectURL

        # DOWNLOADING FILES
		unique_folder_name = repo_name + commit_sha
		os.mkdir(unique_folder_name)
		os.chdir(unique_folder_name)
        os.system('git clone ' + project_url)
        os.chdir(repo_name)
        os.system('git checkout ' + commit_sha)
    else:
        #print("I am the client")
        # DOWNLOADING FILES
		unique_folder_name = repo_name + repo_name + commit_sha
		os.mkdir(unique_folder_name)
		os.chdir(unique_folder_name)
        os.system('git clone ' + project_url)    # Assumes that user's credentials are stored in git
        os.chdir(repo_name)
        os.system('git checkout ' + commit_sha)
	print("Repo commit cloned at: " + unique_folder_name + "/" + repo_name)

def arg_type(arg):
    """Returns the type of argument, either "url"" or "path".

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
