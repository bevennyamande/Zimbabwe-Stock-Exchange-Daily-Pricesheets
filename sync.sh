#! /usr/bin/bash

#TODO:  use the system date here and set as the variable here
$today = date

echo "Starting the application to download pricesheet for $date"

./scrapper.py

git init
git add .
git commit -m "Pricesheet for $date"
