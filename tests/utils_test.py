# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase

import testdata
#from bs4.element import Tag, NavigableString

from enno.utils import HTML, Plain, ENML, Tree


class TreeTest(TestCase):
    def test_traversal(self):
        enml_doc = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
 <p>
  <b>
   The Dormouse's story
  </b>
 </p>
 <p>
  Once upon a time there were three little sisters; and their names were
  <a href="http://example.com/elsie">
   Elsie
  </a>
  ,
  <a href="http://example.com/lacie">
   Lacie
  </a>
  and
  <a href="http://example.com/tillie">
   Tillie
  </a>
  ;
and they lived at the bottom of a well.
 </p>
 <p>
  ...
 </p>
</en-note>"""

        t = Tree(ENML(enml_doc).soup)
        self.assertEqual(3, t.plain().count("\n"))

    def test_plain(self):
        html_doc = "\n".join([
            '<p> 1 2 3 </p>',
            '<pre>',
            '  4 ',
            '  5',
            '  6',
            '</pre>',
        ])
        elem = Tree(HTML(html_doc).soup)
        s = elem.plain()
        self.assertEqual("1 2 3 \n\n  4 \n  5\n  6\n\n", s)

        html_doc = "\n".join([
            '<p> 1 2 3 </p>',
            '<div>',
            '<pre>',
            '  4 ',
            '  <span>5</span>',
            '  6',
            '</pre>',
            '</div>',
        ])
        f = testdata.create_file("foo.html", html_doc)
        elem = Tree(HTML(html_doc).soup)
        s = elem.plain()
        self.assertEqual("1 2 3 \n\n  4 \n  5\n  6\n\n\n", s)

        html_doc = "\n".join([
            '<p>1',
            '  <a href="#">',
            '    <b>2</b> 3',
            '  </a>.',
            '</p>',
            '<p>',
            '  4 ',
            '  <b>5</b>',
            '  6',
            '</p>',
        ])
        f = testdata.create_file("foo.html", html_doc)
        elem = Tree(HTML(html_doc).soup)
        s = elem.plain()
        self.assertEqual("1 2 3 . \n4 5 6 \n", s)

        html_doc = '<p>1 <a href="#"><b>2</b> 3</a>.</p>'
        elem = Tree(HTML(html_doc).soup)
        s = elem.plain()
        self.assertEqual("1 2 3.\n", s)




# class ElementTest(TestCase):
# 
#     def test_plain(self):
#         html_doc = "\n".join([
#             '<p> 1 2 3 </p>',
#             '<pre>',
#             '  4 ',
#             '  5',
#             '  6',
#             '</pre>',
#         ])
#         f = testdata.create_file("foo.html", html_doc)
#         elem = Element(HTML(html_doc).soup)
#         s = elem.plain()
#         self.assertEqual("1 2 3 \n\n  4 \n  5\n  6\n\n", s)
# 
#         html_doc = "\n".join([
#             '<p> 1 2 3 </p>',
#             '<div>',
#             '<pre>',
#             '  4 ',
#             '  <span>5</span>',
#             '  6',
#             '</pre>',
#             '</div>',
#         ])
#         f = testdata.create_file("foo.html", html_doc)
#         elem = Element(HTML(html_doc).soup)
#         s = elem.plain()
#         self.assertEqual("1 2 3 \n\n  4 \n  5\n  6\n \n", s)
# 
#         html_doc = "\n".join([
#             '<p>1',
#             '  <a href="#">',
#             '    <b>2</b> 3',
#             '  </a>.',
#             '</p>',
#             '<p>',
#             '  4 ',
#             '  <b>5</b>',
#             '  6',
#             '</p>',
#         ])
#         f = testdata.create_file("foo.html", html_doc)
#         elem = Element(HTML(html_doc).soup)
#         s = elem.plain()
#         self.assertEqual("1 2 3 . \n4 5 6 \n", s)
# 
#         html_doc = '<p>1 <a href="#"><b>2</b> 3</a>.</p>'
#         elem = Element(HTML(html_doc).soup)
#         s = elem.plain()
#         self.assertEqual("1 2 3.\n", s)
# 
#     def test_blocks(self):
#         html_doc = "\n".join([
#             '<p>1',
#             '  <a href="#">',
#             '    <b>2</b> 3',
#             '  </a>.',
#             '</p>',
#             '<p>',
#             '  4 ',
#             '  <b>5</b>',
#             '  6',
#             '</p>',
#         ])
#         elem = Element(HTML(html_doc).soup)
#         self.assertEqual(3, len(list(elem.blocks())))
# 
#         html_doc = '<p>1 <a href="#"><b>2</b> 3</a>.</p>'
#         elem = Element(HTML(html_doc).soup)
#         self.assertEqual(1, len(list(elem.blocks())))
# 
#         html_doc = "\n".join([
#             "pre1",
#             '<p>1 <a href="#"><b>2</b> 3</a>.</p>',
#             "post1",
#             "<p>4 <b>5</b> 6</p>",
#         ])
#         s = HTML(html_doc)
#         elem = Element(s.soup)
#         self.assertEqual(4, len(list(elem.blocks())))
# 
#         html_doc = "\n".join([
#             "<div>",
#             '  <p>1 <a href="#"><b>2</b> 3</a>.</p>',
#             "  <p>4 <b>5</b> 6</p>",
#             "</div>",
#             "<div>",
#             "  <h1>7</h1>",
#             "</div>",
#         ])
#         s = HTML(html_doc)
#         elem = Element(s.soup)
#         self.assertEqual(3, len(list(elem.blocks())))
# 
#     def test_tree(self):
#         html_doc = """<div>
# <p>1 <a href="#"><b>2</b> 3</a>.</p>
# <p>4 <b>5</b> 6</p>
# </div>
# <div>
# <h1>7</h1>
# </div>"""
# 
# 
#         from bs4.element import Tag, NavigableString
# 
#         s = HTML(html_doc)
#         elem = Element(s.soup)
# 
#         for x in elem.tree():
#             if isinstance(x[1], Tag):
#                 print("{}. {}".format(x[0], x[1].name))
#             else:
#                 print("{}. {}".format(x[0], x[1]))


