#
# Simple Makefile for first Flask project
#

##
## Except for installation, all commands should be run with 
## the virtual environment active
##

# Configuration 
#
PYVENV = /usr/local/bin/virtualenv  # This is the version in ix.cs.uoregon.edu

##
## Install in a new environment:
##     We need to rebuild the Python environment to match
##     
install:
	# pyvenv-3.4 env ### BUGGY on ix
	echo "pyvenv without PIP to work around ubuntu bug"
	$(PYVENV) env
	(.  env/bin/activate; pip install -r requirements.txt)

dist:
	pip freeze >requirements.txt

