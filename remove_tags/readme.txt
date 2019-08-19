Each file represents a disk set.  Packages named in the disk set file will
not be installed.  An empty disk set file means all packages in that series 
will be installed.  A non-existent file means no packages in that disk set
will be installed.


The kernel is included because it's needed to compile the guest additions.
VBoxLinuxAdditions.run requires perl, bzip2, /l/gc-7.4.2- libffi, libunistr, libmpc, dbus
