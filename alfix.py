#!/usr/bin/python3


import sqlite3
import http.server
import socketserver
import socket
import gzip
from lxml import etree
from lxml import html
from lxml.html import builder as E
from urllib.parse import urlparse, parse_qsl

from http import HTTPStatus

myname = 'Alfix'
lcname = myname.lower()
dbpath='app/%s.db' % lcname
web_base = 'app/Web/'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetch(db, sql, as_dict=False):
    if as_dict:
        db.row_factory = dict_factory
    else:
        db.row_factory = sqlite3.Row

    c = db.cursor()
    c.execute(sql)
    rows = c.fetchall()
    c.close()
    return rows

def codename(e):
    keys = ['CODE', 'NAME']
    r = []
    for k in keys:
        if k in e.keys():
            r.append(e[k])
    if 'CODEP_NAME' in e.keys():
        r.append('(%s)' % e['CODEP_NAME'])
    return ' '.join(r)

def mkquery(sql, order=True):
    if order:
        sql.append('order by orders')
    return ' '.join(sql)

def mkpage(title):
    html = E.HTML(
             E.HEAD(
               E.TITLE(title, id='title'),
               E.LINK(rel='stylesheet', href='css/%s.css' % lcname, type='text/css'),
             ),
             E.BODY(
               E.TABLE(
                 E.TR(
                   E.TD(E.A(E.CLASS('menutxt'), myname, href='/'), id='logobar'),
                   E.TD('', id='menubar'),
                   id='toprow',
                 ),
                 E.TR(
                   E.TD(E.CLASS('labeltxt'), '', id='model'),
                   E.TD(E.CLASS('labeltxt'), '', id='path'),
                   id='pathrow',
                 ),
                 E.TR(
                   E.TD(id='sections'),
                   E.TD(id='contents'),
                 ),
                 id='maintable',
               ),
             ),
           )
    return html

class myServer(socketserver.TCPServer):
    def server_bind(self):
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

