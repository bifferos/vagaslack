#!/bin/sh

source ./includes.sh

vagrant package --base $VM_NAME --OUTPUT $VM_NAME.box
