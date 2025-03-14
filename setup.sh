#!/bin/bash

function error()
{
    echo "error: $*"
    exit 1
}

[ -z "$1" ] && error "usage: $0 <path-to-cdimage>"

cdpath="$(realpath "$1")"

[ -e "${cdpath}"/elearn.ico ] || error "${cdpath}: not an elearn image"

mkdir app

echo "extracting data..."
innoextract -s -I app/Web "${cdpath}/setup.exe"
find app/ -name "*.xsl" -o -name "*.ehtm" -o -name "*.css" -o -name "*.js"|xargs dos2unix -q
find app/ -name "*.xsl" -o -name "*.ehtm" -o -name "*.css" -o -name "*.js"| xargs perl -pi -e "s:\\\:/:g"

cddev=$(stat --format "%D" "${cdpath}")
mydev=$(stat --format "%D" .)

echo "copying images..."
cp -a "${cdpath}/Image" app/Web/
mv app/Web/Image app/Web/image

ln -s ../../../alfix.css app/Web/css/

perl -pi -e "s:a.getDocumentElement\(\):a.documentElement:g" app/Web/svgscript/mysvg.js

./mdb2sql.sh "$cdpath"
