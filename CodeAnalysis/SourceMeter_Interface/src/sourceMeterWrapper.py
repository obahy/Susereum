import fnmatch
import json
import os
import re
import shutil
import socket
import sys
from subprocess import Popen, check_call, CalledProcessError
from pandas import read_csv, concat
from constants import CLEAN_UP_SM_FILES, SOURCE_METER_JAVA_PATH, SOURCE_METER_PYTHON_PATH, \
    CLASS_KEEP_COL, METHOD_KEEP_COL, CLEAN_UP_REPO_FILES, TMP_DIR

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
    ensure that all .py files are analyzed, we traverse all subdirectories and ensure that __init__.py exists. If it
    does not exist, we add it so that Source Meter can analyze it.

    Args:
        proj_dir (str): The path of the project, whose subdirectories will have __init__.py added.
    """
    added_inits = []
    for root, dirs, files in os.walk(proj_dir):
        files_in_root = os.listdir(root)
        for filename in files_in_root:
            if filename.endswith('.py') and '__init__.py' not in files_in_root:
                f = open(root + os.sep + '__init__.py', 'w')
                f.write('')
                f.close()
                added_inits.append(os.path.join(root, '__init__.py'))
                break
    return added_inits


def remove_inits(added_inits):
    """This function is used when projects of type "python" have been analyzed, and this module had to add
    __init__.py files in order to analyze  Python files. This function takes in a list of added files by the wrapper
    and will remove them.

        Args:
            added_inits (list): A list of paths to added __init__.py files that will be removed.
        """
    for added_init in added_inits:
        os.remove(added_init)


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
    added_inits = []
    if proj_type is "python":
        added_inits = add_inits(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    if len(added_inits):
        remove_inits(added_inits)
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
    added_inits = []
    if proj_type is "python":
        added_inits = add_inits(proj_dir)
    exec_metric_analysis(proj_dir, proj_name, proj_type, results_dir)
    consolidate_metrics(proj_name, proj_type, results_dir)
    if len(added_inits):
        remove_inits(added_inits)
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
        f = open(
            "/home/practicum2018/Suserium/Susereum/CodeAnalysis/SourceMeter_Interface/src/susereumGitHubCredentials",
            "r")
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
    Returns:
        The type of argument, either "url" or "path".
    """
    return "url" if "github.com" in arg else "path"


def is_pathname_valid(pathname):
    """ Returns whether the pathname is writable and valid.
    This method was adapted from a Stack Overflow Question: https://stackoverflow.com/a/34102855

    Args:
        pathname (str): A string representation of a system path.

    Returns:
        `True` if the passed pathname is a valid pathname for the current OS;
        `False` otherwise.
    """
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        pathname = os.path.abspath(pathname)

        # Root directory guaranteed to exist
        root_dirname = os.path.sep
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                if len(pathname_part):
                    if root_dirname is os.path.sep:
                        root_dirname += pathname_part
                    else:
                        root_dirname = root_dirname + os.path.sep + pathname_part
                    os.lstat(root_dirname)
            except OSError:
                return False
        # If a "TypeError" exception was raised, it almost certainly has the
        # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError:
        return False
        # If no exception was raised, all path components and hence this
        # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True


def is_path_creatable(pathname):
    """ Returns whether a pathname is creatable.
        This method was adapted from a Stack Overflow Question: https://stackoverflow.com/a/34102855

    Args:
        pathname (str): A string representation of a system path.
    Returns:
        `True` if the current user has sufficient permissions to create the passed
        pathname; `False` otherwise.
    """
    # Parent directory of the passed path. If empty, we substitute the current
    # working directory (CWD) instead.
    pathname = os.path.abspath(pathname)
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)


def is_path_exists_or_creatable(pathname):
    """ Returns whether a pathname is valid and whether or not it already exists or is creatable.
        This method was adapted from a Stack Overflow Question: https://stackoverflow.com/a/34102855

    Args:
        pathname (str): A string representation of a system path.
    `True` if the passed pathname is a valid pathname and whether it currently exists or
    is hypothetically creatable; `False` otherwise.

    """
    pathname = os.path.abspath(pathname)
    try:
        # To prevent "os" module calls from raising undesirable exceptions on
        # invalid pathnames, is_pathname_valid() is explicitly called first.
        return is_pathname_valid(pathname) or os.path.exists(pathname) or is_path_creatable(pathname)
    # Report failure on non-fatal filesystem complaints (e.g., connection
    # timeouts, permissions issues) implying this path to be inaccessible. All
    # other exceptions are unrelated fatal issues and should not be caught here.
    except OSError:
        return False


def is_valid_github_repo_url(url):
    """ Returns whether a url is a valid GitHub Repo URL, by using 'git ls-remote'.

    Args:
        url (str): A string representation of a system path.
    Returns:
        `True` if 'git ls-remote <url>' call returns 0 (success); `False` otherwise.
    """
    try:
        return check_call(['git', 'ls-remote', url.split('/commit')[0]]) == 0
    except CalledProcessError:
        return False


def main(args):
    """Main method for the Source Meter Wrapper script.

    Args:
        args: System arguments passed into the script
    """
    if len(args) != 3:
        print "Error: Incorrect number of arguments. Usage should be:\n" \
              "$ python sourceMeterWrapper.py <(GitHub Project Repo) | (Path to Project)> " \
              "<Directory Where to Store Results>"
    else:  # Number of args is correct
        if arg_type(args[2]) is "path":  # Verify that args[2] is a valid path
            if not is_path_exists_or_creatable(args[2]):
                print "Error: The second passed argument is not a valid directory."
            else:
                if not is_valid_github_repo_url(args[1]):  # Verify that args[1] is a valid GitHub Repo URL
                    print "Error: The first passed argument is not a valid GitHub Repo URL."
                else:
                    analyze_from_repo(args[1], args[2])


if __name__ == "__main__":
    main(sys.argv)
