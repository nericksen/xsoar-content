#!/bin/bash

while read line; do git checkout develop -- Packs/$line; done < PACK_LIST.txt
