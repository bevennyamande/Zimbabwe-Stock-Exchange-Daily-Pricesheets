#! /usr/bin/bash
# Author: Beven Nyamande

GIT=`which git`
TODAY=$(date)
# REPO=`/root/werkzeug/projects/Scrapper/.git/`
# echo ${REPO}

echo "Starting the application to download pricesheet for $TODAY"

./scrapper.py

echo "Download for pricesheet completed successfully"

echo "Now initialising git repo"
${GIT} init

echo "Now adding files"
${GIT} add --all

echo "Now adding commit message"
${GIT} commit -m "Pricesheet for $TODAY"
