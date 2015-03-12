#! /usr/bin/env python

# Copyright (c) 2008-2009, PediaPress GmbH
# See README.rst for additional licensing information.
"""
TODO:
 * add license handling
 * implement missing methods: Imagemap, Hiero, Timeline, Gallery

More Info:
* http://books.evc-cit.info/odbook/book.html
* http://opendocumentfellowship.com/projects/odfpy
* http://testsuite.opendocumentfellowship.com/ sample documents
"""

from __future__ import division

import sys
import odf

from mwlib.log import Log
from mwlib import advtree, writerbase, odfconf, parser
from mwlib import odfstyles as style
from mwlib.treecleaner import TreeCleaner



# - func  ---------------------------------------------------


def writer(env, output, status_callback):
    if status_callback:
        buildbook_status = status_callback.getSubRange(0, 50)
    else:
        buildbook_status = None
    book = writerbase.build_book(env, status_callback=buildbook_status)
    scb = lambda status, progress :  status_callback is not None and status_callback(status=status, progress=progress)
    scb(status='preprocessing', progress=50)
    preprocess(book)
    scb(status='rendering', progress=60)
    w = ODFWriter(env, status_callback=scb)
    w.writeBook(book, output=output)

writer.description = 'PDF (SoftCover)'
writer.content_type = 'application/vnd.oasis.opendocument.text'
writer.file_extension = 'pdf'


# - helper funcs   r ---------------------------------------------------

def preprocess(root):
    #advtree.buildAdvancedTree(root)
    #xmltreecleaner.removeChildlessNodes(root)
    #xmltreecleaner.fixLists(root)
    #xmltreecleaner.fixParagraphs(root)
    #xmltreecleaner.fixBlockElements(root)
    #print"*** parser raw "*5
    #parser.show(sys.stdout, root)
    #print"*** new TreeCleaner "*5
    advtree.buildAdvancedTree(root)
    tc = TreeCleaner(root)
    tc.cleanAll()
    #parser.show(sys.stdout, root)

# ==============================================================================

def main():
    for fn in sys.argv[1:]:

        from mwlib.dummydb import DummyDB
        from mwlib.uparser import parseString
        db = DummyDB()
        input = unicode(open(fn).read(), 'utf8')
        r = parseString(title=fn, raw=input, wikidb=db)
        #parser.show(sys.stdout, r)
        #advtree.buildAdvancedTree(r)
        #tc = TreeCleaner(r)
        #tc.cleanAll()


        preprocess(r)
        parser.show(sys.stdout, r)
        odf = ODFWriter()
        odf.writeTest(r)
        doc = odf.getDoc()
        #doc.toXml("%s.xml"%fn)
        doc.save(fn, True)


if __name__=="__main__":
    main()
