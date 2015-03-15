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
import os
import tempfile
import shutil
import re

from mwlib.log import Log
from mwlib import advtree, writerbase, odfconf, parser
from mwlib import odfstyles as style
from mwlib.treecleaner import TreeCleaner

from tomd import MarkdownConverter

log = Log('scwriter')

# - func  ---------------------------------------------------
class ScWriter():
    def __init__(self, env):
        self.chapters = []
        self.env = env
        
    def write(self, output):
        
        #self.tmpdir = tempfile.mkdtemp()
        self.tmpdir = '/tmp/tester'
        self.bookdir = os.path.join(self.tmpdir, 'book')
        self.chapters_path = os.path.join(self.bookdir, 'chapters')
        
        # Softcover init
        
        os.chdir(self.tmpdir)
        command = "softcover new book > /dev/null"
        os.system(command)
        
        #log.info(self.env.metabook.items)
        single_chapter = False
        if (len(self.env.metabook.walk("chapters")) == 0):
            single_chapter = True
        
        if (single_chapter):
            for item in self.env.metabook.walk("article"):
                title = item.displaytitle or item.title
                title = title.replace('/','-')
                title = title.replace(' ','_')
                title = title.replace(':','-')
                log.info("Writing article content in file %s" % title)
                
                #print self.env.metabook.wikis[0].baseurl #get_wiki().baseurl
                #print item.wiki.baseurl
                c = MarkdownConverter(item.wiki, os.path.join(self.bookdir, 'images'))
                
                mywiki = item.wiki
                art = mywiki.getParsedArticle(title=item.title,
                                             revision=item.revision)
                c.parse_node(art)
                #print art
                c.add_footnotes()
                cout = c.out
                # Fix Math
                #cout = re.sub(r'\$\$\s?([^\$\$]+)\s?\$\$',r'\[ \1 \]', cout)
                #cout = re.sub(r'\$\$(.*?)\$\$',r'\[ \1 \]', cout)
                cout = re.sub(r'(?s)(?<!\\)\$\$(.*?)(?<!\\)\$\$',r'\[ \1 \]',cout)
                #print cout
                
                # Write content of the chapter to a file
                self.chapters.append('%s.md' % title)
                fi = os.path.join(self.chapters_path, '%s.md' % title)
                open(fi, 'w').write(cout)
        
        #booktxt = "cover\nfrontmatter:\nmaketitle\ntableofcontents\npreface.md\nmainmatter:\n%s" % '\n'.join(self.chapters)
        booktxt = "frontmatter:\nmaketitle\ntableofcontents\nmainmatter:\n%s" % '\n'.join(self.chapters)
        #log.info("babble")
        log.info(booktxt)
        open(os.path.join(self.bookdir, 'Book.txt'), 'w').write(booktxt)
        
        
        log.info('building...')
        os.chdir(self.bookdir)
        os.system("softcover build:pdf -n -q")
        shutil.move(os.path.join(self.bookdir, "ebooks/book.pdf"), output)
        
        
        
def writer(env, output, status_callback):
    s = ScWriter(env)
    s.write(output)
    
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
