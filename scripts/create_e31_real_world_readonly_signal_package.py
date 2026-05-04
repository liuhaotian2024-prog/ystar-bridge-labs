#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from office.mission_command.e31_existing_real_world_observation_wheel_inventory import write_all_artifacts

if __name__ == "__main__":
    print(json.dumps(write_all_artifacts(Path.cwd()), indent=2, sort_keys=True))
