#!/bin/bash

pname=alfix
langid="${2:-2}"
cdpath="$1"
dbfile="app/${pname}.db"
mdb="${cdpath}/database/eLearn_${langid}.dat"

# create the db
echo "creating schema..."
mdb-schema --no-relations "${mdb}" sqlite | sqlite3 "${dbfile}"

# import db contents
for mdb in ${cdpath}/database/eLearn_${langid}.dat; do
    echo "importing database $(basename ${mdb})"...
    for table in $(mdb-tables "${mdb}"); do
	    echo "  importing table ${table}"
	    f=$(mktemp)
	    mdb-export -H -d '|' "${mdb}" "${table}" > "${f}"
	    dos2unix -q "${f}"
	    sqlite3 "${dbfile}" ".mode csv" ".separator |" ".import ${f} ${table}"
	    rm -f ${f}
    done
    echo "done"
done

echo "regenerating searchable text..."
./xml2txt.py ${dbfile}
echo "done"
