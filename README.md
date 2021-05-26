## Release Branch

Use the `create_release.sh` script to checkout the Packs specfied in the `PACK_LIST.txt` file.

Once the release branch is populated use the `demisto-sdk upload` command to push the packs to the UAT instance.
This would be the dev instance of the remote repositories feature.

Note you may have to update the environment variables to point to the correct instance.

You can delete the Packs folder before running the release command to generate a clean pull from develop branch.
