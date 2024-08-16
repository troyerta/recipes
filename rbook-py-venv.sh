#!/usr/bin/env/ bash

# Build the venv
venv_path="$(dirname $(readlink -f $0))/.rbook-venv"

# Install virtualenv module on your system if necessary:
# python -m pip install virtualenv
python3 -m virtualenv --quiet $venv_path
interpreter="$venv_path/bin"

source "$interpreter/activate"
# python -m pip install --quiet --upgrade pip==21.3.1
# python -m pip install --quiet --requirement "$(dirname $(readlink -f $0))/rbook_requirements.txt"
# python -m pip install --quiet virtualenv
python -m pip install --upgrade pip==21.3.1
python -m pip install --requirement "$(dirname $(readlink -f $0))/rbook_requirements.txt"
python -m pip install virtualenv
