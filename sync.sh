#! /usr/bin/bash

today=date

echo "Starting the application to download pricesheet for $today"

./scrapper.py

echo "Download for pricesheet completed successfully"

echo "Now initialising git repo"
git init

echo "Now adding files"
git add .

echo "Now adding commit message"
git commit -m "Pricesheet for $today"
