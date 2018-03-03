# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString


def html_tree(elem):
    for el in elem:
        if isinstance(el, Tag):
            yield el
            #pout.v(el.name)
            for ele in html_tree(el):
                yield ele

        elif isinstance(el, NavigableString):
            yield el
            #pout.v(type(el))


def html_tags(elem):
    try:
        for ch in elem.children:
            if isinstance(ch, Tag):
                yield ch
                for gch in html_tags(ch):
                    yield gch

    except AttributeError:
        pass


def normalize_html_whitespace(s):
    s = re.sub("^\s+", " ", str(s), re.M)
    s = re.sub("[\r\n\t]+", " ", s)
    s = re.sub("\s+", " ", s)
    return s


class Block(object):
    @property
    def name(self):
        ret = ""
        if self.tag:
            ret = self.tag.name
        return ret

    def __init__(self, tag, contents):
        self.tag = tag
        self.contents = contents


class Element(object):

    def __init__(self, soup):
        self.soup = soup

    def tree(self):
        for index, elem in self._html_tree(self.soup, 0):
            yield index, elem

    def blocks(self):
        block_index = -1
        for index, elem in self.tree():
            if block_index >= 0:
                if index == block_index:
                    block_index = -1
                    yield elem

            else:
                yield elem
                if isinstance(elem, Tag) and elem.name in HTML.BLOCK_ELEMS:
                    block_index = index

    def plain(self):
        strings = []
        for block in self.blocks():
            if isinstance(block, Tag):
                first = True
                is_pre = block.name == 'pre'

                for index, elem in type(self)(block).tree():
                    if isinstance(elem, Tag):
                        if elem.name == 'pre':
                            is_pre = True

                    elif isinstance(elem, NavigableString):
                        if is_pre and 'pre' in set(x.name for x in elem.parents):
                            strings.append(elem.string)

                        else:
                            is_pre = False
                            string = normalize_html_whitespace(elem)
                            if first:
                                string = string.lstrip()
                                first = False

                            if strings:
                                if strings[-1].endswith(" "):
                                    string = string.lstrip()
                            strings.append(string)

                if block.name in HTML.BLOCK_ELEMS:
                    strings.append("\n")

            elif isinstance(block, NavigableString):
                strings.append(normalize_html_whitespace(str(block).strip()))
 
        return "".join(strings)







    def blocks2(self):
        block = None
        contents = []
        block_index = -1
        for index, elem in self.tree():
            if block_index >= 0:
                contents.append(elem)
                if index == block_index:
                    #block = type(self)(contents)
                    block_index = -1

            else:
                if isinstance(elem, Tag) and elem.name in HTML.BLOCK_ELEMS:
                    if contents:
                        yield Block(block, contents)
                        block = None
                        contents = []

                    block = elem
                    block_index = index

                else:
                    contents.append(elem)

        if contents:
            yield Block(block, contents)

    def _html_tree(self, elem, index):
        for el in elem:
            if isinstance(el, Tag):
                yield index, el
                #pout.v(el.name)
                for i, ele in self._html_tree(el, index + 1):
                    yield i, ele

            elif isinstance(el, NavigableString):
                yield index, el
                #pout.v(type(el))

#     def __iter__(self):
#         for elem in self.soup:
#             yield elem

    def plain3(self):
        strings = []
        for element in self.blocks():
            for elem in element.soup[1:]:
                if isinstance(elem, Tag):
                    if elem.name in HTML.BLOCK_ELEMS:
                        element2 = type(self)(elem)
                        for elem2 in element2.blocks():
                            strings.append(elem2.plain())

                else:
                    string = elem.string
                    if string is not None:
                        strings.append(string)

        ret = "".join(strings)
        lines = []
        for line in ret.splitlines(False):
            lines.append(line)
        return "".join(lines)



    def plain2(self):
        strings = []
        for elem in self.soup:
            string = elem.string
            if string is not None:
                strings.append(string)

            if isinstance(elem, Tag):
                if elem.name in HTML.BLOCK_ELEMS:
                    element = type(self)(elem)
                    for el in element.blocks():
                        strings.append(el.plain())

        ret = "".join(strings)
        pout.v(ret)
        lines = []
        for line in ret.splitlines(False):
            lines.append(line)
        return "".join(lines)










# class Soup(BeautifulSoup):
#     def tags(self):
#         def _tags(elem):
#             try:
#                 for ch in elem.children:
#                     if isinstance(ch, Tag):
#                         yield ch
#                         for gch in _tags(ch):
#                             yield gch
# 
#             except AttributeError:
#                 pass
# 
#         for tag in _tags(self):
#             yield tag
# 


# class String(str):
#     def plain(self):
#         raise NotImplementedError()
# 
#     def html(self):
#         raise NotImplementedError()
# 
#     def enml(self):
#         raise NotImplementedError()


class Plain(str):
#     class __new__(cls, s):
#         instance = super(

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

        for elem in html_tags(tag):
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
        # TODO -- convert all <br /> to newlines?

#         for elem in html_tree(soup):
#             if isinstance(el, Tag):
#                 yield el
#                 #pout.v(el.name)
#                 for ele in html_tree(el):
#                     yield ele
# 
#             elif isinstance(el, NavigableString):
#                 pass

        return ""
        return soup.get_text()





        def get_lines(tag):
            ret = []
            for elem in tag.children:
                if isinstance(elem, Tag):
                    if elem.name in self.BLOCK_ELEMS:
                        line = elem.prettify().strip() + "\n"

                    elif elem.name in self.INLINE_ELEMS:
                        line = elem.prettify().strip()

                else:
                    line = str(elem).strip()

                if line and not line.isspace():
                    ret.append(line)
            return ret

        lines = []
        lines.extend(get_lines(soup))
        for sibling in soup.next_siblings:
            lines.extend(get_lines(sibling))

        return Plain("".join(lines))
        #return Plain("".join(soup.strings))

    def html(self):
        return type(self)(self)


class ENML(HTML):
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


