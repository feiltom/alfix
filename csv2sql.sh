#!/bin/bash

pname=alfix
langid="1"
cdpath=$1
mdb=${cdpath}/database/elearn_${langid}.dat
dbfile=app/${pname}.db

# create the db
echo "creating schema..."
mdb-schema ${mdb} | sed -e 's:Memo/Hyperlink:Text:g' | sqlite3 ${dbfile}

# import db contents
for table in $(mdb-tables ${mdb}); do
	echo "importing table ${table}"
	sqlite3 ${dbfile} ".mode csv" ".separator |" ".import csv/${pname}-${table}.csv ${table}"
done

echo "done"
