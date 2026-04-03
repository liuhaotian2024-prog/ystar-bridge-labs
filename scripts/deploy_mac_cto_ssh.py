#!/usr/bin/env python3
"""
Y* Bridge Labs — Deploy CTO Workstation on MAC Mini via SSH
Requires SSH key to be set up first (see setup_ssh_access.md)
"""
import subprocess
import sys
from pathlib import Path

MAC_HOST = "liuha@haotians-mac-mini.local"

SETUP_COMMANDS = [
    # Step 1: Check prerequisites
    ("check_node", "node --version 2>&1 || echo 'MISSING: Node.js'"),
    ("check_npm", "npm --version 2>&1 || echo 'MISSING: npm'"),
    ("check_git", "git --version 2>&1 || echo 'MISSING: git'"),
    ("check_python", "python3 --version 2>&1 || echo 'MISSING: python3'"),
    ("check_pip", "pip3 --version 2>&1 || echo 'MISSING: pip3'"),

    # Step 2: Create workspace
    ("create_workspace", "mkdir -p ~/workspace && cd ~/workspace && pwd"),

    # Step 3: Clone repositories (if not exist)
    ("clone_ygov", "cd ~/workspace && (test -d Y-star-gov || git clone https://github.com/liuhaotian2024-prog/Y-star-gov.git) && echo 'Y-star-gov ready'"),
    ("clone_company", "cd ~/workspace && (test -d ystar-bridge-labs || git clone https://github.com/liuhaotian2024-prog/ystar-bridge-labs.git) && echo 'ystar-bridge-labs ready'"),

    # Step 4: Install Y*gov
    ("install_ygov", "cd ~/workspace/Y-star-gov && pip3 install -e . 2>&1 | tail -5"),

    # Step 5: Verify ystar command
    ("verify_ystar", "which ystar && ystar --version"),

    # Step 6: Check if Claude Code is installed
    ("check_claude", "which claude || echo 'MISSING: claude-code'"),

    # Step 7: Setup governance hook
    ("setup_hook", "cd ~/workspace/ystar-bridge-labs && ystar setup --yes 2>&1 && ystar hook-install 2>&1"),

    # Step 8: Run doctor
    ("doctor", "cd ~/workspace/Y-star-gov && ystar doctor 2>&1"),
]

CLAUDE_INSTALL_CMD = ("install_claude", "npm install -g @anthropic-ai/claude-code 2>&1 | tail -10")

def run_ssh_command(command, step_name):
    """Execute command on MAC via SSH."""
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"CMD:  {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", MAC_HOST, command],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr
        print(f"RESPONSE:\n{output}")
        return output, result.returncode == 0

    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return "TIMEOUT", False
    except Exception as e:
        print(f"ERROR: {e}")
        return str(e), False

def main():
    print("Y* Bridge Labs — MAC CTO Workstation Deployment (SSH)")
    print("="*60)

    # Test SSH connectivity
    print("\nTesting SSH connection...")
    output, success = run_ssh_command("whoami", "test_connection")
    if not success:
        print("\nERROR: SSH connection failed!")
        print("Please setup SSH access first:")
        print("  See: C:/Users/liuha/OneDrive/桌面/ystar-company/scripts/setup_ssh_access.md")
        sys.exit(1)

    print(f"\nSSH connection successful! Connected as: {output.strip()}")

    # Execute setup commands
    results = {}
    for step_name, command in SETUP_COMMANDS:
        output, success = run_ssh_command(command, step_name)
        results[step_name] = (output, success)

        # Check if Claude Code needs installation
        if step_name == "check_claude" and "MISSING" in output:
            print("\nClaude Code not found. Installing...")
            install_output, install_success = run_ssh_command(CLAUDE_INSTALL_CMD[1], CLAUDE_INSTALL_CMD[0])
            results["install_claude"] = (install_output, install_success)

            # Verify installation
            verify_output, verify_success = run_ssh_command("which claude && claude --version", "verify_claude_install")
            results["verify_claude_install"] = (verify_output, verify_success)

    # Generate summary
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)

    success_steps = []
    failed_steps = []
    warning_steps = []

    for step, (output, success) in results.items():
        if not success or "MISSING" in output or "error" in output.lower():
            if "MISSING" in output:
                warning_steps.append(f"{step}: {output[:100]}")
            else:
                failed_steps.append(f"{step}: {output[:100]}")
        else:
            success_steps.append(step)

    print(f"\nSUCCESS: {len(success_steps)} steps")
    for step in success_steps:
        print(f"  ✓ {step}")

    if warning_steps:
        print(f"\nWARNINGS: {len(warning_steps)} steps")
        for warning in warning_steps:
            print(f"  ⚠ {warning}")

    if failed_steps:
        print(f"\nFAILED: {len(failed_steps)} steps")
        for failure in failed_steps:
            print(f"  ✗ {failure}")

    print("\n" + "="*60)
    print("Next steps:")
    print("1. Set ANTHROPIC_API_KEY on MAC:")
    print(f"   ssh {MAC_HOST} \"echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zshrc\"")
    print("2. Create ~/.clauderc with API key")
    print("3. Configure CTO agent: .claude/agents/cto.md")
    print("4. Start CTO session:")
    print(f"   ssh {MAC_HOST} \"cd ~/workspace/Y-star-gov && tmux new -d -s cto 'claude --agent cto'\"")
    print("="*60)

if __name__ == "__main__":
    main()
