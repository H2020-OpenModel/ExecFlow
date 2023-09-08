#!/usr/bin/env bash
set -ev

verdi setup --non-interactive --config "${CONFIG}/profile.yaml"

# set up localhost computer
verdi computer setup --non-interactive --config "${CONFIG}/localhost.yaml"
