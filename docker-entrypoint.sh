#!/bin/bash
set -e


if [[ $# -eq 0 ]] ; then
    echo 'No option given'
    exit 1
fi

for arg in "$@"
do
    case "$arg" in
        scheduler)
            python produce.py scheduler
            ;;
        worker)
            python produce.py worker
            ;;
        consumer)
            python consume.py
            ;;
        *)
            echo "Not valid choice"
            ;;
    esac
done