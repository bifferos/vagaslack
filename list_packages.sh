#!/bin/sh

source ./includes.sh

cat $TEMP_DIR/isofs/slackware*/$1/tagfile | grep ":ADD"

