#!/usr/bin/env bash

export DIR=Juliet-DeliveryRadar

mkdir -p $DIR

cp -r .git common database processingController processingThreads videoQueue videoUpload .gitignore .python-version app.py build.sh config.py.template Conventions.md flake.lock flake.nix README.md requirements.txt .envrc $DIR

find $DIR | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

rm -rf $DIR/videoUpload/dist $DIR/videoUpload/node_modules $DIR/processingThreads/assets

tar czvf $DIR.tar.gz --directory=. $DIR

rm -rf $DIR