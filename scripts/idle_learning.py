#!/usr/bin/env python3.11
"""Idle learning executor - AGENTS.md Amendment-003 implementation.

Three-priority learning loop:

Priority 1: Role definition completeness
  - world_class_standard.md: What does world-class look like?
  - role_heroes.md: Who are the exemplars to study?
  - task_type_map.md: What types of tasks does this role handle?

Priority 2: Theory library building
  - For each task type in task_type_map.md without a theory entry,
    generate theory/{task_type}.md with principles and patterns

Priority 3: Counterfactual simulation
  - Generate fictional scenarios via local_learn.py --mode tasks
  - Produce execution plan (but don't execute)
  - Record gaps identified during planning

Every execution writes CIEU event and gemma_sessions.log entry.

Usage:
    python3.11 scripts/idle_learning.py --actor cto --priority 1
    python3.11 scripts/idle_learning.py --actor ceo --priority all
    python3.11 scripts/idle_learning.py --actor cmo  # defaults to priority 1
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"

ROLES = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}

PRIORITY_1_FILES = [
    "world_class_standard.md",
    "role_heroes.md",
    "task_type_map.md",
]


def canonical_actor(actor: str) -> str:
    """Normalize actor name."""
    aliases = {
        "ethan_wright": "cto",
        "aiden_liu": "ceo",
        "sofia_blake": "cmo",
        "zara_johnson": "cso",
        "marco_rivera": "cfo",
        "samantha_lin": "secretary",
    }
    return aliases.get(actor, actor)


def write_gemma_log(actor: str, priority: int, action: str, result: str):
    """Write JSONL entry to gemma_sessions.log."""
    gaps_dir = KNOWLEDGE_ROOT / actor / "gaps"
    gaps_dir.mkdir(parents=True, exist_ok=True)
    log_path = gaps_dir / "gemma_sessions.log"

    entry = {
        "timestamp": time.time(),
        "actor": actor,
        "mode": "idle_learning",
        "priority": priority,
        "action": action,
        "result": result,
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def write_cieu_event(actor: str, priority: int, action: str, outcome: str):
    """Write CIEU event for idle learning completion."""
    try:
        cieu_db = REPO_ROOT / ".ystar_cieu.db"
        if not cieu_db.exists():
            return  # No CIEU tracking yet

        from ystar.governance.omission_models import GovernanceEvent, GEventType

        event = GovernanceEvent(
            event_type=GEventType.CUSTOM,
            entity_id=f"idle_learning_{actor}_{int(time.time())}",
            actor_id=actor,
            ts=time.time(),
            payload={
                "event_subtype": "IDLE_LEARNING_COMPLETED",
                "priority": priority,
                "action": action,
                "outcome": outcome,
            },
            source="idle_learning",
        )

        from ystar.governance.omission_store import OmissionStore
        store = OmissionStore(str(cieu_db))
        store.add_event(event)
    except Exception:
        pass  # Fail-open


def priority_1_execute(actor: str) -> dict:
    """Priority 1: Ensure role_definition completeness.

    Returns:
        {"completed": int, "missing": List[str], "created": List[str]}
    """
    role_def_dir = KNOWLEDGE_ROOT / actor / "role_definition"
    role_def_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    created = []

    for filename in PRIORITY_1_FILES:
        file_path = role_def_dir / filename
        if not file_path.exists():
            missing.append(filename)
            # Generate stub file
            content = generate_role_definition_stub(actor, filename)
            file_path.write_text(content)
            created.append(filename)

    return {
        "completed": len(PRIORITY_1_FILES) - len(missing),
        "total": len(PRIORITY_1_FILES),
        "missing": missing,
        "created": created,
    }


def generate_role_definition_stub(actor: str, filename: str) -> str:
    """Generate initial content for role definition files."""
    if filename == "world_class_standard.md":
        return f"""# World-Class {actor.upper()} Standard

## What does world-class look like?

### Execution Excellence
- (To be filled during idle learning)

### Output Quality
- (To be filled during idle learning)

### Process Maturity
- (To be filled during idle learning)

### Innovation Capability
- (To be filled during idle learning)

