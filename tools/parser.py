
"""
Regex notes:

Get recipe title
(?:^# (.*)\s+)

Get the img tag or whatever is between the title line and the next section
(?:^# .*\s*)(^(?:<.+>\s*?)*?)\s*(?:##[^#])

Get the overview section rows in a single group
(?:^## Overview\s+)(^(?:.*\s*?)*?)\s*(?:##[^#])

Get the entire ingredients sections, including blanks rows, and all sub lists of ingredients
(?:^## Ingredients\s+)(^(?:.*\s)*?)\s*(?:##[^#])

# This method capture REQUIRES a '## ' afterwards - otherwise backtracks... need to fix
Get the entire methods section including blank rows, '---' rows, and sub method rows and titles
# Since there might be nothing after this section, just try to remove them after grabbing the entire methods block
(?:^## Method\s+)(^(?:.*\s*?)*?)\s*(?:##[^#])
Grab everything: (?:^## Method\s+)(^(?:.*\s)+)
so use this to grab EVERYTHING, and the group(0) components to remove the other things

then sub out group(1) of this: (^## Notes\W.*\s*^(?:.*\s)+)
and this of group 1: (^## (?:(?:Ref)|(?:Ack)|?:Adap).*\s^(?:.*\s*)+)
and finally this group 1: (^## Tags\W.*\s*^(?:.*\s)+)


Get the Note section rows, including any blank lines
(?:^## Notes\s*)(^(?:.*\s)*?)\s*(?:##[^#])

Get the reference section, if it is named with "References" or with "Acknowledgements"
(?:^## (?:(?:Ref)|(?:Ack)).*\s*)(^(?:.*\s)*?)\s*(?:##[^#])

Get the tags section, including any blank lines. Must be last section
(?:^## Tags\s*)(^(?:.*\s)*)
"""

import re
from typing import List

items = List[str]

"""
Functions that "perfectly" extract recipe info from md files
"""

"""
A sublist must have at least 1 item, but the title is optional
"""
class Sublist:
    def __init__( self, items: items = None, title: str = None ):
        self.title = title
        self.items = items

    def __len__( self ):
        if self.items:
            return len(self.items)
        else:
            return 0

Sections = List[Sublist]

class Section:
    def __init__( self ):
        self.sections = list()

    def append_sublist( self, section: Sublist ):
        self.sections.append( section )

    def num_sublists( self ):
        return len(self.sections)

    def num_items( self ):
        sl = [ sublist for sublist in self.sections ]
        total = 0
        for sl in sl:
            total += len(sl.items)
        return total

def valid( txt ):
    return txt != ""

# Returns the title string, None otherwise
def get_title( txt ):
    ret = None
    match = re.search( r'(?:^# (.*)\s+)', txt, flags=re.M )
    if match and valid( match.group(0) ) and valid( match.group(1) ):
        ret =  match.group(1)
    else:
        assert(match)
        assert(match.group(0))
        assert(match.group(1))
    return ret

# Returns a tuple ("Title", "Link")
# If the img reference section exists, the "link" attribute must be present
# The title attribute is optional
def get_img_link( txt ):
    match = re.search( r'(?:^# .*\s*)(^(?:<.+>\s*?)*?)\s*(?:##[^#])', txt, flags=re.M )
    ret_title = None
    ret_link = None
    title = None
    link = None
    if match:
        assert( valid( match.group(1) ) )
        # TODO: Read lines and return a tuple
        link_section = match.group(1)
        link_data_match = re.search( r"<(?:.*title\s*=\s*\")(.+)(?:\"\s*src\s*=\s*\")(.*)(?:\"\s*>)", link_section, flags=re.M )
        title_match = re.search( r"(?:<.*title\s*=\s*\")([^\"]*)", link_section, flags=re.M )
        link_match = re.search( r"(?:<.*src\s*=\s*\")([^\"]*)", link_section, flags=re.M )

        assert( link_match )
        assert( valid( link_match.group(1) ) )

        if(title_match):
            title = title_match.group(1)
        if(link_match):
            link = link_match.group(1)

        if valid( link ):
            if valid( title ):
                ret_title = title
                ret_link = link
        else:
            assert( valid(link) )
    return ret_title, ret_link

