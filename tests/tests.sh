#!/usr/bin/env bash
set -ev

# Make sure the folder containing the workchains is in the python path before the daemon is started
verdi daemon start 4
AIIDA_TEST_PROFILE=test_aiida pytest -vvv --cov-report=xml