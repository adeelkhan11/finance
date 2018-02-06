#!/usr/bin/env bash

DATE=`date +"%Y-%m-%d"`
TIME=`date +"%H-%M-%S"`
echo $DATE $TIME
#exit
for path in `ls -tr data/*.csv`
do
    ./load.py "$path"
    RESULT=$?
    if [ $RESULT -ne 0 ]
    then
        echo "Error processing $path"
        exit 1
    fi
    file=`basename "$path"`
    echo "mv $path archive/$file"
    mv "$path" "archive/$file"
done