# Returns a list of the lines in the Overview ["Servings: 4", "prep time", "cook time", "total time", .. ]
def get_overview( txt ):
    ret = None
    ov_lines_blk_match = None
    filled_lines = list()
    final_lines = list()

    if re.search( r'(?:^## Overview\s+)', txt, flags=re.M ):
        ov_lines_blk_match = re.search( r'(?:^## Overview\s+)(^(?:.*\s*?)*?)\s*(?:##[^#])', txt, flags=re.M )

        if ov_lines_blk_match:
            lines = ov_lines_blk_match.group(1).splitlines()
            filled_lines = [line for line in lines if line != ""]
            assert( len(filled_lines) > 0 )

            # Strip any bullet points, or number prefixes in the lines
            final_lines = [re.sub( r"\W*\d*\.?\W*(.*)", r"\g<1>", line, flags=re.M) for line in filled_lines]
            assert( len(final_lines) > 0 )

            for line in final_lines:
                assert( len(line) > 0 )
                assert( line != "" )

            ret = final_lines
    return ret

#
def get_ingredients( txt ):
    ret = None
    ing_section = Section()
    in_sublist = False

    # Get all the text under the ingredients header in group 1
    match = re.search( r'(?:^## Ingredients\s+)(^(?:.*\s)*?)\s*(?:##[^#])', txt, flags=re.M )
    if match:
        # Remove and blank/empty lines
        subbed_blanks = re.sub( r"\s*$", r"", match.group(1), flags=re.M )
        ing_txt = subbed_blanks
        ing_lines = subbed_blanks.split('\n')

        # If a recipe starts a sublist, then any ungrouped regular listed items
        # Must come before all the sublists. The sublists must be last in the section.
        for line in ing_lines:
            assert(line != "")
            item_match = re.search( r'^\W\s*([\w].+)$', line, flags=re.M)
            heading_match = re.search( r'^#+\s*([\w].+)$', line, flags=re.M )
            blank_match = re.search( r'^\s*$', line, flags=re.M )
            assert(item_match or heading_match or blank_match)

            # Grab regular items in a simple list
            if item_match and not in_sublist:
                stripped_item = re.sub( r'^\s*([- \*]*\s*)?([\w].+)$', r"\g<2>", item_match.group(1), flags=re.M )
                ing_section.append_sublist( Sublist( items = [item_match.group(1)] ) )
                ret = ing_section
                assert(heading_match is None)
                assert(blank_match is None)

            # Everything after this is in a sublist
            elif heading_match:
                sublist_matches = re.finditer( r'^#+\s*([\w].+)$\s*((?:[-\d\(].*\s*)+)', match.group(1), flags=re.M )
                in_sublist = True
                for subsection in sublist_matches:
                    subsection_items = list()
                    stripped_subsection_title = re.sub( r'^([\w].*?)(\W*)?$', r"\g<1>", subsection.group(1), flags=re.M )
                    for ln in re.split( r'\n', subsection.group(2), 50, flags=re.M ):
                        if ln != "":
                            stripped_item = re.sub( r'^\s*([- \*]*\s*)?([\w].+)$', r"\g<2>", ln, flags=re.M )
                            subsection_items.append(stripped_item)
                            # print(f"{stripped_subsection_title}: {subsection_items}")
                    ing_section.append_sublist( Sublist( items = subsection_items, title = stripped_subsection_title ) )
                    ret = ing_section
                assert(item_match is None)
                assert(blank_match is None)
                break
            elif blank_match:
                assert(item_match is None)
                assert(heading_match is None)
            else:
                assert(False)
    return ret


