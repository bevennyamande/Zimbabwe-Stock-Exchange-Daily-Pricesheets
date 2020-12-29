#! /usr/bin/bash
# Author: Beven Nyamande

GIT=`which git`
TODAY=$(date)

echo "Now downloading pricesheet for $TODAY ......"

./scrapper.py

echo "Pricesheet downloaded successfully"

echo "Initialising git repo"
${GIT} init

echo "Now adding files"
${GIT} add --all

echo "Now adding commit message"
${GIT} commit -m "Pricesheet for $TODAY"

${GIT} push
