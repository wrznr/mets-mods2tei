# -*- coding: utf-8 -*-

from lxml import etree

import os

ns = {
     'mets': "http://www.loc.gov/METS/",
     'mods': "http://www.loc.gov/mods/v3",
     'xlink' : "http://www.w3.org/1999/xlink",
}
METS = "{%s}" % ns['mets']
XLINK = "{%s}" % ns['xlink']

class Mets:

    def __init__(self):
        """
        The constructor.
        """

        self.tree = None
        self.title = None
        self.sub_titles = None
        self.authors = None
        self.editors = None
        self.places = None

    @classmethod
    def read(cls, source):
        """
        Reads in METS from a given (file) source.
        :param source: METS (file) source.
        """
        if hasattr(source, 'read'):
            return cls.fromfile(source)
        if os.path.exists(source):
            return cls.fromfile(source)

    @classmethod
    def fromfile(cls, path):
        """
        Reads in METS from a given file source.
        :param str path: Path to a METS document.
        """
        i = cls()
        i.__fromfile(path)
        return i

    def __fromfile(self, path):
        """
        Reads in METS from a given file source.
        :param str path: Path to a METS document.
        """
        self.tree = etree.parse(path)
        self.__spur()

    def __spur(self):
        """
        Initial interpretation of the METS/MODS file.
        """
        # TODO: Check whether the first dmdSec always refers to the volume title,
        # alternatively identify the corresponding dmdSec via <structMap type="Logical" />

        #
        # main title
        self.title = self.tree.xpath("//mets:dmdSec[1]//mods:mods/mods:titleInfo/mods:title", namespaces=ns)[0].text

        #
        # sub titles
        self.sub_titles = [text.text for text in self.tree.xpath("//mets:dmdSec[1]//mods:mods/mods:titleInfo/mods:subTitle", namespaces=ns)]

        #
        # authors and editors
        self.authors = []
        self.editors = []
        for name in self.tree.xpath("//mets:dmdSec[1]//mods:mods/mods:name", namespaces=ns):
            person = {}
            typ = name.get("type", default="unspecified")
            for name_part in name.xpath("mods:namePart", namespaces=ns):
                person[name_part.get("type", default="unspecified")] = name_part.text

            # either author or editor
            roles = name.xpath("mods:role/mods:roleTerm", namespaces=ns)
            # TODO: handle the complete set of allowed roles
            for role in roles:
                if role.text == "edt":
                    self.editors.append((typ, person))
                elif role.text == "aut":
                    self.authors.append((typ, person))
        #
        # publication places
        self.places = []
        for place in self.tree.xpath("//mets:dmdSec[1]//mods:mods/mods:originInfo[1]/mods:place", namespaces=ns):
            place_ext = {}
            for place_term in place.xpath("mods:placeTerm", namespaces=ns):
                typ = place_term.get("type", default="unspecified")
                place_ext[typ] = place_term.text
            self.places.append(place_ext)

    def get_main_title(self):
        """
        Returns the main title of the work.
        """
        return self.title

    def get_sub_titles(self):
        """
        Returns the main title of the work.
        """
        return self.sub_titles

    def get_authors(self):
        """
        Returns the author of the work.
        """
        return self.authors

    def get_places(self):
        """
        Returns the place(s) of publication
        """
        return self.places