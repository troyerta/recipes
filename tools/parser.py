
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
so use this to grab EVERYTHING, and the group(0) components to remove the other things

then sub out group(1) of this: (^## Notes\W.*\s*^(?:.*\s)*?)\s*(?:##[^#])
and this of group 1: (^## (?:(?:Ref)|(?:Ack)).*\s^(?:.*\s*)*?)\s*(?:##[^#])
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
A Subsection must have at least 1 item, but the title is optional
"""
class Subsection:
    def __init__( self, items: items = None, title: str = None ):
        self.title = title
        self.items = items

Sections = List[Subsection]

class Multisection:
    def __init__( self, sections: Sections = None ):
        self.sections = sections

    def append_subsection( self, section: Subsection ):
        self.sections.append( section )

def valid( txt ):
    return txt != ""

# Returns the title string, None otherwise
def get_title( txt ):
    ret = None
    match = re.search( r'(?:^# (.*)\s+)', txt, flags=re.MULTILINE )
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
    match = re.search( r'(?:^# .*\s*)(^(?:<.+>\s*?)*?)\s*(?:##[^#])', txt, flags=re.MULTILINE )
    ret_title = None
    ret_link = None
    title = None
    link = None
    if match:
        assert( valid( match.group(1) ) )
        # TODO: Read lines and return a tuple
        link_section = match.group(1)
        link_data_match = re.search( r"<(?:.*title\s*=\s*\")(.+)(?:\"\s*src\s*=\s*\")(.*)(?:\"\s*>)", link_section, flags=re.MULTILINE )
        title_match = re.search( r"(?:<.*title\s*=\s*\")([^\"]*)", link_section, flags=re.MULTILINE )
        link_match = re.search( r"(?:<.*src\s*=\s*\")([^\"]*)", link_section, flags=re.MULTILINE )

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

    if re.search( r'(?:^## Overview\s+)', txt, flags=re.MULTILINE ):
        ov_lines_blk_match = re.search( r'(?:^## Overview\s+)(^(?:.*\s*?)*?)\s*(?:##[^#])', txt, flags=re.MULTILINE )

        if ov_lines_blk_match:
            lines = ov_lines_blk_match.group(1).splitlines()
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

#
def get_ingredients( txt ):
    pass


def get_method( txt ):
    pass

def get_notes( txt ):
    ret = None
    notes_lines_blk_match = None
    filled_lines = list()
    final_lines = list()

    if re.search( r'(?:^## Notes\s+)', txt, flags=re.MULTILINE ):
        notes_lines_blk_match = re.search( r'(?:^## Notes\s*)(^(?:.*\s)*?)\s*(?:##[^#])', txt, flags=re.MULTILINE )

        if notes_lines_blk_match:
            lines = notes_lines_blk_match.group(1).splitlines()
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


def get_reference( txt ):
    match = re.search( r'(?:^## (?:(?:Ref)|(?:Ack)).*\s*)(^(?:.*\s)*?)\s*(?:##[^#])', txt, flags=re.MULTILINE )
    title = None
    link = None
    if match:
        assert( valid( match.group(1) ) )
        details_match = re.search( r'^(?:\[(.*)\])(?:\((.*)\))$', match.group(1), flags=re.MULTILINE )
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
