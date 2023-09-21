#!/bin/sh

echo "Preparing config files..."

config_files="application.json database.json"

for config_file in ${config_files}
do
    if [ ! -f config/$config_file ]
    then
        echo "Creating config/$config_file"
        cp config/devel-$config_file config/$config_file
    fi
done
