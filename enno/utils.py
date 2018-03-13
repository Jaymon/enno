# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, ProcessingInstruction, Doctype

from .compat import *


class TypeList(list):
    """A list that runs type() on an item on entry into the list

    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    def __init__(self, type, iterable=None):
        self.type = type
        if not iterable: iterable = []
        super(TypeList, self).__init__()
        self.extend(iterable)

    def append(self, item):
        super(TypeList, self).append(self.type(item))

    def extend(self, iterable):
        super(TypeList, self).extend(self.type(item) for item in iterable)

    def __setitem__(self, k, item):
        item = self.type(item)
        super(TypeList, self).__setitem__(k, item)

    def insert(self, i, item):
        item = self.type(item)
        super(TypeList, self).insert(i, item)


class Tree(object):
    """
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/bs4/__init__.py
    """
    def __init__(self, soup):
        self.soup = soup

    def tags(self):
        try:
            for ch in self.soup.children:
                if isinstance(ch, (ProcessingInstruction, Doctype, BeautifulSoup)):
                    continue

                elif isinstance(ch, Tag):
                    yield ch
                    t = type(self)(ch)
                    for gch in t.tags():
                        yield gch

        except AttributeError:
            pass


    def normalize_html_whitespace(self, s):
        """
        https://medium.com/@patrickbrosset/when-does-white-space-matter-in-html-b90e8a7cdd33
        https://www.w3.org/TR/CSS21/text.html#white-space-model
        https://www.w3.org/TR/CSS21/visuren.html#inline-formatting
        """
        s = re.sub("^\s+", " ", Plain(s), re.M)
        s = re.sub("[\r\n\t]+", " ", s)
        s = re.sub("\s+", " ", s)
        return s


    def plain(self):
        strings = []
        is_pre = False
        if isinstance(self.soup, Tag) and not isinstance(self.soup, BeautifulSoup):
            is_pre = self.soup.name == "pre"

        # this is basically a pre-order tree traversal
        # https://en.wikipedia.org/wiki/Tree_traversal
        for e in self.soup.children:
            if isinstance(e, (ProcessingInstruction, Doctype)):
                continue

            elif isinstance(e, NavigableString):
                if not Plain(e).isspace():
                    if is_pre:
                        string = e

                    else:
                        string = self.normalize_html_whitespace(e)
                        if strings:
                            if strings[-1].endswith(" "):
                                string = string.lstrip()
                        else:
                            string = string.lstrip()

                    strings.append(string)

            elif isinstance(e, Tag):
                t = type(self)(e)
                string = t.plain()
                is_pre = is_pre or e.name == "pre"
                if not is_pre:
                    if strings:
                        if strings[-1].endswith(" "):
                            string = string.lstrip()
                    else:
                        string = string.lstrip()

                strings.append(string)

                if e.name in HTML.BLOCK_ELEMS:
                    strings.append("\n")

        return "".join(strings)


class Plain(unicode):
    def __new__(cls, val, encoding="UTF-8"):
        if not encoding:
            encoding = sys.getdefaultencoding()

        if is_py2:
            if isinstance(val, str):
                val = val.decode(encoding)

        instance = super(Plain, cls).__new__(cls, val)
        instance.encoding = encoding
        return instance

    def plain(self):
        return type(self)(self)

    def html(self):
        lines = []
        for line in self.splitlines(False):
            lines.append("<p>{}</p>".format(line))
        return HTML("\n".join(lines))

    def enml(self):
        """http://dev.evernote.com/doc/articles/enml.php"""
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        lines.append('<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">')
        lines.append("<en-note>")

        for line in self.splitlines(False):
            if line.isspace():
                lines.append("<div><br /></div>")
            else:
                lines.append("<div>{}</div>".format(line))

        lines.append("</en-note>")
        return ENML("\n".join(lines))


