#! /bin/bash
source "venv/bin/activate"
tree -I venv > tree.md
find . -name "*:Zone.Identifier" -type f -delete
find . -name "*.DS_Store" -type f -delete








