#!/bin/sh

source ./includes.sh

rm -f $VM_NAME.box
vagrant package --base $VM_NAME --OUTPUT $VM_NAME.box
