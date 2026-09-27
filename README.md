# PIVOT!

```text
██████╗ ██╗██╗   ██╗ ██████╗ ████████╗██╗
██╔══██╗██║██║   ██║██╔═══██╗╚══██╔══╝██║
██████╔╝██║██║   ██║██║   ██║   ██║   ██║
██╔═══╝ ██║╚██╗ ██╔╝██║   ██║   ██║   ╚═╝
██║     ██║ ╚████╔╝ ╚██████╔╝   ██║   ██╗
╚═╝     ╚═╝  ╚═══╝   ╚═════╝    ╚═╝   ╚═╝

SHUT UP!, SHUT UP!, SHUT UPPPPPPP!!!
```

**Network Pivot Configuration Manager**
 By AJ Whitfield A.K.A "Hypercube"

Version **1.0**

---

## Overview

**Pivotctl** is a terminal-based network pivot configuration manager designed to simplify the repetitive configuration involved in penetration testing labs, CTF environments, and authorised security assessments.

Rather than repeatedly editing host mappings, ProxyChains configuration, pivot information, and network state by hand, Pivotctl provides a single interactive interface for managing and inspecting them.

Pivotctl is intended to act as a lightweight operator utility rather than automate the penetration testing process itself.

---

## Features

### Hosts Manager

Manage Pivotctl-controlled entries within `/etc/hosts`.

- Add host mappings
- Edit existing mappings
- Remove host mappings
- Remove individual hostnames
- View the current hosts configuration
- Preserve unmanaged system entries

### ProxyChains Manager

Manage `/etc/proxychains4.conf` from the Pivotctl interface.

- View configured proxies
- Add proxies
- Edit proxies
- Remove proxies
- Change ProxyChains chain mode
- Enable or disable Proxy DNS
- View the resulting configuration

Supported configurations include common SOCKS and HTTP proxy entries.

### Pivot Manager

Maintain an internal representation of the current pivot topology.

Pivot information can include:

- Pivot name
- Address
- Reachable networks
- Pivoting tool
- Parent pivot
- Local forwarding port
- Operator notes

Supported tool labels include:

- SSH
- Chisel
- Ligolo-ng
- Socat
- sshuttle
- Other

Pivotctl can represent multi-hop pivot relationships and the networks reachable through them.

### Profiles

Save and restore Pivotctl configurations.

Profiles can contain:

- Managed hosts
- ProxyChains state
- Pivot topology

This makes it possible to preserve configurations for individual labs, targets, or environments and restore them later.

### Network Status

Inspect the current host networking state directly from Pivotctl.

Information includes:

- Network interfaces
- Active interfaces
- Local IP address
- Default gateway
- Routing table
- VPN/tunnel interfaces
- Pivotctl configuration
- Current pivot topology

### Configuration Testing

Pivotctl includes a diagnostic system for checking the current environment.

Checks include:

- Hosts configuration
- ProxyChains configuration
- Proxy availability
- Default route
- VPN/tunnel state
- Pivot topology
- Profiles directory
- Backup directory

Results are displayed as:

```text
[PASS]
[WARN]
[FAIL]
```

---

## Dashboard

Pivotctl presents current network and pivoting state immediately when launched.

Example:

```text
════════════════════════════════════════════════════════════════
                         PIVOT STATUS
════════════════════════════════════════════════════════════════

 SYSTEM
  Host          : WORKSTATION
  Interface     : eth0
  Local IP      : 192.168.1.100
  Gateway       : 192.168.1.1
  VPN / Tunnel  : tun0

 PIVOTCTL
  Managed Hosts : 0
  Proxy Chain   : strict_chain
  Proxy DNS     : enabled
  Proxy         : socks4 127.0.0.1:9050
  Pivots        : 0
  Pivot Networks: 0
```

Values are collected from the current system and Pivotctl configuration rather than being hard-coded.

---

## Requirements

Pivotctl currently has no third-party Python package dependencies.

### Python

Recommended:

```text
Python 3.10+
```

### System

Pivotctl is designed primarily for Linux penetration-testing environments.

Required system components include:

```text
iproute2
proxychains4
OpenSSH
```

The installer can install missing required packages automatically on supported `apt`-based distributions.

Optional pivoting tools include:

```text
Chisel
Ligolo-ng
Socat
sshuttle
```

These tools are not Python dependencies and are not installed through `requirements.txt`.

---

## Installation

Clone the repository:

```bash
git clone git@github.com:AidenW184/Pivotctl.git
cd Pivotctl
```

Make the installer executable:

```bash
chmod +x install.sh
```

Install Pivotctl:

```bash
sudo ./install.sh
```

The installer will:

- Validate the Pivotctl source
- Verify Python availability
- Check required system dependencies
- Offer to install missing dependencies on `apt`-based systems
- Create original system configuration backups where appropriate
- Install Pivotctl under `/opt/pivotctl`
- Create the global `/usr/local/bin/pivotctl` command
- Validate the installed Python source

After installation, launch Pivotctl from anywhere with:

```bash
sudo pivotctl
```

The global command resolves to:

```text
/usr/local/bin/pivotctl
        ↓
/opt/pivotctl/pivotctl.py
```

The original cloned repository is therefore not required to remain in its original location after installation.

---

## Updating

Pull or download the newer Pivotctl source and rerun:

```bash
sudo ./install.sh
```

