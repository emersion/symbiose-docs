#!/usr/bin/bash

fileToDocument="boot/lib/file.js"
#fileToDocument="usr/lib/gtk/widgets.js"
#fileToDocument="usr/lib/empathy/main.js"
#fileToDocument="boot/lib/operation.js"

# Generate docs db
#./build-db.sh "$fileToDocument"
# Render docs
#./build-docs.py "../db/$fileToDocument"

node ./build-docs.js "../../symbiose/$fileToDocument"