#!/usr/bin/env python

import os
import six
import sys
import explodeinstaller


def get_vm_name(path):
    name = os.path.splitext(os.path.basename(path))[0]
    name = name.replace("-install-dvd", "-vagrant")
    return name


ISO_PATH = sys.argv[1]
VM_NAME = get_vm_name(ISO_PATH)
VBOX_SOCKET = "/tmp/vbox"
temp_dir = "tmp_dir"
ISO_NAME = VM_NAME + ".iso"


# List of packages to remove from the ISO. None of them are needed for an install to
# Virtualbox.  The kernel is kept only because it's needed to compile the guest additions.
# Set disk set name to a list of packages to exclude.
# Set to None to skip the disk set altogether.  Empty string will include all packages.

# VBoxLinuxAdditions.run requires perl, bzip2, /l/gc-7.4.2- libffi, libunistr, libmpc, dbus
to_remove = {
    "a": "acl btrfs-progs cpio cpufrequtils cryptsetup dialog dosfstools ed efibootmgr "
         "eject elilo elvis floppy genpower gpm gptfdisk grub hdparm infozip inotify-tools "
         "jfsutils kernel-generic lha libcgroup lrzip lvm2 mcelog mdadm minicom mkinitrd mt-st mtx "
         "ncompress ntfs-3g os-prober patch pciutils pcmciautils quota reiserfsprogs rpm2tgz sdparm "
         "sharutils slocate smartmontools splitvt tcsh unarj upower usb_modeswitch usbutils "
         "utempter xfsprogs zoo",
    "ap": "a2ps acct alsa-utils amp ash at bc bpe cdparanoia cdrdao cdrtools cgmanager cups cups-filters "
         "dc3dd ddrescue diffstat diffutils dmapi dmidecode dvd+rw-tools enscript flac ghostscript "
         "ghostscript-fonts-std "
         "ghostscript-fonts gphoto2 groff gutenprint hplip htop ispell itstool jed joe jove ksh93 "
         "libx86 linuxdoc-tools lm_sensors lsof lsscsi lxc lzip madplay man man-pages mariadb mc moc most "
         "mpg123 nano normalize pamixer pm-utils powertop qpdf radeontool rpm rzip sc screen seejpeg "
         "slackpkg soma sox sqlite squashfs-tools sysstat terminus-font texinfo tmux usbmuxd vbetool vim "
         "vorbis-tools workbone xfsdump zsh",
    "d": "bison ccache clisp cmake cscope cvs Cython dev86 distcc doxygen flex "
       "gcc-gfortran gcc-gnat gcc-go gcc-objc gcc-java git gnu-cobol gperf help2man "
       "indent llvm mercurial nasm oprofile p2c pmake rcs ruby scons slacktrack strace "
       "subversion swig yasm",
    "e": None,
    "f": None,
    "k": "",
    "kde": None,
    "kdei": None,
    "l": "ConsoleKit2 GConf LibRaw M2Crypto PyQt QScintilla a52dec aalib adwaita-icon-theme "
       "akonadi alsa-lib alsa-oss alsa-plugins apr apr-util aspell aspell-en "
       "at-spi2-atk at-spi2-core atk atkmm attica audiofile automoc4 babl boost cairo "
       "cairomm chmlib clucene db42 db44 db48 dbus-glib dbus-python dconf dconf-editor "
       "desktop-file-utils djvulibre ebook-tools eigen2 eigen3 elfutils enchant esound exiv2 "
       "expat fftw freetype fribidi fuse gamin gcr gd gdbm gdk-pixbuf2 gegl giflib glade3 glib "
       "glib-networking glib2 glibc glibc-i18n glibc-profile glibmm gmime gmm gmp gnome-keyring "
       "gnome-themes-standard gnu-efi gobject-introspection grantlee gsettings-desktop-schemas "
       "gsl gst-plugins-base gst-plugins-base0 gst-plugins-good gst-plugins-good0 gstreamer " 
       "gstreamer0 gtk+ gtk+2 gtk+3 gtkmm2 gtkmm3 gtkspell gvfs harfbuzz herqq hicolor-icon-theme "
       "hunspell icon-naming-utils icu4c ilmbase iso-codes jasper jemalloc js185 json-c judy " 
       "keybinder keyutils lcms lcms2 libaio libao libarchive libart_lgpl libasyncns libatasmart "
       "libbluedevil libcaca libcanberra libcap libcap-ng libcddb libcdio libcdio-paranoia libcroco "
       "libdbusmenu-qt libdiscid libdvdnav libdvdread libevent libexif libfakekey libglade "
       "libgnome-keyring libgphoto2 libgpod libgsf libical libid3tag libidl libidn libieee1284 "
       "libimobiledevice libiodbc libjpeg-turbo libkarma liblastfm libmad libmcrypt libmcs libmng "
       "libmowgli  libmsn libmtp libnih libnjb libnl libnl3 libnotify libodfgen libogg liboggz "
       "liboil libpcap libplist libpng libproxy libraw1394 librevenge librsvg libsamplerate libsecret "
       "libsigc++ libsigsegv libsndfile libsoup libspectre libssh libssh2 libtasn1 libtermcap libtheora "
       "libtiff libusb libusb-compat libusbmuxd libvisio libvisual libvisual-plugins " 
       "libvncserver libvorbis libvpx libwmf libwmf-docs libwnck libwpd libwpg libxklavier "
       "libxml2 libxslt libyaml libzip loudmouth lzo media-player-info mhash mm mozilla-nss mpfr " 
       "ncurses neon netpbm newt notify-python openexr openjpeg orc pango pangomm parted pcre phonon "
       "phonon-gstreamer pilot-link polkit polkit-gnome polkit-qt-1 poppler poppler-data popt pulseaudio "
       "pycairo pycups pycurl pygobject pygobject3 pygtk pyrex python-pillow qca qimageblitz qjson qt "
       "qt-gstreamer qtscriptgenerator raptor2 rasqal readline redland sbc sdl seamonkey-solibs serf "
       "sg3_utils shared-desktop-ontologies shared-mime-info sip slang slang1 soprano " 
       "sound-theme-freedesktop speexdsp startup-notification strigi svgalib system-config-printer "
       "t1lib taglib taglib-extras tango-icon-theme tango-icon-theme-extras urwid v4l-utils virtuoso-ose "
       "vte wavpack xapian-core zlib",
    "n": "alpine autofs biff+comsat bind bluez bluez-firmware bootp bsd-finger ca-certificates "
       "cifs-utils conntrack-tools crda cyrus-sasl dhcp dirmngr ebtables elm epic5 fetchmail "
       "gnupg2 gnupg gnutils gpa gpgme htdig httpd icmpinfo idnkit iftop imapd inetd ipset "
       "iptraf-ng ipw2100-fw ipw2100-fw irssi iw lftp libassuan libgcrypt libgpg-error libksba "
       "libmbim libmnl libndp libnetfilter_acct libnetfilter_conntrack libnetfilter_cthelper "
       "libnetfilter_cttimeout libnetfilter_log libnetfilter_queue libnfnetlink libnftnl "
       "libqmi libtirpc links lynx mailx mcabber metamail mobile-broadband-provider-info "
       "ModemManager mtr mutt nc ncftp net-snmp netatalk netkit-bootparamd netkit-ftp netkit-ntalk "
       "netkit-routed netket-rsh netkit-rusers netkit-rwall netkit-rwho netkit-timed netpipes "
       "nettle netwatch NetworkManager netwrite newspost nfacct nfs-utils nftables nn obexftp "
       "openldap-client openobex openvpn p11-kit php pidentd pinentry popa3d ppp procmail proftpd "
       "pssh pth rdist rfkill rp-pppoe rpcbind rsync samba sendmail slrn snownews stunnel "
       "tftp-hpa tin trn ulogd uucp vlan vsftpd wireless-tools wpa_supplicant yptools ytalk "
       "zd1211-firmware",
    "t": None,
    "tcl": None,
    "x": None,
    "xap": None,
    "xfce": None,
    "y": None
}


