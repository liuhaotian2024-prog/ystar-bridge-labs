#!/usr/bin/env python3
"""
Y* Bridge Labs — Deploy CTO Workstation on MAC Mini
Executes setup commands remotely via Telegram bridge.
"""
import asyncio
import sys
from pathlib import Path
from telethon import TelegramClient

API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
BOT_USERNAME = "K9newclaw_bot"
SESSION_FILE = "ystar_telegram_session"

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

async def send_command(client, command, step_name):
    """Send command and wait for response."""
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"CMD:  {command}")
    print(f"{'='*60}")

    await client.send_message(BOT_USERNAME, command)
    await asyncio.sleep(12)  # Wait for execution

    messages = await client.get_messages(BOT_USERNAME, limit=3)
    response = None
    for msg in reversed(messages):
        if msg.sender_id != (await client.get_me()).id:
            response = msg.text
            break

    if response:
        print(f"RESPONSE:\n{response}")
        return response
    else:
        print("WARNING: No response received")
        return None

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start(phone="+17033422330")
    print("Telegram authenticated!")

    results = {}

    # Execute setup commands
    for step_name, command in SETUP_COMMANDS:
        response = await send_command(client, command, step_name)
        results[step_name] = response

        # Check if Claude Code needs installation
        if step_name == "check_claude" and response and "MISSING" in response:
            print("\nClaude Code not found. Installing...")
            install_response = await send_command(client, CLAUDE_INSTALL_CMD[1], CLAUDE_INSTALL_CMD[0])
            results["install_claude"] = install_response

            # Verify installation
            verify_response = await send_command(client, "which claude && claude --version", "verify_claude_install")
            results["verify_claude_install"] = verify_response

    # Generate summary
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)

    success_steps = []
    failed_steps = []
    warning_steps = []

    for step, response in results.items():
        if response is None:
            failed_steps.append(f"{step}: No response")
        elif "MISSING" in response or "error" in response.lower() or "failed" in response.lower():
            warning_steps.append(f"{step}: {response[:100]}")
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
    print("1. Set ANTHROPIC_API_KEY on MAC: export ANTHROPIC_API_KEY=sk-ant-...")
    print("2. Create ~/.clauderc with API key")
    print("3. Configure CTO agent: .claude/agents/cto.md")
    print("4. Start CTO session: cd ~/workspace/Y-star-gov && claude --agent cto")
    print("="*60)

    await client.disconnect()

if __name__ == "__main__":
    print("Y* Bridge Labs — MAC CTO Workstation Deployment")
    print("This script will remotely configure the MAC mini via Telegram.")
    print("\nPress Ctrl+C to cancel, or wait 3 seconds to continue...")

    try:
        import time
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nDeployment cancelled.")
        sys.exit(0)

    asyncio.run(main())