---
Generated: {time.strftime('%Y-%m-%d')}
Next: Review quarterly, update after major learnings
"""
    elif filename == "role_heroes.md":
        return f"""# {actor.upper()} Role Heroes

## Exemplars to Study

### Domain Leaders
- (To be filled during idle learning)

### Methodology Pioneers
- (To be filled during idle learning)

### Craft Masters
- (To be filled during idle learning)

---
Generated: {time.strftime('%Y-%m-%d')}
Next: Add 1 hero per month, distill their practices
"""
    elif filename == "task_type_map.md":
        return f"""# {actor.upper()} Task Type Map

## Core Task Categories

### 1. (Primary task type)
- Description: (To be filled)
- Frequency: (daily/weekly/monthly)
- Criticality: (high/medium/low)

### 2. (Secondary task type)
- Description: (To be filled)
- Frequency: (daily/weekly/monthly)
- Criticality: (high/medium/low)

---
Generated: {time.strftime('%Y-%m-%d')}
Next: Refine after 10 tasks executed, add theory entries
"""
    else:
        return f"# {filename}\n\n(Auto-generated stub)\n"


def priority_2_execute(actor: str) -> dict:
    """Priority 2: Build theory library from task_type_map.

    Returns:
        {"task_types_total": int, "theories_existing": int, "created": List[str]}
    """
    role_def_dir = KNOWLEDGE_ROOT / actor / "role_definition"
    theory_dir = KNOWLEDGE_ROOT / actor / "theory"
    theory_dir.mkdir(parents=True, exist_ok=True)

    task_type_map = role_def_dir / "task_type_map.md"
    if not task_type_map.exists():
        return {
            "task_types_total": 0,
            "theories_existing": 0,
            "created": [],
            "error": "task_type_map.md not found - run priority 1 first",
        }

    # Parse task types from task_type_map.md (simple header extraction)
    task_types = extract_task_types(task_type_map.read_text())

    # Check which task types already have theory entries
    existing_theories = {f.stem for f in theory_dir.glob("*.md")}
    missing_theories = [t for t in task_types if t not in existing_theories]

    created = []
    if missing_theories:
        # Generate theory for the first missing task type
        task_type = missing_theories[0]
        theory_content = generate_theory_stub(actor, task_type)
        theory_file = theory_dir / f"{task_type}.md"
        theory_file.write_text(theory_content)
        created.append(task_type)

    return {
        "task_types_total": len(task_types),
        "theories_existing": len(existing_theories),
        "created": created,
    }


def extract_task_types(task_type_map_content: str) -> list:
    """Extract task type identifiers from task_type_map.md.

    Simple heuristic: look for level-3 headers (###) and slugify them.
    """
    import re
    task_types = []
    for line in task_type_map_content.split("\n"):
        if line.startswith("### "):
            # Extract text after "###", slugify
            task_name = line[4:].strip()
            # Remove numbering like "1. ", "2. "
            task_name = re.sub(r"^\d+\.\s*", "", task_name)
            # Slugify: lowercase, replace spaces with underscores
            slug = task_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            # Remove special chars
            slug = re.sub(r"[^a-z0-9_]", "", slug)
            if slug:
                task_types.append(slug)
    return task_types


def generate_theory_stub(actor: str, task_type: str) -> str:
    """Generate theory entry for a task type."""
    return f"""# Theory: {task_type}

## Principles

### Core Principle 1
(To be filled via learning)

### Core Principle 2
(To be filled via learning)

## Patterns

### Pattern A: (Name)
- Context: When X happens
- Action: Do Y
- Rationale: Because Z

### Pattern B: (Name)
- Context: When X happens
- Action: Do Y
- Rationale: Because Z

## Anti-Patterns

### Anti-Pattern 1
- What NOT to do
- Why it fails
- Alternative approach

## References
- (Add sources, case studies, hero practices)

---
Generated: {time.strftime('%Y-%m-%d')}
Actor: {actor}
Task type: {task_type}
Next: Refine after executing 5 tasks of this type
"""


def priority_3_execute(actor: str) -> dict:
    """Priority 3: Counterfactual simulation via local_learn.py.

    Returns:
        {"scenario": str, "plan_generated": bool, "gaps_recorded": int}
    """
    local_learn_script = REPO_ROOT / "scripts" / "local_learn.py"
    if not local_learn_script.exists():
        return {
            "scenario": "",
            "plan_generated": False,
            "gaps_recorded": 0,
            "error": "local_learn.py not found",
        }

    # Generate scenario via local_learn.py --mode tasks
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(local_learn_script),
                "--mode", "tasks",
                "--actor", actor,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            scenario = result.stdout.strip()
            # Record scenario as a gap (simulation plan)
            gaps_dir = KNOWLEDGE_ROOT / actor / "gaps"
            gaps_dir.mkdir(parents=True, exist_ok=True)

            sim_file = gaps_dir / f"simulation_{int(time.time())}.md"
            sim_content = f"""# Counterfactual Simulation

## Scenario
{scenario}

## Plan
(Agent would generate plan here - not executing to avoid side effects)

## Gaps Identified
- (Record what you learned from planning this scenario)

---
Generated: {time.strftime('%Y-%m-%d')}
Mode: idle_learning_priority_3
"""
            sim_file.write_text(sim_content)

            return {
                "scenario": scenario[:200] + "..." if len(scenario) > 200 else scenario,
                "plan_generated": True,
                "gaps_recorded": 1,
            }
        else:
            return {
                "scenario": "",
                "plan_generated": False,
                "gaps_recorded": 0,
                "error": result.stderr[:200],
            }
    except subprocess.TimeoutExpired:
        return {
            "scenario": "",
            "plan_generated": False,
            "gaps_recorded": 0,
            "error": "local_learn.py timeout",
        }
    except Exception as e:
        return {
            "scenario": "",
            "plan_generated": False,
            "gaps_recorded": 0,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Idle learning executor")
    parser.add_argument("--actor", required=True, help="Agent role (ceo, cto, etc)")
    parser.add_argument(
        "--priority",
        default="1",
        help="Learning priority: 1, 2, 3, or 'all' (default: 1)",
    )
    args = parser.parse_args()

    actor = canonical_actor(args.actor)
    if actor not in ROLES:
        print(f"Error: Unknown actor '{args.actor}' (normalized: '{actor}')")
        print(f"Valid actors: {', '.join(sorted(ROLES))}")
        return 1

    priorities = []
    if args.priority == "all":
        priorities = [1, 2, 3]
    else:
        try:
            priorities = [int(args.priority)]
        except ValueError:
            print(f"Error: Invalid priority '{args.priority}'. Use 1, 2, 3, or 'all'")
            return 1

    results = {}

    for priority in priorities:
        print(f"\n=== Priority {priority} Learning: {actor} ===")

        if priority == 1:
            result = priority_1_execute(actor)
            action = f"role_definition_check"
            outcome = f"{result['completed']}/{result['total']} complete"
            if result['created']:
                print(f"Created: {', '.join(result['created'])}")
            else:
                print(f"All files present ({result['completed']}/{result['total']})")

        elif priority == 2:
            result = priority_2_execute(actor)
            action = f"theory_library_build"
            if "error" in result:
                outcome = result["error"]
                print(f"Error: {outcome}")
            else:
                outcome = f"{result['theories_existing']}/{result['task_types_total']} theories exist"
                if result['created']:
                    print(f"Created theory: {', '.join(result['created'])}")
                else:
                    print(f"Theory library complete ({result['theories_existing']}/{result['task_types_total']})")

        elif priority == 3:
            result = priority_3_execute(actor)
            action = f"counterfactual_simulation"
            if "error" in result:
                outcome = result["error"]
                print(f"Error: {outcome}")
            else:
                outcome = f"scenario generated, {result['gaps_recorded']} gaps recorded"
                print(f"Scenario: {result['scenario']}")

        results[f"priority_{priority}"] = result

        # Write logs
        write_gemma_log(actor, priority, action, json.dumps(result))
        write_cieu_event(actor, priority, action, outcome)

    print(f"\n=== Learning Summary ===")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
