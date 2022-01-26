#!/bin/bash

for pack in $(ls Packs); do
 if cp -r Packs/$pack/Overwrite/* Packs/$pack/; then 
   echo Packs/$pack/Overwrite
 else
   echo
 fi  
done 
