#!/usr/bin/env python3

import subprocess
import json
import yaml
import hashlib
import sys
import os
import urllib.request
import tempfile
import tarfile

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

ASTRIAL_INFO_CMD = "/opt/astrial_sysinfo/sysinfo.py"
ASTRIAL_INFO_DIR = "/opt/astrial_sysinfo"

# Installer server
INSTALL_BASE_URL = "https://example.com/myapp"

INSTALL_SCRIPT = "install.py"
INSTALL_HASH = "install.py.sha256"

DOWNLOAD_DIR = "/tmp"

# Platform sanity checks
EXPECTED_KERNEL = "5.15.71"
EXPECTED_SOC = "i.MX8MP"

# -------------------------------------------------
# Utility functions
# -------------------------------------------------


def run_cmd(cmd):

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def sha256sum(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


def download_file(url, dest):

    print(f"Downloading {url}")

    urllib.request.urlretrieve(url, dest)


# -------------------------------------------------
# ASTRIAL INFO INSTALLATION
# -------------------------------------------------


def install_astrial_info():

    print("astrial_info not found. Installing...")

    try:
        os.system("curl -O -s https://raw.githubusercontent.com/gfilippi/astrial_sysinfo/refs/heads/main/install.sh && chmod 754 ./install.sh && ./install.sh")

        os.chmod(ASTRIAL_INFO_CMD, 0o755)

        print("astrial_info installed successfully")

    except Exception as e:

        print(f"ERROR installing astrial_info: {e}")
        sys.exit(1)


def ensure_astrial_info():

    if not os.path.exists(ASTRIAL_INFO_CMD):
        install_astrial_info()


# -------------------------------------------------
# Run astrial_info
# -------------------------------------------------


def run_astrial_info():

    try:

        result = subprocess.run(
            [ASTRIAL_INFO_CMD, "--json"],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout.strip()

        try:
            return json.loads(output)
        except Exception:
            return yaml.safe_load(output)

    except Exception as e:

        print(f"ERROR running astrial_info: {e}")
        sys.exit(1)


# -------------------------------------------------
# Platform validation
# -------------------------------------------------


def check_platform(info):

    try:

        kernel = info["software"]["yocto"]["kernel"]["kernel_version"]
        soc = info["hardware"]["cpu"]["soc_id"]

    except Exception:

        print("ERROR: missing platform info")
        return False

    if not kernel.startswith(EXPECTED_KERNEL):

        print(f"Unsupported kernel: {kernel}")
        return False

    if EXPECTED_SOC not in soc:

        print(f"Unsupported SoC: {soc}")
        return False

    print("Platform validation OK")

    return True


# -------------------------------------------------
# Installer download
# -------------------------------------------------


def fetch_installer():

    install_url = f"{INSTALL_BASE_URL}/{INSTALL_SCRIPT}"
    hash_url = f"{INSTALL_BASE_URL}/{INSTALL_HASH}"

    install_path = os.path.join(DOWNLOAD_DIR, INSTALL_SCRIPT)
    hash_path = os.path.join(DOWNLOAD_DIR, INSTALL_HASH)

    download_file(install_url, install_path)
    download_file(hash_url, hash_path)

    return install_path, hash_path


# -------------------------------------------------
# Hash verification
# -------------------------------------------------


def verify_hash(file_path, hash_path):

    with open(hash_path) as f:
        expected = f.read().split()[0]

    actual = sha256sum(file_path)

    if expected != actual:

        print("ERROR: SHA256 verification failed")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")

        return False

    print("Installer integrity verified")

    return True


# -------------------------------------------------
# Execute installer
# -------------------------------------------------


def execute_installer(path):

    print(f"Executing installer {path}")

    subprocess.run(
        ["python3", path],
        check=True
    )


# -------------------------------------------------
# MAIN
# -------------------------------------------------


def main():

    ensure_astrial_info()

    info = run_astrial_info()

    if not check_platform(info):
        sys.exit(1)

    install_path, hash_path = fetch_installer()

    if not verify_hash(install_path, hash_path):
        sys.exit(1)

    execute_installer(install_path)


if __name__ == "__main__":
    main()
