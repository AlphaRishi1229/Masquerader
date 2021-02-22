#!/usr/bin/env bash

# if any command inside script returns error, exit and return that error
set -e

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
# thanks to it we can just enter `./scripts/run-tests.bash`
cd "${0%/*}/.."

# let's fake failing test for now
echo "Running tests"
echo "............................"
#test_result="pytest"
#$test_result
flake8 --count --statistics --output-file=flake8_index.txt --tee --doctests --benchmark --import-order-style google --docstring-convention google
pytest -rA --cov-report annotate:reports/pytest/coverage_annotate --cov-report html:reports/pytest/coverage_html --junitxml reports/pytest/coverage_junitxml/index.xml --cov-report xml:reports/pytest/coverage_xml/index.xml --cov-report term-missing --cov-branch 
echo Pytest exited $?
