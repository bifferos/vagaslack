#!/usr/bin/env python2

import os
import six
import sys
import glob
import tarfile
import explodeinstaller
import contextlib
from subprocess import Popen, PIPE

from backports import lzma


def get_vm_name(path):
    name = os.path.splitext(os.path.basename(path))[0]
    name = name.replace("-install-dvd", "-vagrant")
    return name



ISO_PATH = sys.argv[1]
VM_NAME = get_vm_name(ISO_PATH)
VBOX_SOCKET = "/tmp/%s" % VM_NAME
TEMP_DIR = "/ram/" + VM_NAME + "_tmp"
ISO_NAME = "/ram/" + VM_NAME + ".iso"
DISK_NAME = "/ram/" + VM_NAME + ".vdi"
# These are all the disk sets, not related to any one version.
DISK_SETS = "a ap d e f k kde kdei l n t tcl x xap xfce y".split()


def get_disk_set_removals(disk_set):
    path = os.path.join("remove_tags", disk_set)
    if not os.path.exists(path):
        return None
    return [i.decode("utf-8") for i in open(path, "rb").read().split()]


def update_tagfiles(disk_sets_dir):
    """
        Update contents of original tagfiles based on the list of packages to skip.
        There's no point to keep the original tagfiles around as this is all generated.
    """
    for disk_set in DISK_SETS:
        removals = get_disk_set_removals(disk_set)
        out_tags = []
        p = os.path.join(disk_sets_dir, disk_set, "tagfile")
        print("Updating %r" % p)
        for line in open(p).readlines():
            name = line.split(":")[0]
            print(name)
            if (removals is None) or (name in removals):
                out_tags.append(name + ":SKP")
            else:
                out_tags.append(name + ":ADD")
        open(p, "wb").write("\n".join(out_tags).encode("utf-8"))


def is_included(name):
    """
        Find if the package is SKP.
    :param name: name of package
    :return: True/False
    """
    for disk_set in DISK_SETS:
        p = os.path.join("remove_tags", disk_set)
        if os.path.exists(p):
            if name in open(p, "rb").read().split():
                return False
    return True


def open_package_tarfile(name):
    if name.endswith("xz"):
        xz = lzma.LZMAFile(name)
        return tarfile.open(fileobj=xz)
    elif name.endswith("gz"):
        return tarfile.open(name, "r:gz")
    else:
        raise ValueError("unknown compression type")


def check_lilo_utf8():
    wild = os.path.join(TEMP_DIR, "isofs", "slackware*", "a", "lilo*.txz")
    poss = glob.glob(wild)
    if len(poss) != 1:
        raise ValueError("unable to find lilo package in A disk series")
    name = glob.glob(wild)[0]
    tf = open_package_tarfile(name)
    data = tf.extractfile("sbin/liloconfig").read()
    if data.find(b'USE UTF-8 TEXT CONSOLE?') != -1:
        return True
    else:
        return False



def make_expect_parameters():
    fp = open("includes.exp", "wb")
    fp.write(b'set VM_NAME "%s"\n' % VM_NAME.encode("utf-8"))
    fp.write(b'set VBOX_SOCKET "%s"\n' % VBOX_SOCKET.encode("utf-8"))
    mouse = is_included("gpm")
    fp.write(b'set mouse %s\n' % str(mouse).lower().encode("utf-8"))
    network = is_included("net-tools")
    fp.write(b'set network %s\n' % str(network).lower().encode("utf-8"))
    utf8lilo = check_lilo_utf8()
    fp.write(b'set utf8lilo %s\n' % str(utf8lilo).lower().encode("utf-8"))
    fp.close()


def make_shell_parameters():
    fp = open("includes.sh", "wb")
    fp.write(b'VM_NAME=%s\n' % VM_NAME.encode("utf-8"))
    fp.write(b'VBOX_SOCKET=%s\n' % VBOX_SOCKET.encode("utf-8"))
    fp.write(b'DISK_NAME=%s\n' % DISK_NAME.encode("utf-8"))
    fp.write(b'ISO_NAME=%s\n' % ISO_NAME.encode("utf-8"))
    fp.close()



def additions_to_extra():
    """Copy the additions into the extra folder"""
    os.system("iso-read -e VBoxLinuxAdditions.run -i /opt/VirtualBox/additions/VBoxGuestAdditions.iso "
              "-o %s/isofs/extra/VBoxLinuxAdditions.run" % TEMP_DIR)


def vagrant_pub_key_to_extra():
    """Copy the additions into the extra folder"""
    os.system("wget https://raw.githubusercontent.com/hashicorp/vagrant/master/keys/vagrant.pub"
              " -O %s/isofs/extra/vagrant.pub" % TEMP_DIR)


# Adapt a Slackware ISO so it boots over serial port
# And then create a VirtualBox VM to run the ISO.

os.system("rm -rf %s" % TEMP_DIR)

# Extract the ISO
explodeinstaller.extract_all(ISO_PATH, TEMP_DIR)

additions_to_extra()

vagrant_pub_key_to_extra()


disk_sets_dir = os.path.join(TEMP_DIR, "isofs/slackware64")
if not os.path.exists(disk_sets_dir):
    disk_sets_dir = os.path.join(TEMP_DIR, "isofs/slackware")

update_tagfiles(disk_sets_dir)

CFG=os.path.join(TEMP_DIR, "isofs/isolinux/isolinux.cfg")

data = b"serial 0 115200\n" + open(CFG, "rb").read()
data = data.replace(b"SLACK_KERNEL=huge.s", b"SLACK_KERNEL=huge.s console=ttyS0")
data = data.replace(b"SLACK_KERNEL=hugesmp.s", b"SLACK_KERNEL=hugesmp.s console=ttyS0")

open(CFG, "wb").write(data)

explodeinstaller.assemble_all(TEMP_DIR, ISO_NAME)

# Setup parameters for the auto-install expect script:
make_expect_parameters()
make_shell_parameters()