def get_disk_sets(disk_sets_dir):
    """
        Get the list of disk-sets in a distribution, just a count of the directories under slackware64 for now.
    """
    out = []
    parent = disk_sets_dir
    if not os.path.exists(parent):
        parent = os.path.join(temp_dir, "isofs/slackware")
    for item in os.listdir(parent):
        p = os.path.join(parent, item)
        if os.path.isdir(p):
            out.append(item)
    return out


def update_tagfiles(disk_sets_dir):
    """
        Update contents of original tagfiles based on the list of packages to skip.
        There's no point to keep the original tagfiles around as this is all generated.
    """
    for disk_set in get_disk_sets(disk_sets_dir):
        if disk_set not in to_remove:
            continue
        removals = to_remove[disk_set]
        out_tags = []
        p = os.path.join(disk_sets_dir, disk_set, "tagfile")
        print("Updating %r" % p)
        if removals is not None:
            removals = removals.split()
        for line in open(p).readlines():
            name = line.split(":")[0]
            if (removals is None) or (name in removals):
                out_tags.append(name + ":SKP")
            else:
                out_tags.append(name + ":ADD")
        open(p, "wb").write("\n".join(out_tags))


def is_included(name):
    """
        Find if the package is SKP.
    :param name: name of package
    :return: True/False
    """
    for k, v in six.iteritems(to_remove):
        if v is None:
            continue
        if name in v.split():
            return False
    return True


