#!/usr/bin/env bash

set -e

# -------------------------------
# CONFIGURATION
# -------------------------------

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

TARGET_FOLDER="/root/apps/astrial_simpleapp"  # destination folder

SOURCE_FOLDER="$SCRIPT_DIR/src" # folder to copy content from if target does not exist

# -------------------------------
# INSTALL
# -------------------------------

if [[ -d "$TARGET_FOLDER" ]]; then
    echo "Folder $TARGET_FOLDER exists. Removing it completely..."
    rm -rf "$TARGET_FOLDER"
    echo "Folder removed."
    mkdir -p "$TARGET_FOLDER"
    echo "Folder created."
else
    echo "Folder $TARGET_FOLDER does not exist. Creating it..."
    mkdir -p "$TARGET_FOLDER"
    echo "Folder created."
fi

# If source folder exists, copy content
if [[ -d "$SOURCE_FOLDER" ]]; then
    echo "Copying content from $SOURCE_FOLDER to $TARGET_FOLDER..."
    cp -r "$SOURCE_FOLDER"/* "$TARGET_FOLDER"/
    echo "Copy completed."
else
    echo "WARNING: Source folder $SOURCE_FOLDER does not exist. Nothing copied."
fi

# -------------------------------
# POST-INSTALL
# -------------------------------
cd $TARGET_FOLDER
gcc ./helloworld.c -o helloworld
./helloworld
