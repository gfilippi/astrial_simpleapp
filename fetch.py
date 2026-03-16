#!/usr/bin/env python3

import subprocess
import json
import yaml
import sys
import os
import urllib.request
import tempfile
import tarfile

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

# Path to astrial_sysinfo tool
ASTRIAL_INFO_CMD = "/opt/astrial_sysinfo/sysinfo.py"

# GitHub repo for installer
GITHUB_REPO = "gfilippi/astrial_simpleapp"

# Installer filename inside release (can be installer.py or installer.sh)
INSTALLER_NAME = "install.sh"  

# Temporary folder to download/extract release
TEMP_DIR = "/tmp/astrial_simpleapp"

# Target folder where app will be installed (passed to installer)
TARGET_DIR = "/root/apps/astrial_simpleapp"

# -------------------------------------------------
# Utility functions
# -------------------------------------------------


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


# -------------------------------------------------
# Astrial sysinfo
# -------------------------------------------------


def ensure_astrial_sysinfo():
    if not os.path.exists(ASTRIAL_INFO_CMD):
        print("astrial_sysinfo not found. Installing...")
        os.system(
            "curl -s -O https://raw.githubusercontent.com/gfilippi/astrial_sysinfo/refs/heads/main/install.sh "
            "&& chmod +x ./install.sh && ./install.sh"
        )
        os.chmod(ASTRIAL_INFO_CMD, 0o755)
        print("astrial_sysinfo installed.")


def run_astrial_sysinfo():
    try:
        result = subprocess.run([ASTRIAL_INFO_CMD, "--format", "json"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        try:
            return json.loads(output)
        except Exception:
            return yaml.safe_load(output)
    except Exception as e:
        print(f"ERROR running astrial_sysinfo: {e}")
        sys.exit(1)


def check_platform(info, expected_kernel="5.15.71", expected_soc="i.MX8MP"):
    try:
        kernel = info["software"]["yocto"]["kernel"]["kernel_version"]
        soc = info["hardware"]["cpu"]["soc_id"]
    except Exception:
        print("ERROR: missing platform info")
        return False

    if not kernel.startswith(expected_kernel):
        print(f"Unsupported kernel: {kernel}")
        return False

    if expected_soc not in soc:
        print(f"Unsupported SoC: {soc}")
        return False

    print("Platform validation OK")
    return True


# -------------------------------------------------
# GitHub release download
# -------------------------------------------------


def get_latest_release_tarball_url(repo):
    url = f"https://api.github.com/repos/{repo}/releases"
    with urllib.request.urlopen(url) as resp:
        releases = json.load(resp)
        if not releases:
            print("No releases found!")
            sys.exit(1)
        tarball_url = releases[0]["tarball_url"]
        print(f"Latest release tarball: {tarball_url}")
        return tarball_url


def download_and_extract(url, temp_dir):
    """Download tarball and extract to temp_dir."""
    os.makedirs(temp_dir, exist_ok=True)
    archive_path = os.path.join(temp_dir, "release.tar.gz")

    print(f"Downloading release tarball to {archive_path} ...")
    urllib.request.urlretrieve(url, archive_path)

    print(f"Extracting tarball...")
    with tarfile.open(archive_path) as tar:
        tar.extractall(temp_dir)

    # GitHub tarballs create a single root folder
    src_dir = next(
        os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))
    )
    return src_dir


def run_installer(src_dir, installer_name, target_dir):
    """Run the installer inside the release folder and pass the target folder."""
    installer_path = os.path.join(src_dir, installer_name)

    if not os.path.exists(installer_path):
        print(f"ERROR: installer {installer_name} not found in release")
        sys.exit(1)

    print(f"Executing installer: {installer_path} with target folder {target_dir}")

    if installer_name.endswith(".py"):
        subprocess.run(["python3", installer_path, target_dir], check=True)
    elif installer_name.endswith(".sh"):
        subprocess.run(["bash", installer_path, target_dir], check=True)
    else:
        print(f"Unsupported installer type: {installer_name}")
        sys.exit(1)


# -------------------------------------------------
# MAIN
# -------------------------------------------------


def main():
    ensure_astrial_sysinfo()
    info = run_astrial_sysinfo()
    if not check_platform(info):
        sys.exit(1)

    tarball_url = get_latest_release_tarball_url(GITHUB_REPO)
    release_dir = download_and_extract(tarball_url, TEMP_DIR)
    run_installer(release_dir, INSTALLER_NAME, TARGET_DIR)


if __name__ == "__main__":
    main()