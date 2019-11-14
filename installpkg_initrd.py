#!/usr/bin/env python3

import tarfile
import re
import os
import sys


def get_config():
    d = {}
    rex = re.compile(r"^(.*)=(.*)$")
    for line in open("./includes.sh").readlines():
        m = rex.match(line)
        name = m.group(1)
        value = m.group(2)
        d[name] = value
    return d


def blacklisted(name):
    for b in ["usr/doc/", "usr/man/", "usr/include/", "install/", ".", "install"]:
        if name.startswith(b):
            return True
        if name == b:
            return True
    return False


def read_dirs(path):
    dirs = []
    rex = re.compile("^dir (\S+) .*$")
    for line in open(path).readlines():
        m = rex.match(line)
        if m:
            dirs.append(m.group(1))
    return dirs


def extract(tf, initrd):
    spec = initrd + ".spec"
    existing_dirs = read_dirs(spec)
    added_lines = []
    for info in tf:
        if blacklisted(info.name):
            # Manuals, headers, and docs are not needed in initrd
            continue
        if info.name in existing_dirs:
            # Directory has already been created, skip
            continue
        if info.isdir():
            added_lines.append("dir %s 755 0 0" % info.name)
            continue
        if not info.isfile():
            raise ValueError("Unsupported file type in package %r" % info.name)
            
        target = os.path.join(initrd, info.name)
        if not os.path.exists(target):
            tf.extract(info, path=initrd, set_attrs=False)
        added_lines.append("file %s %s 755 0 0" % (info.name, target))
    extra = "\n".join(added_lines)+"\n"
    open(spec, "a").write(extra)


def add_file_to_initrd(initrd_root, path, data):
    cfg = get_config()
    initrd = os.path.join(cfg["TEMP_DIR"], initrd_root)
    spec = initrd + ".spec"
    added_lines = []
    target = os.path.join(initrd, path)
    open(target, "wb").write(data)
    extra = "file %s %s 755 0 0\n" % (path, target)
    print("writing to %r" % spec)
    open(spec, "a").write(extra)


def install(package, initrd_root):
    cfg = get_config()
    pkg_root = os.path.join(cfg["TEMP_DIR"], "isofs", "slackware")
    initrd = os.path.join(cfg["TEMP_DIR"], initrd_root)
    rex = re.compile(r"^(?P<name>.*)-(?P<version>.*)-(?P<arch>.*)-(?P<build>.*)\.txz$")
    for root, dirs, names in os.walk(pkg_root):
        for name in names:
            p = os.path.join(root, name)
            m = rex.match(name)
            if m:
                name = m.groupdict()["name"]
                if name == package:
                    print(p)
                    tf = tarfile.open(p)
                    extract(tf, initrd)
                    return


def set_startup_script(initrd_root):
    cfg = get_config()
    initrd = os.path.join(cfg["TEMP_DIR"], initrd_root)
    rc = os.path.join(initrd, "etc/rc.d/rc.S")
    data = open(rc, "rb").read()
    prof = b"\n. /etc/profile\n"
    extra = open("startup.sh", "rb").read()
    data = data.replace(prof, prof+extra, 1)
    open(rc, "wb").write(data)
    


def install_all(initrd):
    for package in open("initrd_packages.txt").read().split():
        print("installing %r" % initrd)
        install(package, initrd)

    set_startup_script(initrd)
    add_file_to_initrd(initrd, "etc/setup.exp", open("setup.exp", "rb").read())


if __name__ == "__main__":
    install_all("_isolinux_initrd.img")

