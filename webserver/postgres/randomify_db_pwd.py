#!/usr/bin/env python3

import random
import string
import os
import subprocess
import re


SETTINGS_FILE = "/srv/jodlgang/jodlgang/jodlgang/settings.py"


def update_password():
    # Create new unique password
    new_pwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

    # Set new password
    cmd = ["sudo", "-u", "postgres", "psql", "-c", "ALTER USER jodlgang WITH PASSWORD '" + new_pwd + "';"]
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    streamdata = child.communicate()[0]
    rc = child.returncode

    if 0 != rc:
        print("Changing user password returned exit code {:d}".format(rc))
        return

    # Read settings file
    with open(SETTINGS_FILE, "r") as f:
        settings = f.read()

    # Replace password
    updated_settings = re.sub("'PASSWORD': 'tothemoon'", "'PASSWORD': '" + new_pwd + "'", settings)

    # Save back to settings file
    with open(SETTINGS_FILE, "w") as f:
        f.write(updated_settings)


def has_default_password():
    with open(SETTINGS_FILE, "r") as f:
        settings = f.read()

    return re.search("'PASSWORD': 'tothemoon'", settings) is not None


if __name__ == "__main__":
    if has_default_password():
        update_password()
