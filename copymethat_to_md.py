#!/usr/bin/env python3

import sys
import os
from os.path import abspath, basename, isdir, isfile
import re
import shutil
import subprocess

SRC_PATH = "src/"
SUMMARY_PATH = "src/SUMMARY.md"
TEMPLATE_PATH = "src/template_blank.md"

REGEX_URL = r'^(?:Adapted from )(.*)$'
REGEX_TAGS_LINE = r'^tags: (.*)$'
REGEX_SERVINGS = r'^(?:Servings: )(.*)$'
REGEX_DESCRIPTION_WHEN_NO_TAGS = r'^Adapted from.*$\n+(^.*$\n)'
REGEX_DESCRIPTION_WHEN_TAGS = r'^tags:.*$\n(^.*$\n){2}'
# REGEX_INGRED_SECTION = r'INGREDIENTS\n\n((.*\n)*)^STEPS'
# REGEX_INGRED_SUBSECTION_TITLE = r'^(.*):'
# REGEX_INGRED_SUBSECTION_LIST = r''
# REGEX_INGRED_ITEM = r''
# REGEX_STEPS_SECTION = r''
# REGEX_STEPS_SUBSECTION = r''
# REGEX_STEPS_ITEM = r''

'''
Grab the sub ingred titles, then use
r':\n\n(^\w.*\n)+\n' to match the entire sublist. THen match sure the number of matches are equal


Or grab everything between INGREDIENTS and STEPS with a simple regex and just use this: r'(^\w.*:)\n\n((^\w.*\n)+\n)'
to grab the titles in group 1, and the sublist in group 2.


TO match ORDINARY ingredient lists: just use
r'INGREDIENTS\n\n((.*\n)*)^STEPS'
and the entire list shows up in group 1
'''

''' other things...
match first sublist item (group 1): r':\n\n(^.*)(?<!:\n\n)'
match last sublist item (group 1): r'\n(^.*)(?<!\n)\n\n'
match everything between them: \n((.*\n)+)
match each item with ^(.*)$

THis works pretty good: r'1\/2 cup shredded coconut, toasted\n(^\w.*\n)+\n'
'''

'''
For multi-part steps, this one at least captures the names of the parts and the entire sub-sequence
in groups 1 and 2 respectively: r'(?:STEPS)?\n\n*(\w.*:\n*)((\n\n^\d\).*)+)'
'''

def confirm_title( title ):
    result = title
    while True:
        new_title = input( "Current title is \'" + result + "\'\n\tPress ENTER to confirm\n\t\'q\' to cancel\n\tOr type new title: " )

        if new_title:
            if new_title == 'q':
                result = title
                break
            else:
                result = new_title
        else:
            break
    print("Title:", result)
    return result

def clean_title( title_in ):
    num_temp = re.sub('\d+-', '', os.path.basename( title_in ).title() )
    with_temp = re.sub('With', 'with', num_temp )
    and_temp = re.sub('And', 'and', with_temp )
    u_score_temp = re.sub('_', ' ', and_temp )
    tasty_temp = re.sub('By Tasty', '', u_score_temp )
    recipe_temp = re.sub('Recipe', '', tasty_temp )
    return recipe_temp.strip()

def get_title( first_line_in ):
    return confirm_title( clean_title( first_line_in.strip() ) )

def find_url( data ):
    match = re.search( REGEX_URL, data, flags=re.MULTILINE )
    if match:
        return match.group(1)
    else:
        return None

def find_servings( data ):
    match = re.search( REGEX_SERVINGS, data, flags=re.MULTILINE )
    if match:
        return match.group(1)
    else:
        return None

def find_tags( data ):
    match = re.search( REGEX_TAGS_LINE, data, flags=re.MULTILINE )
    if match:
        line = match.group(1)
        tag_list = line.split(", ")
        return tag_list
    else:
        return None

def find_description( data ):
    # Grab everything between the URL and INGREDIENTS
    match = re.search( r'Adapted from.*\n[\s\S]*?INGREDIENTS', data, flags=re.MULTILINE )
    section = match.group(0)
    # print(section)
    # Remove the things we know could be there
    section = re.sub( r'^(?:Adapted from )(.*)$', r'', section.strip('\n'), flags=re.MULTILINE )
    # print( section )
    section = re.sub( r'^tags: (.*)$', r'', section, flags=re.MULTILINE )
    # print( section )
    section = re.sub( r'^(?:Servings: )(.*)$', r'', section, flags=re.MULTILINE )
    # print( section )
    section = re.sub( r'INGREDIENTS', r'', section, flags=re.MULTILINE )
    # print( section )
    desc = re.search( r'^\w*$', section.strip('\n'), flags=re.MULTILINE )
    # print( desc )
    if desc and desc.group(0) != '':
        return desc.group(0)
    else:
        return None

def workerFunction():
    if len(sys.argv) <= 1:
        print("Please pass in a txt file to convert..")
        sys.exit()

    target_file = sys.argv[1]
    title = ''
    if not isfile( target_file ):
        print("File not found:", target_file )
        sys.exit()

    data = None
    with open( target_file, 'r') as fi:
        title = get_title(  fi.readline() )
        prep_time = '1' #input('Prep Time: ')
        cook_time = '1' #input('Cook Time: ')
        total_time = '1' #input('Total Time: ')

        while True:
            prep_time = input('Prep Time: ')
            cook_time = input('Cook Time: ')
            total_time = input('Total Time: ')
            answer = input( "Enter any key to redo, or Press ENTER to confirm: " )
            if not answer:
                break


        data = fi.read()
        # print(data)

        url_match = find_url( data )
        tags_match = find_tags( data )
        description_match = find_description( data )
        servings_match = find_servings( data )

        # What kind of ingredients section do we have? continuous? broken up?
        if url_match:
            print( "url_match:", "\'" + url_match + "\'" )
        if tags_match:
            print( "tags_match", "\'" + tags_match + "\'" )
        if description_match:
            print( "description_match:", "\'" + description_match + "\'" )
        # print( "description_match:", "\'" + description_match + "\'" )
        if servings_match:
            print( "servings_match:", "\'" + servings_match + "\'" )







        # ingredients_sub_lists =
        # steps_sub_lists =
        # tags =










if __name__ == "__main__":
    workerFunction()