class StringTest(TestCase):
    def get_html(self):
        html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

        s = HTML(html_doc)
        return s

    def test_unicode(self):
        # if this doesn't fail with a unicode exception then the test passed
        s = Plain(testdata.get_unicode_words())

    def test_enml(self):
        s = self.get_html()
        r = s.enml()
        self.assertTrue("<en-note>" in r)
        self.assertFalse("class=" in r)
        self.assertFalse("id=" in r)

    def test_closing_tag(self):
        html_doc = "<p>1</p><hr><br><p>2</p>"
        s = HTML(html_doc)
        r = s.enml()
        self.assertTrue("<br/>" in r)
        self.assertTrue("<hr/>" in r)
        self.assertFalse("<br>" in r)
        self.assertFalse("<hr>" in r)

    def test_enml_to_html(self):
        s = self.get_html().enml()

        r = s.html()
        self.assertFalse("en-note" in r)
        self.assertFalse("<?xml" in r)
        self.assertFalse("<!DOCTYPE" in r)

    def test_enml_to_plain(self):
        enml_doc = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
 <p>
  <b>
   The Dormouse's story
  </b>
 </p>
 <p>
  Once upon a time there were three little sisters; and their names were
  <a href="http://example.com/elsie">
   Elsie
  </a>
  ,
  <a href="http://example.com/lacie">
   Lacie
  </a>
  and
  <a href="http://example.com/tillie">
   Tillie
  </a>
  ;
and they lived at the bottom of a well.
 </p>
 <p>
  ...
 </p>
</en-note>"""

        r = "\n".join([
            "The Dormouse's story ",
            " ".join([
                "Once upon a time there were three little sisters;",
                "and their names were Elsie , Lacie and Tillie ;",
                "and they lived at the bottom of a well. ",
            ]),
            "... ",
            "",
        ])
        s = ENML(enml_doc)
        self.assertEqual(r, s.plain())

    def test_html_to_plain(self):
        html_doc = """<div>
<p>1 <a href="#"><b>2</b> 3<a>.</p>
<p>4 <b>5</b> 6</p>
</div>"""

        s = HTML(html_doc)
        s.plain()

