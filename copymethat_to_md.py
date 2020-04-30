#!/usr/bin/env python3

import sys
import os
from os.path import abspath, basename, isdir, isfile
import re
import shutil
import subprocess

TEMPLATE_PATH = "./template_blank.md"
OUTPUT_PATH = "./drafts/parser_output"

REGEX_TITLE = r'^(.*)\n'
REGEX_URL = r'^(?:Adapted from )(.*)$'
REGEX_TAGS_LINE = r'^tags: (.*)$'
REGEX_SERVINGS = r'^(?:Servings: )(.*)$'

def error( msg ):
    print( "\n" + msg + "\n" )
    sys.exit()

class recipe():
    def __init__( self, path, template_path, output_dir ):

        self.target_file_path = os.path.normpath( path )
        self.template_file_path = os.path.normpath( template_path )
        self.output_dir = os.path.normpath( output_dir)

        self.target_file_data = self.readTargetFile()
        self.template_file_data = self.readTemplateFile()
        self.out_file = ''

        self.title = None
        self.prep_time = None
        self.cook_time = None
        self.total_time = None
        self.url_txt = None
        self.tags_txt = None
        self.notes_txt = None
        self.description_txt = None
        self.servings_txt = None
        self.ingredients_txt = None
        self.method_txt = None
        self.formatted_txt = None
        self.result_file_path = None

    def __str__(self):
        return str( self.target_file_path )

    def readTargetFile( self ):
        with open( self.target_file_path, 'r') as fi:
            data = fi.read()
            return data

    def readTemplateFile( self ):
        with open( self.template_file_path, 'r') as fi:
            data = fi.read()
            return data

    # Finds all test groups and test cases, returning a list of test group objects
    def parse_data( self ):
        self.title              = self.get_title( self.target_file_data )
        self.result_file_path   = os.path.join( OUTPUT_PATH, re.sub(' ', '-', self.title.lower() ) + ".md" )
        self.url_txt            = self.find_url( self.target_file_data )
        self.tags_txt           = self.find_tags( self.target_file_data )
        self.description_txt    = self.find_description( self.target_file_data )
        self.servings_txt       = self.find_servings( self.target_file_data )
        # print("Servings: " + "'" + self.servings_txt + "'" )
        self.ingredients_txt    = self.find_ingredients( self. target_file_data )
        self.method_txt         = self.find_method( self.target_file_data )

    def get_title( self, data ):
        title = None
        title_match = re.search( REGEX_TITLE, data )
        if title_match:
            title = self.confirm_title( self.clean_title( title_match.group(1) ) )
        return title

    def confirm_title( self, title ):

        ret = title

        while True:

            print( "Current title is \'" + ret + "\'\n\n")
            confirmation = input( "\tPress ENTER to confirm\n\t\'q\' to cancel\n\tOr type new title:\n\n" )

            if confirmation:
                if confirmation == 'q':
                    error( "User quit" )
                else:
                    ret = confirmation
            else:
                break
        print("Title:", ret)
        return ret

    def set_times( self ):
        while True:
            self.prep_time = input( "Prep Time: " )
            if self.prep_time and self.prep_time == 'q':
                error("User quit")

            self.cook_time = input( "Cook Time: " )
            if self.cook_time and self.cook_time == 'q':
                error("User quit")

            self.total_time = input( "Total Time: " )
            if self.total_time and self.total_time == 'q':
                error("User quit")

            confirmation = input("\nPress ENTER to confirm, r to retry, q to quit\n")

            if confirmation:
                if confirmation == 'q':
                    error("User quit")
            else:
                break

        print( "Prep Time:", self.prep_time )
        print( "Cook Time:", self.cook_time )
        print( "Total Time:", self.total_time )

    def clean_title( self, title_in ):
        num_temp = re.sub('\d+-', '', os.path.basename( title_in ).title() )
        with_temp = re.sub('With', 'with', num_temp )
        and_temp = re.sub('And', 'and', with_temp )
        u_score_temp = re.sub('_', ' ', and_temp )
        tasty_temp = re.sub('By Tasty', '', u_score_temp )
        recipe_temp = re.sub('Recipe', '', tasty_temp )
        return recipe_temp.strip()

    def clean_subsection( self, title_in ):
        with_temp = re.sub('With', 'with', title_in.title() )
        the_temp = re.sub('The', 'the', with_temp )
        and_temp = re.sub('And', 'and', the_temp )
        u_score_temp = re.sub('_', ' ', and_temp )
        tasty_temp = re.sub('By Tasty', '', u_score_temp )
        recipe_temp = re.sub('Recipe', '', tasty_temp )
        return recipe_temp.strip()

    def find_url( self, data ):
        match = re.search( REGEX_URL, data, flags=re.MULTILINE )
        if match:
            return match.group(1)
        else:
            return None

    def find_servings( self, data ):
        match = re.search( REGEX_SERVINGS, data, flags=re.MULTILINE )
        if match and match.group(1) != '':
            return match.group(1).strip('\n')
        else:
            return None

    def find_tags( self, data ):
        match = re.search( REGEX_TAGS_LINE, data, flags=re.MULTILINE )
        if match:
            line = match.group(1)
            tag_list = line.split(", ")
            return tag_list
        else:
            return None

    def find_description( self, data ):
        # Grab everything between the URL and INGREDIENTS
        match = re.search( r'Adapted from.*\n[\s\S]*?INGREDIENTS', data, flags=re.MULTILINE )
        section = match.group(0)
        # Remove the things we know could be there
        section = re.sub( r'^(?:Adapted from )(.*)$', r'', section.strip('\n'), flags=re.MULTILINE )
        section = re.sub( r'^tags: (.*)$', r'', section, flags=re.MULTILINE )
        section = re.sub( r'^(?:Servings: )(.*)$', r'', section, flags=re.MULTILINE )
        section = re.sub( r'INGREDIENTS', r'', section, flags=re.MULTILINE )
        desc = re.search( r'^.*$', section.strip('\n'), flags=re.MULTILINE )
        # print( desc )
        if desc and desc.group(0) != '':
            return desc.group(0)
        else:
            return None

    def find_ingredients( self, data ):

        formatted_output = str()
        lines_in_ingredients = str()

        ingredients_match = re.search( r'^(?:INGREDIENTS\n\n)((.*\n)+)^\nSTEPS', data, flags=re.MULTILINE )
        if ingredients_match:
            all_ingredient_lines = ingredients_match.group(1).splitlines()
            lines_in_ingredients = [line for line in all_ingredient_lines if line != '']
            # Find first alpha-word in each line: r'([a-zA-Z]+).*\n'

        for item in lines_in_ingredients:
            section_title_match = re.search( r'(.*:)', item )
            ingredient_match = re.search( r'(.+)', item )

            if section_title_match:
                formatted_output += ( "#### " + self.clean_subsection( section_title_match.group(1) ) + "\n\n" )
            elif ingredient_match:
                formatted_output += ( '- ' + item + '\n\n' )
            else:
                print("Ingredients section contains unreadable line:", item)
                sys.exit()
        return formatted_output

    def find_method( self, data ):
        formatted_output = str()

        notes_match = re.search( r'(^NOTES\n\n(.*\n)+)', data, flags=re.MULTILINE )

        if( notes_match):
            notes_items_match = re.search( r'(?:^NOTES\n\n)((.*\n)+)', notes_match.group(0), flags=re.MULTILINE )
            notes = str()
            if notes_items_match:
                all_note_lines = notes_items_match.group(1).splitlines()
                for line in all_note_lines:
                    if line != '':
                        notes += ( '- ' + line + '\n\n' )
            if notes != '':
                self.notes_txt = notes

            noteless_data = data.replace( notes_match.group(0), '' )
        else:
            noteless_data = data

        formatted_output = str()
        lines_in_steps = str()

        steps_match = re.search( r'(?:^STEPS\n\n)((.*\n)+)', noteless_data, flags=re.MULTILINE )
        if steps_match:
            all_lines = steps_match.group(1).splitlines()
            lines_in_steps = [line for line in all_lines if line != '']

        for step in lines_in_steps:
            step_match = re.search( r'^(\d+)\) (.*)', step )
            sub_step_title_match = re.search( r'^(.*:)' , step )

            if step_match:
                formatted_output += ( step_match.group(1) + '. ' + step_match.group(2) + '\n' )
                formatted_output += ("---\n\n")
            elif sub_step_title_match:
                formatted_output += ( "#### " + self.clean_subsection( sub_step_title_match.group(1) ) + "\n\n" )
            else:
                print("Steps section contains unreadable line:", step)
                sys.exit()
        return formatted_output

    def create_out_file( self ):
        # Make target filename
        self.out_file = os.path.join( OUTPUT_PATH, re.sub(' ', '-', self.title.lower() ) + ".md" )
        shutil.copy(TEMPLATE_PATH, self.out_file)

    def print_to_out_file( self ):
        # Read in the template
        data = None

        with open(self.out_file, 'r') as fi:
            data = fi.read()

        if data:
            data = self.fill_template_title( data )
            data = self.fill_template_url( data )
            data = self.fill_template_description( data )
            data = self.fill_template_servings( data )
            data = self.fill_template_prep_time( data )
            data = self.fill_template_cook_time( data )
            data = self.fill_template_total_time( data )
            data = self.fill_overview( data )
            data = self.fill_template_tags( data )
            data = self.fill_template_ingredients( data )
            data = self.fill_template_method( data )
            data = self.fill_template_notes( data )

            self.template_file_data = data

            with open( self.out_file, 'w' ) as file:
                file.write( self.template_file_data )
        else:
            error( "Could not read template" )

    def fill_template_title( self, filedata ):
        if self.title:
            filedata = filedata.replace('Recipe Name', self.title)
        else:
            error( "No title to write" )
        return filedata

    def fill_template_url( self, filedata ):
        if self.url_txt and self.title:
            filedata = filedata.replace('Link Text', self.title)
            filedata = filedata.replace('https://www.website.com/Recipes/recipe/', self.url_txt)
        else:
            if self.title:
                print(self.title, "- Ok")
            if self.url_txt:
                print(self.url_txt, "- Ok")
            error( "No Title or URL to print" )
        return filedata

    def fill_template_description( self, filedata ):
        if self.description_txt:
            filedata = filedata.replace('Description', self.description_txt)
        else:
            filedata = filedata.replace('\n## Description\n', '')
        return filedata

    def fill_template_servings( self, filedata ):
        # If Servings string is just a number, append "servings" or "serving" depending on the value
        if self.servings_txt:
            filedata = filedata.replace('- Yield:', '- Yield: ' + self.servings_txt)
        else:
            filedata = filedata.replace('- Yield:\n', '')
        return filedata

    def fill_template_prep_time( self, filedata ):
        if self.prep_time:
            filedata = filedata.replace('- Prep Time:', '- Prep Time: ' + self.prep_time)
        else:
            filedata = filedata.replace('- Prep Time:\n', '')
        return filedata

    def fill_template_cook_time( self, filedata ):
        if self.cook_time:
            filedata = filedata.replace('- Cook Time:', '- Cook Time: ' + self.cook_time)
        else:
            filedata = filedata.replace('- Cook Time:\n', '')
        return filedata

    def fill_template_total_time( self, filedata ):
        if self.total_time:
            filedata = filedata.replace('- Total Time:', '- Total Time: ' + self.total_time)
        else:
            filedata = filedata.replace('- Total Time:\n', '')
        return filedata

    def fill_overview( self, filedata ):
        if not self.servings_txt and not self.prep_time and not self.cook_time and not self.total_time:
            filedata = filedata.replace('\n## Overview\n\n', '')
        return filedata

    def fill_template_tags( self, filedata ):
        if self.tags_txt:
            tags_str = '\n'.join( sorted( self.tags_txt ) )
            filedata = filedata.replace('## Tags\n', '## Tags\n' + tags_str)
        else:
            filedata = filedata.replace('\n## Tags\n\n', '')
        return filedata

    def fill_template_ingredients( self, filedata ):
        if self.ingredients_txt:
            filedata = filedata.replace('- ingredient 1\n', self.ingredients_txt)
        else:
            error( "No ingredients to write" )
        return filedata

    def fill_template_method( self, filedata ):
        if self.method_txt:
            filedata = filedata.replace('- step 1\n', self.method_txt)
        else:
            error( "No methods to write" )
        return filedata

    def fill_template_notes( self, filedata ):
        if self.notes_txt:
            filedata = filedata.replace( '## Notes\n', '## Notes\n\n' + self.notes_txt )
        else:
            filedata = filedata.replace( '\n## Notes\n', '' )
        return filedata

    def clean_up( self ):
        os.remove( self.target_file_path )

def workerFunction():
    if len(sys.argv) <= 1:
        print("Please pass in a txt file to convert..")
        error( "Missing argument 1" )

    target_file = sys.argv[1]
    if not isfile( target_file ):
        print("File not found:", target_file )
        error( "File not found" )

    target_recipe = recipe( target_file, TEMPLATE_PATH, OUTPUT_PATH )
    target_recipe.parse_data()
    target_recipe.set_times()
    target_recipe.create_out_file()
    target_recipe.print_to_out_file()
    target_recipe.clean_up()

    print("\nSuccess!\n")

if __name__ == "__main__":
    workerFunction()