class HTML(Plain):

    BLOCK_ELEMS = set([
        "address",
        "article",
        "aside",
        "blockquote",
        "canvas",
        "dd",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "noscript",
        "ol",
        "output",
        "p",
        "pre",
        "section",
        "table",
        "tfoot",
        "ul",
        "video",
    ])

    INLINE_ELEMS = set([
        "a",
        "abbr",
        "acronym",
        "b",
        "bdo",
        "big",
        "br",
        "button",
        "cite",
        "code",
        "dfn",
        "em",
        "i",
        "img",
        "input",
        "kbd",
        "label",
        "map",
        "object",
        "q",
        "samp",
        "script",
        "select",
        "small",
        "span",
        "strong",
        "sub",
        "sup",
        "textarea",
        "time",
        "tt",
        "var",
    ])

    PROHIBITED_ATTRS = set([
        "id",
        "class",
        "onclick",
        "ondblclick",
        "on",
        "accesskey",
        "data",
        "dynsrc",
        "tabindex",
    ])

    PROHIBITED_ELEMS = set([
        "applet",
        "base",
        "basefont",
        "bgsound",
        "blink",
        "body",
        "button",
        "dir",
        "embed",
        "fieldset",
        "form",
        "frame",
        "frameset",
        "head",
        "html",
        "iframe",
        "ilayer",
        "input",
        "isindex",
        "label",
        "layer,",
        "legend",
        "link",
        "marquee",
        "menu",
        "meta",
        "noframes",
        "noscript",
        "object",
        "optgroup",
        "option",
        "param",
        "plaintext",
        "script",
        "select",
        "style",
        "textarea",
        "xml",
    ])

    PERMITTED_ELEMS = set([
       "a",
       "abbr",
       "acronym",
       "address",
       "area",
       "b",
       "bdo",
       "big",
       "blockquote",
       "br",
       "caption",
       "center",
       "cite",
       "code",
       "col",
       "colgroup",
       "dd",
       "del",
       "dfn",
       "div",
       "dl",
       "dt",
       "em",
       "font",
       "h1",
       "h2",
       "h3",
       "h4",
       "h5",
       "h6",
       "hr",
       "i",
       "img",
       "ins",
       "kbd",
       "li",
       "map",
       "ol",
       "p",
       "pre",
       "q",
       "s",
       "samp",
       "small",
       "span",
       "strike",
       "strong",
       "sub",
       "sup",
       "table",
       "tbody",
       "td",
       "tfoot",
       "th",
       "thead",
       "title",
       "tr",
       "tt",
       "u",
       "ul",
       "var",
       "xmp",
    ])

#     @property
#     def title(self):
#         ret = ""
#         soup = self.soup
#         title = self.soup.find("title")
#         if title:
#             ret = "".join(title.strings)
#         return ret

    @property
    def soup(self):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        soup = BeautifulSoup(self, "html.parser")
        return soup

    def enml(self):
        soup = self.soup
        tag = self.soup.find("body")
        if tag is None:
            tag = soup

        t = Tree(tag)
        for elem in t.tags():
            if elem.name in self.PERMITTED_ELEMS:
                for k in elem.attrs.keys():
                    for kn in self.PROHIBITED_ATTRS:
                        if k.startswith(kn):
                            elem.attrs.pop(k)

            elif elem.name in self.PROHIBITED_ELEMS:
                elem.decompose()

            else:
                elem.unwrap()

        if tag.name == "body":
            tag.name = "en-note"
        else:
            head = tag.new_tag("en-note")
            head.contents = tag
            #head.append(tag)
            tag = head
            #tag = tag.wrap(tag.new_tag("en-note"))

        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        lines.append('<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">')
        lines.append(tag.prettify())
        return ENML("\n".join(lines))

    def plain(self):
        soup = self.soup
        elem = Tree(self.soup)
        return elem.plain()

    def html(self):
        return type(self)(self)


class ENML(HTML):
    """Evernote's markup language should be encapsulated in this class

    http://dev.evernote.com/doc/articles/enml.php
    """
    def enml(self):
        return type(self)(self)

    def html(self):
        soup = self.soup
        tag = self.soup.find("en-note")
        if not tag:
            raise ValueError("ENML does not have <en-note> tag")

        lines = []
        for elem in tag.children:
            if isinstance(elem, Tag):
                line = elem.prettify().strip()
            else:
                line = str(elem).strip()

            if line and not line.isspace():
                lines.append(line)

        return HTML("\n".join(lines))


