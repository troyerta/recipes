#!/usr/bin/env python3

import sys
import os
from os.path import abspath, basename, isdir, isfile
import re
import shutil
import subprocess

TEMPLATE_PATH = "./template_blank.md"
OUTPUT_PATH = "./drafts/parser_output"

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

# GRAB_ALL_LINES_AFTER_STEPS_IN_GROUP1 = (?:STEPS\n\n)((.*\n)+)

# Then go through this, for each non-blank line, see if it is a regular step, or a substep title
# Format accordingly, add to some list, then move on

'''
Find a numbered line/step, store number in group 1, text in group 2: r'^(\d+)\) (.*)'
Find a substep: r'^(.*:)'

Each line will match one these, so just format it appropriately and then move on
'''
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
        new_title = input( "\nCurrent title is \'" + result + "\'\n\tPress ENTER to confirm\n\t\'q\' to cancel\n\tOr type new title: " )

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
    desc = re.search( r'^.*$', section.strip('\n'), flags=re.MULTILINE )
    # print( desc )
    if desc and desc.group(0) != '':
        return desc.group(0)
    else:
        return None

def format_ingredients_lines( ingredients_section ):

    formatted_output = str()

    for item in ingredients_section:
        section_title_match = re.search( r'(.*:)', item )
        ingredient_match = re.search( r'(.+)', item )

        if section_title_match:
            formatted_output += ( "#### " + section_title_match.group(1) + "\n\n" )
        elif ingredient_match:
            formatted_output += ( '- ' + item + '\n\n' )
        else:
            print("Ingredients section contains unreadable line:", item)
            sys.exit()
    return formatted_output

def format_method_lines( steps_section ):

    formatted_output = str()

    for step in steps_section:
        step_match = re.search( r'^(\d+)\) (.*)', step )
        sub_step_title_match = re.search( r'^(.*:)' , step )

        if step_match:
            formatted_output += ( step_match.group(1) + '. ' + step_match.group(2) + '\n' )
            formatted_output += ("---\n\n")
        elif sub_step_title_match:
            formatted_output += ( "#### " + sub_step_title_match.group(1) + "\n\n" )
        else:
            print("Steps section contains unreadable line")
            sys.exit()
    return formatted_output

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

        prep_time = str()
        cook_time = str()
        total_time = str()

        while True:
            prep_time = input('Prep Time: ')
            cook_time = input('Cook Time: ')
            total_time = input('Total Time: ')
            answer = input( "Enter any key to redo, or Press ENTER to confirm: " )
            if not answer:
                break

        data = fi.read()

        url_match = find_url( data )
        tags_match = find_tags( data )
        description_match = find_description( data )
        servings_match = find_servings( data )

        ingredients_match = re.search( r'^(?:INGREDIENTS\n\n)((.*\n)+)^\nSTEPS', data, flags=re.MULTILINE )
        if ingredients_match:
            all_ingredient_lines = ingredients_match.group(1).splitlines()
            lines_in_ingredients = [line for line in all_ingredient_lines if line != '']
            # Find first alpha-word in each line: r'([a-zA-Z]+).*\n'

        ingredients_text_formatted = format_ingredients_lines( lines_in_ingredients )
        # print( ingredients_text_formatted )

        steps_match = re.search( r'(?:^STEPS\n\n)((.*\n)+)', data, flags=re.MULTILINE )
        if steps_match:
            all_lines = steps_match.group(1).splitlines()
            lines_in_steps = [line for line in all_lines if line != '']

        method_text_formatted = format_method_lines( lines_in_steps )
        # print( method_text_formatted )

    # Make target filename
    filename = os.path.join( OUTPUT_PATH, re.sub(' ', '-', title.lower() ) + ".md" )

    shutil.copy(TEMPLATE_PATH, filename)

    # Read in the template
    with open(filename, 'r') as file :
        filedata = file.read()

    # Replace the target string # REPLACE TEMPLATE VARS WITH SIMPLER STRINGS
    filedata = filedata.replace('Recipe Name', title)
    if url_match:
        filedata = filedata.replace('Link Text', title)
        filedata = filedata.replace('https://www.website.com/Recipes/recipe/', url_match)

    if description_match:
        filedata = filedata.replace('Description', description_match)
    else:
        filedata = filedata.replace('## Description\n\n', '')

    # If Servings string is just a number, append "servings" or "serving" depending on the value
    if servings_match:
        filedata = filedata.replace('- Yield:', '- Yield: ' + servings_match)
    else:
        filedata = filedata.replace('- Yield\n:', '')

    if prep_time:
        filedata = filedata.replace('- Prep Time:', '- Prep Time: ' + prep_time)
    else:
        filedata = filedata.replace('- Prep Time:\n', '')
    if cook_time:
        filedata = filedata.replace('- Cook Time:', '- Cook Time: ' + cook_time)
    else:
        filedata = filedata.replace('- Cook Time:\n', '')
    if total_time:
        filedata = filedata.replace('- Total Time:', '- Total Time: ' + total_time)
    else:
        filedata = filedata.replace('- Total Time:\n', '')

    if tags_match:
        tags_str = '\n'.join(sorted(tags_match))
        filedata = filedata.replace('## Tags\n', '## Tags\n' + tags_str)
    else:
        filedata = filedata.replace('\n## Tags\n\n', '')

    filedata = filedata.replace('- ingredient 1\n', ingredients_text_formatted)

    filedata = filedata.replace('- step 1\n', method_text_formatted)

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)

if __name__ == "__main__":
    workerFunction()
