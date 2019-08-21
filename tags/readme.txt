Each .skp file represents a disk set.  Packages named in the disk set file will
*not* be installed.  An empty .skp file means all packages in that series
will be installed.  A non-existent .skp file means no packages in that disk set
will be installed.

Each subdirectory contains additional, supplementary .skp files in each disk set that
apply depending on the name of the ISO.

The kernel is required to compile the guest additions.
VBoxLinuxAdditions.run requires perl, bzip2, /l/gc-7.4.2- libffi, libunistr, libmpc, dbus
