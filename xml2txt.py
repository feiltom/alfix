#!/usr/bin/python3

import sqlite3
import sys
from lxml import etree
from alfix import mkquery, fetch, mkxform
from alfix import web_base, dbpath

def dofoo(db, xform, row):

    transform = xform[row['TYPE']]
    doc = etree.fromstring(row['VALUE_XML'])
    res = transform(doc, codep='0', cdPath='"./"', linkUrl='""')

    txt = []
    for t in res.getroot().itertext():
        txt.append(t)

    return ' '.join(txt)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        dbpath = sys.argv[1]
    db = sqlite3.connect(dbpath)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute('pragma locking_mode = exclusive')

    xform = mkxform(db)
    sql = mkquery(['select xml.id, element_id, value_xml, section.type',
                   'from xml, element, section',
                   'where element_id=element.id',
                   'and element.section_id = section.id'], order=False)
    rows = fetch(db, sql)

    nrows = len(rows)
    cur = 1

    fixes = []

    for r in rows:
        #print('%d / %d' % (cur, nrows))
        cur += 1
        try:
            txt = dofoo(db, xform, r)
        except etree.XMLSyntaxError:
            #print('BAD DATA id %s:\n%s' % (r['ID'], r['VALUE_XML']))
            continue
        fixes.append((txt, r['ID']))

    c.execute('create index idx on xml(id)')
    c.executemany("update xml set full_text=? where id=?", fixes)
    c.execute('drop index idx')
    c.close()

    
        
    
