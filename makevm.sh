#!/bin/sh

source ./includes.sh

VBoxManage controlvm $VM_NAME poweroff
VBoxManage unregistervm $VM_NAME --delete

VBoxManage createvm --name $VM_NAME --register
VBoxManage modifyvm $VM_NAME --memory 1024
VBoxManage modifyvm $VM_NAME --audio none
VBoxManage modifyvm $VM_NAME --nic1 nat
VBoxManage modifyvm $VM_NAME --boot1 dvd
VBoxManage modifyvm $VM_NAME --graphicscontroller vmsvga
VBoxManage storagectl $VM_NAME --name IDE --add ide
VBoxManage createmedium disk --filename disk.vdi --size 20480
VBoxManage storageattach $VM_NAME --storagectl IDE --port 0 --device 0 --type hdd --medium disk.vdi
VBoxManage storageattach $VM_NAME --storagectl IDE --port 1 --device 0 --type dvddrive --medium generated.iso
VBoxManage modifyvm $VM_NAME --uart1 0x3f8 4 --uartmode1 server $VBOX_SOCKET
