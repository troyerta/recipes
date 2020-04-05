#!/usr/bin/env python3

import sys
import os
from os import listdir, sep
from os.path import abspath, basename, isdir, isfile
import re
import shutil

SRC_PATH = "draft_recipes"
TEMPLATE_PATH = "src/template_blank.md"

def process_link( title, link ):
    recipe_name = title

    # Make target filename
    filename = os.path.join( SRC_PATH, re.sub( ' ', '-', title.lower() ) + ".md" )

    print(recipe_name, filename)

    shutil.copy(TEMPLATE_PATH, filename)

    # Read in the file
    with open(filename, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('Recipe Name', title)
    filedata = filedata.replace('Link Text', title)
    filedata = filedata.replace('https://www.website.com/Recipes/recipe/', link.strip())

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)

    return recipe_name, filename

def convert_html_to_recipe( input_file ):
    print( "input_file =", input_file )
    with open(input_file, 'r') as f:
        lines = f.readlines()
        # print(contents)
        p = re.compile( r'.*HREF=\"(.+)\" GUID' )

        link_list = list()

        for each in lines:
            # print(each)
            match = p.match( each )
            link_list.append( match.group(1) )

        # [print(x) for x in link_list]

        title_list = list()
        title_section = re.compile( r'^.*\/(.*)$' )
        html_trim = re.compile( r'^(.*).html.*$' )

        for link in link_list:
            title_match = title_section.match( link.strip('/') )
            # print(title_match.group(1))

            # Trim off any html crap we still have
            html = html_trim.match( title_match.group(1) )
            if html:
                title_list.append( html.group(1) )
            else:
                title_list.append( title_match.group(1) )

        assert( len(link_list) == len(title_list) )

        for idx, title in enumerate(title_list):
            # print( title_list[idx], link_list[idx], "\n" )
            process_link( title_list[idx], link_list[idx] )

def convert_txt_file( input_file ):
    print( "input_file =", input_file )
    with open(input_file, 'r') as f:
        lines = f.readlines()
        # print(lines)
        p = re.compile( r'^(.*),\W?(.*)$' )

        title_list = list()
        link_list = list()

        for each in lines:
            # print(each)
            match = p.match( each )

            if match:
                # print(match)
                title_list.append( match.group(1) )
                link_list.append( match.group(2) )
            else:
                print("No match:", each)

        assert( len(link_list) == len(title_list) )

        for idx, title in enumerate(title_list):
            # print( title_list[idx], link_list[idx], "\n" )
            process_link( title_list[idx], link_list[idx] )

if __name__ == "__main__":
    input_file = sys.argv[1]
    # convert_html_to_recipe( input_file )
    convert_txt_file( input_file )


    sys.exit()
