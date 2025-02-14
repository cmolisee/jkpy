# Jira KP(y)
Terminal based application for building statistics on Jira issues.

## tl;dr
1. Clone the repository `git clone https://github.com/cmolisee/jkpy.git` or `git clone git@github.com:cmolisee/jkpy.git`.
3. Install python `brew install python`.
4. Get your email associated with JIRA and create an API token in JIRA.
5. Run `make setup email=<your_email> token=<your_token>`.
6. see makefile or make help to setup the remainder of the configurations.

## Pre-Installation
Ensure you have the following:
1. `python3`.
2. `pip3` (or similar).

## Install python3
1. `brew install python`.
2. verify with `python --version` and see version 3+.

If you installed correctly then `pip3` and `venv` should be installed with `python3`.

## Install Application
1. Pull the main branch `git clone https://github.com/cmolisee/jkpy.git` or `git clone git@github.com:cmolisee/jkpy.git`.
2. Install with `make install`

You can manually install as follows:
    1. `python3 -m venv ~/Downloads/venv/jkpy` or a path of your choice.
    2. `your-venv-path/bin/pip3 install -q build`.
    3. `your-venv-path/bin/python3 -m build`.
    4. `your-venv-path/bin/pip3 install dist/jkpy-1.0.0.tar.gz`.

`~/Downloads/venv/jkpy` is the default VENV path set in the Makefile.
You can update this to create the python venv in a path of your choice by editing the Makefile.

## Running Inside venv
venv (or similar) is simply a container environment to run python. To run custom commands from the terminal you must
start your venv manually:

`source your-venv-path/bin/activate` (i.e. `source ~/Downloads/venv/jkpy/bin/activate`)

This will start the venv so that any commands you run with `pip3`, `python3`, or other installed packages in this environment will be recognized.
If you installed the application as defined above then you will be able to run `jkpy` without the need for `python3` command. As long as the venv
is active you can run the application or any other installed python packages.

To deactivate the venv simply run `deactivate`.
