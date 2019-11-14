#!/bin/sh

source ./includes.sh

VBoxManage modifymedium disk "$DISK_NAME" --compact
