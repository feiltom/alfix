#!/bin/bash

pname=alfix
lang_id=2
cdpath="$1"
mdb="${cdpath}/database/elearn_${lang_id}.dat"

for table in $(mdb-tables "${mdb}"); do
	mdb-export -H -d'|' "${mdb}" "${table}" > "csv/${pname}-${table}.csv"
	dos2unix "csv/${pname}-${table}.csv"
done
