#!/usr/bin/env python

"""
   Copyright (c) Bifferos (bifferos@gmail.com) 2019.
   Permission is given to use this code for any purpose.  Derived works must contain this copyright notice.
"""

import os
import pycdlib
from subprocess import Popen, PIPE
try:
    import lzma
except ImportError:
    from backports import lzma
import gzip
import json
import datetime
import six
import initrd


# The location of any initrd images is specific to each distribution and bootloader.  Since these are simply
# compressed cpio archives it would be expensive to figure out where they are.  Easiest way to deal with them
# Is hard-code the locations.  This list can be exhaustive, if any are missing they'll be ignored.
INITRD_IMAGES = ["/EFI/BOOT/initrd.img", "/isolinux/initrd.img"]


def extract_one_iso_file(iso_in, src, dest):
    local_path = dest + src
    record = iso_in.get_record(rr_path=src)
    if record.is_file():
        if record.rock_ridge is not None and record.rock_ridge.is_symlink():
            local_dir, local_link_name = os.path.split(local_path)
            old_dir = os.getcwd()
            os.chdir(local_dir)
            src = record.rock_ridge.symlink_path()
            dst = local_link_name
            print("symlink: %s -> %s" % (dst, src))
            os.symlink(src, dst)
            os.chdir(old_dir)
        else:
            print("file: %s" % src)
            iso_in.get_file_from_iso(local_path, rr_path=src)


def walk_iso(iso_file, isofs_dir):
    """The main walking mechanism is the first level extractor, it just extracts the files
       and creates any links for iso filesystem
    """
    iso_in = pycdlib.PyCdlib()
    iso_in.open(iso_file)
    iso_out = pycdlib.PyCdlib()
    iso_out.new(joliet=3)
    os.mkdir(isofs_dir)
    for path, dirs, files in iso_in.walk(rr_path="/"):
        for dirname in dirs:
            dst = isofs_dir + os.path.join(path, dirname)
            print("dir %s" % dst)
            os.mkdir(dst)
        for filename in files:
            src = os.path.join(path, filename)
            extract_one_iso_file(iso_in, src, isofs_dir)


def walk_initrd(initrd_path, initrd_dir):
    print("Extracting initrd at %r" % initrd_path)
    spec_data, type_str = initrd.extract(initrd_path, initrd_dir)

    # Write out the spec file
    spec = initrd_dir+".spec"
    open(spec, "wb").write(spec_data)
    # Update the mtime of the spec file to the same as the original initrd file.
    # This will give us a hint if it's been edited when we re-assemble.
    mtime = os.stat(initrd_path).st_mtime
    os.utime(spec, (mtime, mtime))
    return spec, type_str


def extract_all(iso_file, out_dir):
    if os.path.exists(out_dir):
        raise ValueError("Output directory %r exists" % out_dir)
    os.mkdir(out_dir)
    iso_explode_path = "isofs"
    isofs_dir = os.path.join(out_dir, iso_explode_path)
    walk_iso(iso_file, isofs_dir)
    index = {"ISO": iso_explode_path}

    initrds = {}

    for image in INITRD_IMAGES:
        initrd_path = isofs_dir + image
        if not os.path.exists(initrd_path):
            print("Skipping initrd path %r, doesn't exist" % initrd_path)
            continue
        escaped = image.replace("/", "_")
        initrd_dir = os.path.join(out_dir, "%s" % escaped)
        os.mkdir(initrd_dir)
        spec, type_str = walk_initrd(initrd_path, initrd_dir)
        initrds[escaped] = (image, spec, type_str)

    index["initrds"] = initrds
    # Finally, make a dictionary to find everything.
    index_path = os.path.join(out_dir, ".index")
    print("Writing index to %s" % index_path)
    with open(index_path, "w") as fp:
        json.dump(index, fp)


def determine_boot(file_path):
    isolinux = os.path.join(file_path, "isolinux")

    if os.path.exists(os.path.join(isolinux, 'efiboot.img')):
        return 'isolinux/efiboot.img'
    
    if os.path.exists(os.path.join(isolinux, 'isolinux.boot')):
        return 'isolinux/isolinux.boot'
        
    raise ValueError("can't determine boot file")



def make_iso_fs(file_path, iso_name):
    iso_rel = os.path.join("..", "..", iso_name)

    command = [
        'mkisofs', '-o', iso_rel, '-R', '-J', '-V', 'explode installer',
        '-hide-rr-moved', '-hide-joliet-trans-tbl',
        '-v', '-d', '-N', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table',
        '-b', 'isolinux/isolinux.bin',
        '-c', 'isolinux/isolinux.boot',
        '-sort', 'isolinux/iso.sort',
        '-preparer', "assemble installer",
        '-publisher', "assemble installer",
        '-A', "Slackware",
        '-eltorito-alt-boot', '-no-emul-boot', '-eltorito-platform', '0xEF'
        ]
    #if os.path.isfile(os.path.join(file_path, "isolinux/efiboot.img")):
    command += ['-eltorito-boot', determine_boot(file_path)]
    command += ["."]
    print(" ".join(command))
    p = Popen(command, shell=False, cwd=file_path)
    p.communicate("")


def most_recent(path):
    """Most recent file in a path"""
    latest = 0
    for root, dirs, names in os.walk(path):
        latest = max([os.stat(os.path.join(root, name)).st_mtime for name in names]+[latest])
    return latest


def assemble_all(dir_path, iso_name):
    if not os.path.isdir(dir_path):
        raise ValueError("dir path doesn't exist")
    meta = json.loads(open(os.path.join(dir_path, ".index"), "rb").read())
    isofs_path = os.path.join(dir_path, meta["ISO"])

    for escaped, actual in six.iteritems(meta["initrds"]):
        output_path = isofs_path + actual[0]
        original_time = os.stat(output_path).st_mtime
        print("Initrd date: %s" % datetime.datetime.fromtimestamp(original_time))
        extracted_time = most_recent(os.path.join(dir_path, escaped))
        spec_time = os.stat(actual[1]).st_mtime
        print("Spec date: %s" % datetime.datetime.fromtimestamp(spec_time))
        latest_time = max(spec_time, extracted_time)
        print("Latest content date: %s" % datetime.datetime.fromtimestamp(extracted_time))
        if latest_time > original_time:
            initrd.gen_init_cpio(actual[1], output_path, actual[2])
            print("Written file %r with %r compression" % (output_path, actual[2]))
        else:
            print("Skipping regeneration of initrd, it's hasn't been modified.")

    make_iso_fs(isofs_path, iso_name)

