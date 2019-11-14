#!/bin/sh

source ./includes.sh


VBoxManage guestcontrol "$VM_NAME" run --username vagrant --password vagrant --exe /bin/ls
