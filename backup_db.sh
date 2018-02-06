#!/usr/bin/env bash
YESTERDAY=$(perl -e 'use POSIX;print strftime "%Y_%m_%d",localtime time-86400;')
DATE=`date +"%Y-%m-%d_%H-%M-%S"`
DB_NAME="finance.db"
BACKUP_DB_NAME="backup/finance_${DATE}.db"
echo Backing up $DB_NAME.
if [ -f $BACKUP_DB_NAME ]
then
	echo $BACKUP_DB_NAME already exists.
else
	cp $DB_NAME $BACKUP_DB_NAME
	if [ ! -f $BACKUP_DB_NAME ]
	then
		echo "File was not backed up successfully."
		exit 1
	else
		echo "File backed up successfully to $BACKUP_DB_NAME."
	fi
fi
