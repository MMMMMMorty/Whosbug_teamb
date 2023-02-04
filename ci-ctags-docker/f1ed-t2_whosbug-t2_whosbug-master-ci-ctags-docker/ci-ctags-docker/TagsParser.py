#!/usr/bin/python
# coding=utf-8
import csv

class TagItem:
    def __init__(self, item):
        self.field_name = item[0]
        self.file_name = item[1]
        self.regex_path = item[2]
        self.type_name = item[3]

class ParserCtagsFile:
    """
    use cvs parser ctags's tags file
    """

    fname = ""
    tags = []

    def __init__(self, fname="./tags"):
        self.fname = fname;
        csvf = csv.reader(open(self.fname), delimiter='\t')

        # load the tags file date to mem
        for item in csvf:
            # get ctags file opt
            if item[0][0:6] == '!_TAG_':
                if item[0] == '!_TAG_FILE_FORMAT':
                    self.file_format = item[1]
                elif item[0] == '!_TAG_FILE_SORTED':
                    self.file_sorted = item[1]
                elif item[0] == '!_TAG_PROGRAM_AUTHOR':
                    self.prog_author = item[1]
                elif item[0] == '!_TAG_PROGRAM_NAME':
                    self.prog_name = item[1]
                elif item[0] == '!_TAG_PROGRAM_URL':
                    self.prog_url = item[1]
                elif item[0] == '!_TAG_PROGRAM_VERSION':
                    self.prog_ver = item[1]
                continue

            # get all tags item
            self.tags.append(TagItem(item))

    def get_all(self):
        """
            return all tags
        """
        return self.tags

    def find_all(self, cmp_func):
        """
        find tag item in all tags
        """
        pass

    def __iter__(self):
        return self.tags

    def next(self):
        pass