The installer replaces the installed application code under `/opt/pivotctl` while preserving an existing installed configuration.

After updating:

```bash
sudo pivotctl
```

---

## Uninstallation

Make the uninstaller executable if necessary:

```bash
chmod +x uninstall.sh
```

Then run:

```bash
sudo ./uninstall.sh
```

The uninstaller removes:

```text
/opt/pivotctl
/usr/local/bin/pivotctl
```

Pivotctl's pre-installation system configuration backups are deliberately retained.

The uninstaller does **not** automatically overwrite the current `/etc/hosts` or `/etc/proxychains4.conf` with old backups. Those files may have legitimately changed since Pivotctl was installed.

Any restoration of pre-Pivotctl configuration should therefore be performed manually after reviewing the backup files.

---

## Why Root Is Required

Pivotctl can manage system files including:

```text
/etc/hosts
/etc/proxychains4.conf
```

Writing to these files normally requires elevated privileges.

For this reason, Pivotctl v1.0 is intended to be run using:

```bash
sudo pivotctl
```

Review the configured paths before using Pivotctl against an important workstation or production environment.

---

## Backups

Pivotctl creates backups before modifying managed configuration.

Runtime backups are stored within the installed Pivotctl directory:

```text
/opt/pivotctl/backups/
```

During installation, the installer also preserves the original system configuration where appropriate:

```text
/etc/hosts.pre-pivotctl
/etc/proxychains4.conf.pre-pivotctl
```

Existing pre-Pivotctl backups are preserved rather than overwritten by subsequent installations.

---

## Configuration

The installed Pivotctl configuration is stored in:

```text
/opt/pivotctl/config/settings.json
```

Typical production paths are:

```json
{
    "paths": {
        "hosts_file": "/etc/hosts",
        "proxychains_file": "/etc/proxychains4.conf",
        "profiles_directory": "profiles",
        "backups_directory": "backups"
    }
}
```

Interface behaviour can also be configured, including terminal clearing and banner display.

Existing installed configuration is preserved when the installer is rerun.

---

## Project Structure

```text
Pivotctl/
├── backups/
├── config/
│   └── settings.json
├── core/
│   ├── backup.py
│   ├── config.py
│   ├── hosts.py
│   ├── network.py
│   ├── pivots.py
│   ├── profiles.py
│   ├── proxychains.py
│   └── tester.py
├── profiles/
├── tests/
│   ├── test_hosts.py
│   ├── test_profiles.py
│   └── test_proxychains.py
├── ui/
│   ├── banner.py
│   ├── colours.py
│   ├── hosts_menu.py
│   ├── menu.py
│   ├── network_menu.py
│   ├── pivots_menu.py
│   ├── profiles_menu.py
│   ├── proxychains_menu.py
│   └── test_menu.py
├── install.sh
├── uninstall.sh
├── pivotctl.py
├── README.md
└── requirements.txt
```

The production installation is deployed to:

```text
/opt/pivotctl/
```

---

## Usage

Launch Pivotctl:

```bash
sudo pivotctl
```

The main interface provides:

```text
[1] Hosts Manager
[2] ProxyChains Manager
[3] Pivot Manager
[4] Profiles
[5] Network Status
[6] Test Configuration

[R] Refresh
[Q] Quit
```

Each manager provides its own interactive menu.

Returning from a submenu redraws the dashboard so the displayed state reflects the current configuration.

---

## Profiles

Installed profiles are stored under:

```text
/opt/pivotctl/profiles/
```

Profile names are restricted to safe filename characters.

Profiles can be used to maintain separate Pivotctl configurations for different labs or assessment environments.

Because loading a profile restores managed state, inspect profiles before loading them against a live system configuration.

---

## Development

The cloned repository can be used as the development environment independently of the installed `/opt/pivotctl` copy.

Changes made to the source repository do not affect the installed version until the installer is rerun:

```bash
sudo ./install.sh
```

This provides a simple development workflow:

```text
Develop
   ↓
Test
   ↓
Install / Update
   ↓
Run
```

---

## Development Testing

Check the shell installation scripts:

```bash
bash -n install.sh
bash -n uninstall.sh
```

Compile the Python source:

```bash
python3 -m py_compile pivotctl.py ui/*.py core/*.py
```

Run the existing tests:

```bash
python3 -m unittest discover -s tests -v
```

Test the UI imports:

```bash
python3 -c "import ui.menu; print('[+] Full UI import OK')"
```

Install or update the production copy:

```bash
sudo ./install.sh
```

Confirm the global command points to the installed copy:

```bash
readlink -f /usr/local/bin/pivotctl
```

Expected:

```text
/opt/pivotctl/pivotctl.py
```

Finally, perform a runtime test:

```bash
sudo pivotctl
```

---

## Design Philosophy

Pivotctl is intentionally lightweight.

The objective is not to automate penetration testing or replace understanding of networking and pivoting techniques.

Instead, Pivotctl provides a central interface for configuration and state that an operator would otherwise repeatedly manage by hand.

In short:

```text
Configure.
Pivot.
Keep track of what the hell you changed.
```

---

## Disclaimer

Pivotctl is intended for:

- Authorised penetration testing
- Security research
- CTF environments
- Training laboratories
- Systems you own or have explicit permission to assess

Users are responsible for ensuring they have appropriate authorisation before using Pivotctl against any network or system.

---

## Version

**Pivotctl v1.0**