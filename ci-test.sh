#!/bin/bash

# Print statements
set -e

# Install kube dependency which are required to run test case.
pip3 install -r requirements-kube.txt

# Make directories for artifacts and coverage.
mkdir -p artifacts
mkdir -p coverage

# Run pytest.
pytest -rA --cov=mock_server tests/ --cov-report xml:reports/pytest/coverage_xml/index.xml --cov-report term-missing

# Run xml to json.
python -m tests.coverage_output

# Move coverage to artifacts.
mv -v coverage/** /mnt/artifacts
