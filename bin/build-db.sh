#!/usr/bin/bash

#fileToDocument="boot/lib/file.js"
fileToDocument="$1"

fileDirname=`dirname "$fileToDocument"`

if [ ! -f $FILE ]; then
	echo "$fileToDocument : file does not exist"
	exit
fi

# Create parent directories
mkdir -p "../db/$fileDirname"

# Generate docs using dox
dox --raw < "../../symbiose/$fileToDocument" > "../db/$fileToDocument"
