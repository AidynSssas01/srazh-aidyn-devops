#!/usr/bin/env bash
# ------------------------------------------------------------------
# Srazh_Aidyn_system.sh — student and system information
# Author : Srazh Aidyn, group IT2-2308
# Usage  : chmod +x Srazh_Aidyn_system.sh && ./Srazh_Aidyn_system.sh
# ------------------------------------------------------------------

# Project root = parent of the folder that contains this script,
# so the script works from any current directory (also inside Jenkins).
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFO_FILE="$PROJECT_DIR/Srazh_Aidyn_info.txt"

LINE="=============================="

echo "$LINE"
echo "Student Information"
echo "$LINE"
echo "Name: Aidyn"
echo "Surname: Srazh"
echo "Group: IT2-2308"
echo "Student ID: 36210"
echo "$LINE"
echo "System Information"
echo "$LINE"
echo "Username: $(whoami)"
echo "Hostname: $(hostname)"
echo "Current Date: $(date '+%Y-%m-%d %H:%M:%S')"

# uname -s = kernel name, -r = kernel release, -m = architecture
OS_NAME="$(uname -s) $(uname -r) $(uname -m)"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME="$PRETTY_NAME ($OS_NAME)"
fi
echo "Operating System: $OS_NAME"

echo "Disk Usage:"
df -h / | sed 's/^/    /'

echo "Memory Usage:"
if command -v free >/dev/null 2>&1; then
    free -h | sed 's/^/    /'
else
    echo "    'free' is not available on this system"
fi
echo "$LINE"

# Check whether the student information file exists (-f = regular file exists)
if [ -f "$INFO_FILE" ]; then
    echo "Student information file exists."
else
    echo "Student information file does not exist."
fi
