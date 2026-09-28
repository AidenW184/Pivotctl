#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# Pivotctl v1.0 Installer
# ============================================================

VERSION="1.0"

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/pivotctl"
COMMAND="/usr/bin/pivotctl"

echo -e "${GREEN}"
echo '██████╗ ██╗██╗   ██╗ ██████╗ ████████╗██╗'
echo '██╔══██╗██║██║   ██║██╔═══██╗╚══██╔══╝██║'
echo '██████╔╝██║██║   ██║██║   ██║   ██║   ██║'
echo '██╔═══╝ ██║╚██╗ ██╔╝██║   ██║   ██║   ╚═╝'
echo '██║     ██║ ╚████╔╝ ╚██████╔╝   ██║   ██╗'
echo '╚═╝     ╚═╝  ╚═══╝   ╚═════╝    ╚═╝   ╚═╝'
echo
echo 'SHUT UP!, SHUT UP!, SHUT UPPPPPPP!!!'
echo -e "${RESET}"

echo -e "${CYAN}Pivotctl v${VERSION} Installer${RESET}"
echo

# ------------------------------------------------------------
# Root check
# ------------------------------------------------------------

if [[ "$EUID" -ne 0 ]]; then
    echo -e "${RED}[-] Root privileges are required.${RESET}"
    echo
    echo "Run:"
    echo
    echo "    sudo ./install.sh"
    echo
    exit 1
fi

# ------------------------------------------------------------
# Platform check
# ------------------------------------------------------------

if [[ "$(uname -s)" != "Linux" ]]; then
    echo -e "${RED}[-] Pivotctl currently supports Linux only.${RESET}"
    exit 1
fi

echo -e "${GREEN}[+] Linux detected.${RESET}"

# ------------------------------------------------------------
# Validate source repository
# ------------------------------------------------------------

echo -e "${CYAN}[*] Validating Pivotctl source...${RESET}"

REQUIRED_PATHS=(
    "pivotctl.py"
    "core"
    "ui"
    "config"
)

for path in "${REQUIRED_PATHS[@]}"; do

    if [[ ! -e "$SOURCE_DIR/$path" ]]; then
        echo -e "${RED}[-] Missing required path: $path${RESET}"
        exit 1
    fi

done

echo -e "${GREEN}[+] Pivotctl source structure detected.${RESET}"

# ------------------------------------------------------------
# Python check
# ------------------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}[-] Python 3 is required.${RESET}"
    exit 1
fi

echo -e "${GREEN}[+] $(python3 --version) detected.${RESET}"

# ------------------------------------------------------------
# Source compilation check
# ------------------------------------------------------------

echo -e "${CYAN}[*] Checking Python source...${RESET}"

