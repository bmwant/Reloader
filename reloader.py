import logging
import os
import sys
import subprocess
import time
import runpy
import argparse

_watched_files = set()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

script = None
modify_times = {}

def _reload():
    runpy.run_path(script, run_name='__main__')

    # or if you want to open a new window as double click in Explorer on
    # this file use:
    # os.startfile(script)
    """
    if sys.platform == 'win32':
        # os.execv is broken on Windows and can't properly parse command line
        # arguments and executable name if they contain whitespaces. subprocess
        # fixes that behavior.
        subprocess.Popen("python {script}".format(script=script), shell=True)
        sys.exit(0)
    """


def watch(filename):
    """Add a file to the watch list"""
    _watched_files.add(filename)


def _check_file(modify_times, path):
    modified = os.stat(path).st_mtime  # time of most recent content modification
    if path not in modify_times:
        modify_times[path] = modified
        return
    if modify_times[path] != modified:  # file is modified
        log.info("%s mofified; restarting.", path)
        modify_times[path] = modified
        _reload()


def get_list_of_files(directory, ext):
    files = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            files.append(os.path.abspath(file))
    return files


def check_for_reload():
    for file in _watched_files:
        _check_file(modify_times, file)


def main():
    map(watch, get_list_of_files(r'C:\bmwant\Reloader', '.py'))
    while True:
        # check every second if there is a necessity for reload
        check_for_reload()
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("script", help="python script to autoreload")
    args = parser.parse_args()
    script = os.path.abspath(args.script)
    main()