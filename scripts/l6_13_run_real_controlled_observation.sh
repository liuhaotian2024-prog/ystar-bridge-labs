#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"
python3 l6_real_controlled_external_observation_mission_sprint/tools/build_l6_real_controlled_external_observation_mission_sprint.py
python3 console_read_model/loader/build_team_console_snapshot.py
python3 console_read_model/cli/team_console.py real-controlled-external-observation-mission-sprint