python3 -m py_compile \
    "$SOURCE_DIR/pivotctl.py" \
    "$SOURCE_DIR"/core/*.py \
    "$SOURCE_DIR"/ui/*.py

echo -e "${GREEN}[+] Python source validation passed.${RESET}"

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------

echo -e "${CYAN}[*] Checking system dependencies...${RESET}"

MISSING=()

command -v ip >/dev/null 2>&1 \
    || MISSING+=("iproute2")

command -v proxychains4 >/dev/null 2>&1 \
    || MISSING+=("proxychains4")

command -v ssh >/dev/null 2>&1 \
    || MISSING+=("openssh-client")

if [[ ${#MISSING[@]} -gt 0 ]]; then

    echo -e "${YELLOW}[!] Missing required packages:${RESET}"

    for package in "${MISSING[@]}"; do
        echo "    - $package"
    done

    if command -v apt-get >/dev/null 2>&1; then

        echo
        read -r -p "Install missing packages with apt? [Y/n] " answer
        answer="${answer:-Y}"

        if [[ "$answer" =~ ^[Yy]$ ]]; then

            apt-get update
            apt-get install -y "${MISSING[@]}"

        else

            echo -e "${RED}[-] Installation cancelled.${RESET}"
            exit 1

        fi

    else

        echo
        echo -e "${RED}[-] Automatic dependency installation currently supports apt-based systems.${RESET}"
        echo
        echo "Install the missing packages manually and rerun:"
        echo
        echo "    sudo ./install.sh"
        echo

        exit 1

    fi

fi

echo -e "${GREEN}[+] Required dependencies available.${RESET}"

# ------------------------------------------------------------
# Original system backups
# ------------------------------------------------------------

echo -e "${CYAN}[*] Checking original configuration backups...${RESET}"

if [[ -f /etc/hosts ]]; then

    if [[ ! -e /etc/hosts.pre-pivotctl ]]; then

        cp -a \
            /etc/hosts \
            /etc/hosts.pre-pivotctl

        echo -e "${GREEN}[+] Created /etc/hosts.pre-pivotctl${RESET}"

    else

        echo -e "${GREEN}[+] Original hosts backup already exists.${RESET}"

    fi

fi

if [[ -f /etc/proxychains4.conf ]]; then

    if [[ ! -e /etc/proxychains4.conf.pre-pivotctl ]]; then

        cp -a \
            /etc/proxychains4.conf \
            /etc/proxychains4.conf.pre-pivotctl

        echo -e "${GREEN}[+] Created /etc/proxychains4.conf.pre-pivotctl${RESET}"

    else

        echo -e "${GREEN}[+] Original ProxyChains backup already exists.${RESET}"

    fi

fi

# ------------------------------------------------------------
# Existing installation
# ------------------------------------------------------------

if [[ -d "$INSTALL_DIR" ]]; then

    echo -e "${YELLOW}[!] Existing Pivotctl installation detected.${RESET}"
    echo -e "${CYAN}[*] Updating application files...${RESET}"

fi

# ------------------------------------------------------------
# Create installation directory
# ------------------------------------------------------------

mkdir -p "$INSTALL_DIR"

# ------------------------------------------------------------
# Install application
# ------------------------------------------------------------

echo -e "${CYAN}[*] Installing Pivotctl to $INSTALL_DIR...${RESET}"

cp -a \
    "$SOURCE_DIR/pivotctl.py" \
    "$INSTALL_DIR/"

rm -rf \
    "$INSTALL_DIR/core" \
    "$INSTALL_DIR/ui"

cp -a \
    "$SOURCE_DIR/core" \
    "$INSTALL_DIR/core"

cp -a \
    "$SOURCE_DIR/ui" \
    "$INSTALL_DIR/ui"

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

if [[ ! -d "$INSTALL_DIR/config" ]]; then
    cp -a \
        "$SOURCE_DIR/config" \
        "$INSTALL_DIR/config"
else
    echo -e "${YELLOW}[!] Existing installed configuration preserved.${RESET}"
fi

# ------------------------------------------------------------
# Persistent runtime directories
# ------------------------------------------------------------

mkdir -p \
    "$INSTALL_DIR/backups" \
    "$INSTALL_DIR/profiles"

# ------------------------------------------------------------
# Documentation
# ------------------------------------------------------------

if [[ -f "$SOURCE_DIR/README.md" ]]; then
    cp \
        "$SOURCE_DIR/README.md" \
        "$INSTALL_DIR/README.md"
fi

if [[ -f "$SOURCE_DIR/requirements.txt" ]]; then
    cp \
        "$SOURCE_DIR/requirements.txt" \
        "$INSTALL_DIR/requirements.txt"
fi

# ------------------------------------------------------------
# Permissions
# ------------------------------------------------------------

chmod +x \
    "$INSTALL_DIR/pivotctl.py"

find "$INSTALL_DIR" \
    -type d \
    -exec chmod 755 {} \;

find "$INSTALL_DIR" \
    -type f \
    -exec chmod 644 {} \;

chmod 755 \
    "$INSTALL_DIR/pivotctl.py"

# ------------------------------------------------------------
# Global command
# ------------------------------------------------------------

echo -e "${CYAN}[*] Creating global Pivotctl command...${RESET}"

ln -sfn \
    "$INSTALL_DIR/pivotctl.py" \
    "$COMMAND"

# ------------------------------------------------------------
# Final validation
# ------------------------------------------------------------

echo -e "${CYAN}[*] Validating installation...${RESET}"

python3 -m py_compile \
    "$INSTALL_DIR/pivotctl.py" \
    "$INSTALL_DIR"/core/*.py \
    "$INSTALL_DIR"/ui/*.py

if [[ ! -x "$COMMAND" ]]; then
    echo -e "${RED}[-] Global Pivotctl command could not be created.${RESET}"
    exit 1
fi

echo -e "${GREEN}[+] Installation validated.${RESET}"

# ------------------------------------------------------------
# Complete
# ------------------------------------------------------------

echo
echo -e "${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}                  INSTALLATION COMPLETE${RESET}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo

echo "Installed to:"
echo
echo "    $INSTALL_DIR"
echo

echo "Global command:"
echo
echo "    $COMMAND"
echo

echo "Launch with:"
echo
echo -e "    ${CYAN}sudo pivotctl${RESET}"
echo