class myHandler(http.server.SimpleHTTPRequestHandler):

    db = sqlite3.connect(dbpath)
    part = 'models'

    def do_href(self, val):
        qs = []
        for k in ['production', 'validity', 'language']:
            if not k in self.q:
                continue
            qs.append('%s=%s' % (k, self.q[k]))
        qs.append(val)
        return self.p.path + '?&' + '&'.join(qs)

    def do_elements(self, target, elements, what='elemid', cls=''):
        td = self.page.get_element_by_id(target)
        table = E.TABLE()
        for e in elements:
            row = E.TR(
                    E.TD(E.CLASS(cls),
                      E.A(E.CLASS(cls), '%s' % (codename(e)),
                          href=self.do_href('%s=%s' % (what, e['ID'])))
                    )
                  )
            table.append(row)
        td.append(table)

    def refnodefix(self, link):
        if link.startswith('REFNODEID'):
            return self.do_href(link.replace('REFNODEID', 'elemid='))
        else:
            return link

    def element_view(self, q):
        sql = mkquery([
            'select * from xml',
            'where element_id=%s' % q.get('elemid'),
            'and', '(all_validity = 1 or id in (',
                'select xml_id from xml_validity',
                'where validity_id=%s' % q.get('validity'),
                '))',
            'and', '(all_production = 1 or id in (',
                'select xml_id from xml_production',
                'where production_id=%s' % q.get('production'),
                '))',
            'and', 'language_id = %s' % q.get('language')
        ])

        xsql = mkquery([
                'select xsl from xsl',
                'where section_type in (',
                    'select section.type from section, element',
                    'where element.section_id=section.id',
                    'and element.id=%s)' % q.get('elemid')
        ], order=False)
        xslpath = fetch(self.db, xsql)[0]['XSL']

        xslt_root = etree.parse(open('%s/%s' % (web_base, xslpath)))

        # XXX hack: lxml barfs on some javascript thing from xslt, drop it
        for x in xslt_root.xpath('//script'):
            x.getparent().remove(x)

        transform = etree.XSLT(xslt_root)

        contents = self.page.get_element_by_id('contents')
        for i in fetch(self.db, sql):
            doc = etree.fromstring(i['VALUE_XML'])
            res = transform(doc, codep='0', cdPath='"./"', linkUrl='""')
            tbl = res.find('//table')
            contents.append(tbl)


        if self.page.find_class('electrical'):
            # add back the script we nuked in the above
            contents.append(E.SCRIPT(language='javascript',
                                     src='./svgscript/mysvg.js'))
            # let the svg use all available space
            for x in self.page.find_class('electrical'):
                del x.attrib['width']
                del x.attrib['height']

        self.page.rewrite_links(self.refnodefix)

    def do_sections(self):
        q = mkquery([ 'select * from element,section',
                      'where root_elem_id = element.id',
                      'and', 'element.language_id = %s' % self.q.get('language')
                    ])
        elements = fetch(self.db, q)

        self.do_elements('sections', elements, cls='menutxt')

    def do_codep(self, e):
        ret = False
        if 'ALL_CODEP' in e.keys() and e['ALL_CODEP'] == 0:
            sql = mkquery([
                    'select name',
                    'from codep',
                    'where codep.id in (',
                        'select codep_id',
                        'from element_codep',
                        'where element_id=%s)' % e['ID']
            ], order=False)
            for r in fetch(self.db, sql):
                e['CODEP_NAME'] = r['NAME']
                ret = True
                break
        return ret

    def do_contents(self, q):
        sql = mkquery([
            'select element.*',
            'from element',
            'where parent_id=%s' % q.get('elemid'),
            'and', '(all_validity = 1 or id in (',
                'select element_id from element_validity',
                'where validity_id=%s' % q.get('validity'),
                '))',
            'and', '(all_production = 1 or id in (',
                'select element_id from element_production',
                'where production_id=%s' % q.get('production'),
                '))',
            'and', 'language_id = %s' % q.get('language')
        ])
        elements = fetch(self.db, sql, as_dict=True)
        for e in elements:
            self.do_codep(e)

        if elements:
            self.do_elements('contents', elements)
        else:
            self.element_view(q)

    def do_selection(self, what):
        q = ['select distinct id, name from %s' % what ]
        if what == 'language':
            # filter out non-installed languages
            q.append('where id in (select distinct language_id from validity)')
        else:
            q.append('where language_id = %s' % self.q.get('language'))
        values = fetch(self.db, mkquery(q, order=False))

        self.do_elements('contents', values, what)

    def do_page(self, ctype, out):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', ctype)
        self.send_header('Content-Length', len(out))
        self.end_headers()

        self.wfile.write(out)

    def do_model(self):
        sql = mkquery([
                'select model.name, validity.name',
                'from model, validity',
                'where model.id = validity.model_id',
                'and validity.id=%s' % self.q.get('validity'),
                'and model.language_id=1',
        ], order=False)
        models = fetch(self.db, sql)
        td = self.page.get_element_by_id('model')

        years = fetch(self.db,
                      'select name from production where id=%s' %
                      self.q.get('production'))

        m = models[0]
        y = years[0][0].replace('da ', '').replace(' a ', '-')
        model_year = '%s %s (%s)' % (m[0], m[1], y)
        td.text = model_year

        title = self.page.get_element_by_id('title')
        title.text = '%s - %s' % (myname, model_year)

    def do_path(self):
        path = self.page.get_element_by_id('path')
        eid = self.q.get('elemid')
        while True:
            rows = fetch(self.db,
                    'select * from element where id=%s' % eid,
                    as_dict=True)
            if len(rows) < 1:
                break
            for r in rows:
                self.do_codep(r)
                z = E.A(E.CLASS('menutxt'), '%s' % (codename(r)),
                        href=self.do_href('elemid=%s' % (r['ID'])))
                if path:
                    path.insert(0, E.A(' > '))
                path.insert(0, z)
                eid = r['PARENT_ID']

    def do_database(self):
        self.page = mkpage(myname)

        if not (self.q.get('language')):
            self.do_selection('language')
        elif not (self.q.get('validity')):
            self.do_selection('validity')
        elif not (self.q.get('production')):
            self.do_selection('production')

        if self.q.get('validity') and self.q.get('production'):
            self.do_model()
            self.do_sections()
            if self.q.get('elemid'):
                self.do_contents(self.q)
                self.do_path()


        out = html.tostring(self.page,
                            pretty_print=True,
                            doctype='<!DOCTYPE html>')
        self.do_page('text/html; charset=utf-8', out)

    def do_image(self):
        try:
            f = gzip.open(self.path)
            # The SVG files specify an undefined &ns_graphs entity on which
            # at least Firefox barfs on. Parsing the SVG file with entity
            # resolving disabled strips off this anomaly.
            parser = etree.XMLParser(resolve_entities=False)
            svg = etree.parse(f, parser=parser)
            out = etree.tostring(svg)
            t = 'image/svg+xml'
        except OSError:
            f = open(self.path, 'rb')
            out = f.read()
            t = 'image/jpeg'
        finally:
            f.close()

        self.do_page(t, out)

    def do_GET(self):
        self.p = urlparse(self.path)


        if self.p.path in [ '/' ]:
            self.q = dict(parse_qsl(self.p.query))
            return self.do_database()
        else:
            self.path = web_base + self.path
            # SVG files are compressed and need some other love too
            if self.guess_type(self.path) == 'application/octet-stream':
                return self.do_image()
            else:
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 8000
    Handler = myHandler
    httpd = myServer((HOST, PORT), Handler)
    print('serving at http://%s:%s' % (HOST, PORT))
    httpd.serve_forever()
