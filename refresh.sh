#!/usr/bin/env bash
blog () {
	echo "$(date +'%Y-%m-%d %H:%M:%S')  $@"
}

run_safe () {
	blog "Running: $@"
    "$@"
    result=$?
    if [ $result -ne 0 ]
    then
        blog "Error: exited with code $result."
        exit 1
    fi
}

run_safe ./backup_db.sh
run_safe ./getfiles.sh
#run_safe python generatetran.py Abbu Loan "Ukhan It"
run_safe ./loadfiles.sh
#run_safe python calcinterest.py Abbu Loan
run_safe ./calcbalance.py
run_safe ./categorise.py
#run_safe rm balint.csv
#run_safe python extractbalances.py --fromdate 2014-04-01 balint.csv
