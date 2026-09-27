#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# Pivotctl v1.0 Uninstaller
# ============================================================

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

INSTALL_DIR="/opt/pivotctl"
COMMAND="/usr/local/bin/pivotctl"

echo -e "${CYAN}Pivotctl v1.0 Uninstaller${RESET}"
echo

# ------------------------------------------------------------
# Root check
# ------------------------------------------------------------

if [[ "$EUID" -ne 0 ]]; then

    echo -e "${RED}[-] Root privileges are required.${RESET}"
    echo
    echo "Run:"
    echo
    echo "    sudo ./uninstall.sh"
    echo

    exit 1

fi

# ------------------------------------------------------------
# Detect installation
# ------------------------------------------------------------

if [[ ! -e "$INSTALL_DIR" && ! -L "$COMMAND" ]]; then

    echo -e "${YELLOW}[!] Pivotctl does not appear to be installed.${RESET}"
    exit 0

fi

echo "This will remove:"
echo
echo "    $INSTALL_DIR"
echo "    $COMMAND"
echo
echo -e "${YELLOW}[!] Saved Pivotctl profiles and internal backups will also be removed.${RESET}"
echo

read -r -p "Remove Pivotctl? [y/N] " answer

if [[ ! "$answer" =~ ^[Yy]$ ]]; then

    echo
    echo -e "${YELLOW}[!] Uninstall cancelled.${RESET}"
    exit 0

fi

# ------------------------------------------------------------
# Remove command
# ------------------------------------------------------------

if [[ -L "$COMMAND" ]]; then

    TARGET="$(readlink "$COMMAND")"

    if [[ "$TARGET" == "$INSTALL_DIR/pivotctl.py" ]]; then

        rm "$COMMAND"

        echo -e "${GREEN}[+] Removed $COMMAND${RESET}"

    else

        echo -e "${YELLOW}[!] $COMMAND points somewhere unexpected:${RESET}"
        echo "    $TARGET"
        echo
        echo -e "${YELLOW}[!] Leaving the command untouched.${RESET}"

    fi

elif [[ -e "$COMMAND" ]]; then

    echo -e "${YELLOW}[!] $COMMAND exists but is not a Pivotctl symlink.${RESET}"
    echo -e "${YELLOW}[!] Leaving it untouched.${RESET}"

fi

# ------------------------------------------------------------
# Remove application
# ------------------------------------------------------------

if [[ -d "$INSTALL_DIR" ]]; then

    rm -rf "$INSTALL_DIR"

    echo -e "${GREEN}[+] Removed $INSTALL_DIR${RESET}"

fi

# ------------------------------------------------------------
# Original configuration backups
# ------------------------------------------------------------

echo

if [[ -f /etc/hosts.pre-pivotctl ]]; then

    echo -e "${CYAN}[*] Original hosts backup retained:${RESET}"
    echo "    /etc/hosts.pre-pivotctl"

fi

if [[ -f /etc/proxychains4.conf.pre-pivotctl ]]; then

    echo -e "${CYAN}[*] Original ProxyChains backup retained:${RESET}"
    echo "    /etc/proxychains4.conf.pre-pivotctl"

fi

echo
echo -e "${YELLOW}[!] System configuration was NOT automatically restored.${RESET}"
echo

echo "If you intentionally want to restore the pre-Pivotctl files,"
echo "review the backups first and restore them manually."

echo
echo -e "${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}                    UNINSTALL COMPLETE${RESET}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo