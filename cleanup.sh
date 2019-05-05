#!/bin/sh
echo "Deleting cache and binaries\n" &&
find . \( -name '__pycache__' -or -name '*.pyc' \) -delete
