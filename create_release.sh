#!/bin/bash

#while read line; do git checkout develop -- Packs/$line; done < PACK_LIST.txt

while read line
do
    echo "Copying ${line} pack from develop branch"
    git checkout develop -- "Packs/${line}"
done < PACK_LIST.txt

# Run through and generate dependecy tree
# Checkout those packs as well
# Create zip archive in directory on this branch under release version
