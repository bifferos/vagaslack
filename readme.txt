In Brief:
1) Create directory /ram and mount tmpfs on it if you have enough RAM
   otherwise just create it without mounting and chmod 777 /ram

2) pip install initrd, pycdlib, backports.lzma (ensure kernel sources at
   /usr/src/linux)

3) Ensure VirtualBox installed and VBoxManage in path.

4) ./create_iso.py <some slackware iso> 
   Will generate a new install ISO with serial port enabled.  It will also 
   generate tagfiles according to the remove_tags directory contents (see 
   readme.txt in there)

5) Check generated includes.sh for the name of the VirtualBox VM that will be 
   created.  Make sure you don't have a VM called that because it will be 
   deleted.  It also contains the names of other important files.

6) ./makevm.sh to create the VirtualBox vm, deleting any VM with the same
   name.

7) Finally, run ./auto_install.exp to run the install.  This will start the
   VM and run an expect script against the console on serial port.  The
   tagfiles will be followed to perform a minimal install.  At the end of
   the install, before reboot the guest additions will be installed.


Notes:

There is some attempt to detect packages and only expect certian dialogs if
the relevant package is present (e.g. lilo, gpm, networking).  This is very
crude.

If the display freezes, Slackware has probably put an unexpected dialog up.
Put an interact into the expect script a few steps back from where it froze, 
run:

./makevm.sh
./auto_install.exp

The first command will remake the VM.  The second will re-run the
automation.

