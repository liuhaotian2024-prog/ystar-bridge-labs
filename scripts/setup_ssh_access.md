# Setup SSH Access to MAC Mini

## Current Situation

- MAC mini is reachable: `haotians-mac-mini.local` (fe80::87a:eba:d701:fb3%9)
- Windows has SSH key: `~/.ssh/id_ed25519.pub`
- MAC has SSH server running (visible in known_hosts)
- Need to add Windows key to MAC's authorized_keys

## Option 1: Use Telegram Bridge (One-Time Auth Required)

The Telegram bridge script needs interactive authentication when the session expires.

### Manual Steps:
1. Open PowerShell or CMD
2. Run:
   ```bash
   cd C:\Users\liuha\OneDrive\桌面\ystar-company\scripts
   python telegram_bridge.py
   ```
3. When prompted, enter the code sent to your Telegram
4. After successful auth, the session file is saved
5. Future commands work non-interactively

### Then Add SSH Key via Telegram:
```bash
cd C:\Users\liuha\OneDrive\桌面\ystar-company\scripts
python telegram_bridge.py "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
python telegram_bridge.py "echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1 liuha@zippolyon' >> ~/.ssh/authorized_keys"
python telegram_bridge.py "chmod 600 ~/.ssh/authorized_keys"
```

### Test SSH:
```bash
ssh liuha@haotians-mac-mini.local "whoami"
```

## Option 2: Physical Access to MAC

If you can physically access the MAC mini:

1. Open Terminal on MAC
2. Run:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1 liuha@zippolyon' >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. Test from Windows:
   ```bash
   ssh liuha@haotians-mac-mini.local "whoami"
   ```

## Option 3: Screen Sharing

If Screen Sharing is enabled on MAC:

1. On Windows, use VNC client (e.g., TightVNC, RealVNC)
2. Connect to: `vnc://haotians-mac-mini.local:5900`
3. Follow Option 2 steps in Terminal

## After SSH Setup

Once SSH key is added, you can deploy CTO workstation:

```bash
# Test connection
ssh liuha@haotians-mac-mini.local "uname -a"

# Run deployment commands
ssh liuha@haotians-mac-mini.local "mkdir -p ~/workspace"
ssh liuha@haotians-mac-mini.local "cd ~/workspace && git clone https://github.com/liuhaotian2024-prog/Y-star-gov.git"
ssh liuha@haotians-mac-mini.local "cd ~/workspace && git clone https://github.com/liuhaotian2024-prog/ystar-bridge-labs.git"

# Or run the automated script
python C:/Users/liuha/OneDrive/桌面/ystar-company/scripts/deploy_mac_cto_ssh.py
```

## Windows SSH Public Key

Your current Windows SSH public key to add to MAC:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1 liuha@zippolyon
```

## Verification

After setup, verify SSH works:
```bash
# Test basic connection
ssh liuha@haotians-mac-mini.local "echo 'SSH access working'"

# Test git
ssh liuha@haotians-mac-mini.local "git --version"

# Test python
ssh liuha@haotians-mac-mini.local "python3 --version"

# Test workspace
ssh liuha@haotians-mac-mini.local "ls -la ~/workspace"
```

---

Created: 2026-04-01
Purpose: Enable CTO workstation deployment on MAC mini
