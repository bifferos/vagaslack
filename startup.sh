
# Format the disk
echo start=2048 | sfdisk /dev/sda

# Run the installer, using expect.
/etc/setup.exp

# Copy additions to root, so it can be run from there.
cp /var/log/mount/extra/VBoxLinuxAdditions.run /mnt/root/

# same with pub key
cp /var/log/mount/extra/vagrant.pub /mnt/root/.


chroot /mnt /bin/bash <<"ENDENDEND"

# Message bus needed for Additions to start.
/etc/rc.d/rc.messagebus start

# Run the 
chmod 755 /root/VBoxLinuxAdditions.run
/root/VBoxLinuxAdditions.run


# Setup vagrant user.
useradd vagrant
mkdir -p /home/vagrant/.ssh
mv /root/vagrant.pub /home/vagrant/.ssh/authorized_keys
chown -R vagrant:users /home/vagrant
chmod 0700 /home/vagrant/.ssh
chmod 0600 /home/vagrant/.ssh/authorized_keys


echo -e "vagrant\nvagrant\nvagrant\n" | passwd vagrant

echo "vagrant ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
echo "UseDNS no" >> /etc/ssh/sshd_config


# Lilo changes for faster boot
cat /etc/lilo.conf | sed s/1200/10/ | sed "s/#compact/compact/" > /etc/lilo.conf_tmp
mv /etc/lilo.conf_tmp /etc/lilo.conf
lilo

ENDENDEND


# power off
poweroff -f


exit
