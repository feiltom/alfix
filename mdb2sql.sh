#!/bin/bash

pname=alfix
langid="2"
cdpath="$1"
dbfile="app/${pname}.db"
mdb="${cdpath}/database/elearn_${langid}.dat"

# create the db
echo "creating schema..."
mdb-schema --no-relations "${mdb}" sqlite | sqlite3 "${dbfile}"

# import db contents
for table in $(mdb-tables "${mdb}"); do
	echo "importing table ${table}"
	f=$(mktemp)
	mdb-export -H -d '|' "${mdb}" "${table}" > "${f}"
	dos2unix -q "${f}"
	sqlite3 "${dbfile}" ".mode csv" ".separator |" ".import ${f} ${table}"
	rm -f ${f}
done

echo "done"
