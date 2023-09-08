#!/usr/bin/env bash
set -ev

CONFIG="${GITHUB_WORKSPACE}/.github/config"

verdi setup --non-interactive --config "${CONFIG}/profile.yaml"

# set up localhost computer
verdi computer setup --non-interactive --config "${CONFIG}/localhost.yaml"
