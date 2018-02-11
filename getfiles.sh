#!/usr/bin/env bash
DATE=`date +"%Y-%m-%d"`
TIME=`date +"%H-%M-%S"`
echo $DATE $TIME
#exit
for path in `ls ~/Downloads/*.csv`
do
    file="`basename "$path"`"
    #echo $file
    if [ -f "data/$file" -o -f "archive/$file" ]
    then
        tgtfile=`echo "$file" | sed "s/\(.*\)\.\([^\.]*\)$/\1_${DATE}.\2/"`
        if [ -f "data/$tgtfile" -o -f "archive/$tgtfile" ]
        then
            tgtfile=`echo "$file" | sed "s/\(.*\)\.\([^\.]*\)$/\1_${DATE}_${TIME}.\2/"`
        fi
    else
        tgtfile="$file"
    fi
    echo $tgtfile
    mv "$path" "data/$tgtfile"
done
