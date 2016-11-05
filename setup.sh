#!/bin/bash

function error()
{
    echo "error: $*"
    exit 1
}

[ -z "$1" ] && error "usage: $0 <path-to-cdimage>"

cdpath="$(realpath "$1")"

[ -e "${cdpath}"/elearn.ico ] || error "${cdpath}: not an elearn image"

mkdir app csv
./mdb2csv.sh "$cdpath"
./csv2sql.sh "$cdpath"

innoextract -s -I app/Web "${cdpath}/setup.exe"
find app/ -name "*.xsl" -o -name "*.ehtm" -o -name "*.css" -o -name "*.js"|xargs dos2unix

cddev=$(stat --format "%D" "${cdpath}")
mydev=$(stat --format "%D" .)

if [ "${cddev}" = "${mydev}" ]; then
    echo "Linking images..."
    cp -as "${cdpath}/image" app/Web/
else
    echo "Copying images..."
    cp -a "${cdpath}/image" app/Web/
fi

ln -s ../../../alfix.css app/Web/css/
