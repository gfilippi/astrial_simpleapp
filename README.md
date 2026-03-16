# astrial_simpleapp
The purpose of this repo is to provide a trivial example on how to execute a default "fetch.py" script and install 3rd party apps direclty on the ASTRIAL platform.

# how to install
Simply run on the ASTRIAL platform the following command:

```
 curl -O -s https://raw.githubusercontent.com/gfilippi/astrial_simpleapp/refs/heads/main/fetch.py && chmod 754 ./fetch.py && ./fetch.py
```

# how to use
The fetch script is an template that leverages the astrial_sysinfo tool (separate repo). A 3rd party app only needs to customize the "platform check" to verify that all the system informations are correct for install and execution of the app itself.

See this part of the fetch script to add more sanity checks:

```
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
```

Once all the sanity checks are passed the fetch script will run the installer (either .sh or .py) which can be fully customized by the contributor (no default procedure).

For this example it does create a folder under /root/apps, install and compile the "helloworld.c".