def get_method( txt ):
    ret = None
    mtd_section = Section()
    in_sublist = False

    assert( mtd_section.num_items() == 0 )

    # Get all the text under the methods header in group 1
    match = re.search( r'(?:^## Method\s+)(^(?:.*\s)+)', txt, flags=re.M )
    assert(match)
    if match:
        # Remove all the sections under the methods section
        # This needs to work even if the recipe is missing each of these sections:
        # Notes, refs and acks, tags
        subbed_notes = re.sub( r"(^## Notes\W.*\s*^(?:.*\s)+)", r"", match.group(1), flags=re.M|re.I )
        subbed_references = re.sub( r"(^## (?:(?:Ref)|(?:Ack)|(?:Adap)).*\s^(?:.*\s*)+)", r"", subbed_notes, flags=re.M|re.I )
        subbed_tags = re.sub( r"(^## Tags\W.*\s*^(?:.*\s)+)", r"", subbed_references, flags=re.M|re.I )

        # Remove any blank lines, and '---' separator lines
        subbed_separators = re.sub( r"^-+$", r"", subbed_tags, flags=re.M )
        subbed_blanks = re.sub( r"\s*$", r"", subbed_separators, flags=re.M )

        method_txt = subbed_blanks
        method_lines = subbed_blanks.split('\n')

        # If a recipe starts a sublist, then any ungrouped regular listed items
        # Must come before all the sublists. The sublists must be last in the section.
        for line in method_lines:
            assert(line != "")
            item_match = re.search( r'^(?![#\-]+\s+.*)\d*\.* *(.*)$', line, flags=re.M)
            heading_match = re.search( r'^#+\s*(\w.+)$', line, flags=re.M )
            blank_match = re.search( r'^\s*$', line, flags=re.M )
            separator_match = re.search( r'^-+$', line, flags=re.M )
            assert(item_match or heading_match or blank_match or separator_match)

            # Grab regular items in a simple list
            if item_match and item_match.group(1) != "" and in_sublist == False:
                mtd_section.append_sublist( Sublist( items = [item_match.group(1)] ) )
                ret = mtd_section
                assert(heading_match is None)
                assert(blank_match is None)

            # Everything after this is in a sublist
            elif heading_match:
                sublist_matches = re.finditer( r'^#+\s*([\w].+)$\s*((?:[-\d\(\w].*\s*)+)', method_txt, flags=re.M )

                # Dont revisit the header match section - everything else is part of a sublist
                in_sublist = True

                for subsection in sublist_matches:
                    subsection_items = list()
                    stripped_subsection_title = re.sub( r'^[^a-zA-Z#]+\d*\s*(.*)$', r"\g<1>", subsection.group(1), flags=re.M )
                    # print(stripped_subsection_title+":")
                    for ln in re.split( r'\n', subsection.group(2).strip(), 50, flags=re.M ):
                        if ln != "":
                            stripped_item = re.sub( r'(?:^[\d\-\.\s]*)(.*)$', r"\g<1>", ln, flags=re.M )
                            if stripped_item != "":
                                subsection_items.append(stripped_item)
                    mtd_section.append_sublist( Sublist( items = subsection_items, title = stripped_subsection_title ) )
                    ret = mtd_section
                assert(item_match is None)
                assert(blank_match is None)
                assert(separator_match is None)
                break
            elif blank_match or separator_match:
                assert(item_match is None)
                assert(heading_match is None)
                pass
            else:
                assert(False)
    return mtd_section

def get_notes( txt ):
    ret = None
    notes_lines_blk_match = None
    filled_lines = list()
    final_lines = list()

    if re.search( r'(?:^## Notes\s+)', txt, flags=re.M ):
        notes_lines_blk_match = re.search( r'(?:^## Notes\s*)(^(?:.*\s)*?)\s*(?:##[^#])', txt, flags=re.M )

        if notes_lines_blk_match:
            lines = notes_lines_blk_match.group(1).splitlines()
            filled_lines = [line for line in lines if line != ""]
            assert( len(filled_lines) > 0 )

            # Strip any bullet points, or number prefixes in the lines
            final_lines = [re.sub( r"\W*\d*\.?\W*(.*)", r"\g<1>", line, flags=re.M) for line in filled_lines]
            assert( len(final_lines) > 0 )

            for line in final_lines:
                assert( len(line) > 0 )
                assert( line != "" )

            ret = final_lines
    return ret


def get_reference( txt ):
    match = re.search( r'(?:^## (?:(?:Ref)|(?:Ack)|(?:Adap)).*\s*)(^(?:.*\s)*?)\s*(?:##[^#])', txt, flags=re.M|re.I )
    title = None
    link = None
    if match:
        assert( valid( match.group(1) ) )
        details_match = re.search( r'^(?:\[(.*)\])(?:\((.*)\))$', match.group(1), flags=re.M )
        if details_match:
            assert( valid( details_match.group(1) ) )
            assert( valid( details_match.group(2) ) )
            title = details_match.group(1)
            link = details_match.group(2)
        else:
            assert( False )
    return title, link


def get_tags( txt ):
    ret = None
    tags_lines_blk_match = None
    filled_lines = list()
    final_lines = list()

    if re.search( r'(?:^## Tags\s+)', txt, flags=re.MULTILINE ):
        tags_lines_blk_match = re.search( r'(?:^## Tags\s*)(^(?:.*\s)*)', txt, flags=re.MULTILINE )

        if tags_lines_blk_match:
            lines = tags_lines_blk_match.group(1).splitlines()
            filled_lines = [line for line in lines if line != ""]
            assert( len(filled_lines) > 0 )

            # Strip any bullet points, or number prefixes in the lines
            final_lines = [re.sub( r"\W*\d*\.?\W*(.*)", r"\g<1>", line, flags=re.MULTILINE) for line in filled_lines]
            assert( len(final_lines) > 0 )

            for line in final_lines:
                assert( len(line) > 0 )
                assert( line != "" )

            ret = final_lines
    return ret