def make_expect_parameters():
    fp = open("includes.exp", "wb")
    fp.write('set VM_NAME "%s"\n' % VM_NAME)
    fp.write('set VBOX_SOCKET "%s"\n' % VBOX_SOCKET)
    mouse = is_included("gpm")
    fp.write('set mouse %s\n' % str(mouse).lower())
    network = to_remove['n'] is not None
    fp.write('set network %s\n' % str(network).lower())
    fp.close()


def make_shell_parameters():
    fp = open("includes.sh", "wb")
    fp.write('VM_NAME=%s\n' % VM_NAME)
    fp.write('VBOX_SOCKET=%s\n' % VBOX_SOCKET)
    fp.write('DISK_NAME=%s.vdi\n' % VM_NAME)
    fp.write('ISO_NAME=%s\n' % ISO_NAME)
    fp.close()



def additions_to_extra():
    """Copy the additions into the extra folder"""
    os.system("iso-read -e VBoxLinuxAdditions.run -i /opt/VirtualBox/additions/VBoxGuestAdditions.iso "
              "-o %s/isofs/extra/VBoxLinuxAdditions.run" % temp_dir)


def vagrant_pub_key_to_extra():
    """Copy the additions into the extra folder"""
    os.system("wget https://raw.githubusercontent.com/hashicorp/vagrant/master/keys/vagrant.pub"
              " -o %s/isofs/extra/vagrant.pub" % temp_dir)


# Adapt a Slackware ISO so it boots over serial port
# And then create a VirtualBox VM to run the ISO.

os.system("rm -rf %s" % temp_dir)

# Extract the ISO
explodeinstaller.extract_all(ISO_PATH, temp_dir)

additions_to_extra()

vagrant_pub_key_to_extra()


disk_sets_dir = os.path.join(temp_dir,"isofs/slackware64")
if not os.path.exists(disk_sets_dir):
    disk_sets_dir = os.path.join(temp_dir, "isofs/slackware")

update_tagfiles(disk_sets_dir)

CFG="tmp_dir/isofs/isolinux/isolinux.cfg"

data = b"serial 0 115200\n" + open(CFG, "rb").read()
data = data.replace("SLACK_KERNEL=huge.s", "SLACK_KERNEL=huge.s console=ttyS0")
data = data.replace("SLACK_KERNEL=hugesmp.s", "SLACK_KERNEL=hugesmp.s console=ttyS0")

open(CFG, "wb").write(data)

explodeinstaller.assemble_all(temp_dir, ISO_NAME)

# Setup parameters for the auto-install expect script:
make_expect_parameters()
make_shell_parameters()
