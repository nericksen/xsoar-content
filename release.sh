#!/bin/bash

for pack in $(ls Packs); do
  if demisto-sdk upload -i Packs/$pack --insecure; then
    echo "$pack was successfully uploaded in full"
  else
    echo "$pack may not have uploaded completely. check details above"
  fi
done
