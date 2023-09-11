#!/usr/bin/env bash
set -ev

CONFIG="${GITHUB_WORKSPACE}/.github/config"
sed -i "s|PLACEHOLDER_WORK_DIR|${GITHUB_WORKSPACE}|" "${CONFIG}/localhost.yaml"
verdi setup --non-interactive --config "${CONFIG}/profile.yaml"

# set up localhost computer
verdi computer setup --non-interactive --config "${CONFIG}/localhost.yaml"
verdi computer configure core.local localhost --config "${CONFIG}/localhost-config.yaml"
verdi computer test localhost
verdi daemon start 4
