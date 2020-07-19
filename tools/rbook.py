#!./venv/bin/python3

import os
import sys
import re
import shutil
import argparse
from photoProc import photo_processor

'''
Usage:

python rbook.py -n
Looking for things to do..
Looking for imports in ./imports/copymethat..
  Would parse some_recipe.txt
  Would save ready/some-recipe.md
Looking for URL lists in ./imports/urls..
  Would generate ./ready/url1.md
  Would generate ./ready/url2.md
  Would generate ./ready/url2.md
Processing photos..
  For 'potato-soup.jpg':
    Warning: photo has no matching recipe: "potato-soup.md"
  For 'ordinary-pizza.jpg':
    Would adjust photo link from '../../assets/ordinary-pizza.jpg' to '../assets/ordinary-pizza.jpg'
  For 'cheeto-dip.md':
    Warning: Would remove photo reference '../../assets/cheeto-dip.jpg - No photo './src/assets/cheeto-dip.jpg' found
  Would resize src/assets/pesto-chicken.jpg to 600 x 400
Processing tags
  Would tag "pork-meat.md" with "verified" (auto-verify photo's recipes)
Generating ./src/SUMMARY.md..
end of update
'''


'''
# Tries to do all the things needed to process input files into the book
./rbook update [-n -f] # Just report status or version if nothing is passed in

# Return status of the book, reporting various stats, counts, and any tasks that need to be taken care of to complete the book
./rbook status

General Task List:

- Convert copymethat text files to md files, and place them in /staged

- Convert URLs and lists of URLs to starter md files, place them in /starters

- Update the SUMMARY.md file

- Reconcile photos to recipes and vice versa, resizing if necessary
'''

'''
There is an interesting workflow possible here, where the tinyDB entries are the only things
we edit. Then when editing is done, when just re-generate a recipe md file. This could reduce the amount of
regex type work we have to do, since all changes have to go through the db. The rbook processor can then
just mark each recipe that gets edited throughout the script, then go back through and regenerate those md files
all at once at the end of the script. Wow!

It's still important that we can insert new recipes in the db with nothing but an md file.
It's also important that we distinguish between a deleted recipe, and an edited one. The recipe
name or filename could change, and we need a way to ask the user if a recipe is edited or deleted?

If all automated changes first go through the DB, then we need to distinguish these types of changes
from the ones made manually by editing a md file.

Manual changes should have already happened before the script begins, so the first thing the
script needs to do is update the db with any manually made changes. But how do we figure out what
the changes are? We could just completely regenerate the db, then make any automated changes
to the book via the DB, then regenerate the md file of each DB entry that was automatically edited in the DB.

Is this too much?


Can we use file timestamps to determine which files have been updated? Compare the mtime between each recipe and the db?
os.stat(full_path).st_mtime

So to detect manual changes in the book, we just get a list of all the files with an mtime < the mtime of
the summary or the db, assuming we always update those before leaving the script.

For those files we find as "modified", we can just create an in-memory DB containing them, then
just do all our automatic edits with the DB, then regenerate the md files, and finally generate
the summary and update the edit recipes in the DB with newer info, add any new recipes to the DB, and
remove any recipes from the DB not found as a MD files at this time.

More detailed step by step:

# Modify md files

Handle new photos, and add links to recipes
Test all photo links in the book
Check for orphaned photos
Enforce "verified" tags

# All recipe file modification is done by now

Get a list of modifed recipes using timestamps
Update those entries in the DB, adding if necessary, adding all fields for each recipe
Look for any recipes in the DB, not found as an md file - delete from DB.

# Mdbook and DB are now up-to date with each other

Collect lists of books files - recipes, chapters, sections, dirfiles, summary exclusions, etc.
Generate the SUMMARY.md file
Write all the TOCs and the about file
'''

SRC_DIR = "./fsrc"
SUMMARY_FILE = "SUMMARY.md"
DRAFTS_DIR = "./fdrafts"
ABOUT_FILE = "about.md"
REDIR_404_FILE = "404.md"
REDIR_404_PHOTO = "404.jpg"
PHOTO_DIR = "./fsrc/assets"
PHOTO_WIDTH = 600

def error( indentation, msg ):
    print( (" " * indentation) + "\033[91m " + msg + "\033[00m" )

def error_quit( indentation, msg ):
    print( (" " * indentation) + "\033[91m " + msg + "\033[00m" )
    sys.exit(1)

"""
Recursively find all files of a certain type under some root directory
"""

def list_files(rootdir, ext):
    file_list = list()
    for root, dirs, files in os.walk(rootdir):
        [file_list.append(os.path.join(root, file)) for file in files if file.endswith(ext)]
    return file_list

def print_warning( indentation, msg ):
    print( (" " * indentation) + "\033[93m " + msg + "\033[00m" )

def print_done():
    print( "\033[92m " + "DONE!" + "\033[00m" )

class Rbook:
    def __init__( self, assets_dir, drafts_dir, src_dir, dry_run ):

        self.assets_path = assets_dir
        self.drafts_path = drafts_dir
        self.src_path = src_dir
        self.dry_update = dry_run
        self.photo_files = list_files(assets_dir, ".jpg")
        self.md_files = list_files("src", ".md")

    def proc_photos( self ):
        photo_processor(
                        self.src_path,
                        [REDIR_404_FILE, ABOUT_FILE, SUMMARY_FILE],
                        self.assets_path,
                        [REDIR_404_PHOTO],
                        PHOTO_WIDTH
                        )

    def generate_summary( self ):
        # open_file()
        # tree()
        # close_file()
        pass


def workerFunction():
    print( "Looking for things to do.." )

    # Collect the dry run flag from passed in args
    parser = argparse.ArgumentParser(prog='RBook')
    parser.add_argument('-f', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    book = Rbook( PHOTO_DIR, DRAFTS_DIR, SRC_DIR, args.f )
    '''
    Modify md files
    '''
    #TODO - Convert copymethat text files, url list file to md files, and place them in /staged. Use links_and_times.txt to fill in Overview fields if necessary
    # book.convert_copymethat()
    # book.convert_url_files()
    # book.add_overviews()
    book.proc_photos()

    '''
    Modify recipe database
    '''
    # All recipe file modification is done by now
        # Get a list of modifed recipes using timestamps
        # Update those entries in the DB, adding if necessary, adding all fields for each recipe
        # Look for any recipes in the DB, not found as an md file - delete from DB.
    # modified = book.get_modified_recipes()
    # book.add_update_db( modifed )
    # orphaned = book.get_orphaned_recipes_db()
    # book.trim_db( orphaned )
    '''
    Generate mdbook artifacts
    '''
    # Mdbook and DB are now synced
        # Collect lists of books files - recipes, chapters, sections, dirfiles, summary exclusions, etc.
        # Generate the SUMMARY.md file
        # Write all the TOCs and the about file
    # book.get_objects() - keep this internal
    # book.update_summary()
    # book.update_tocs()
    # book.update_about()
    # A new page that shows how many recipes are verified, how many total, current update rate, etc.
    # book.update_stats()

    # age = os.stat("links_and_times.txt").st_mtime
    # print(age)

    print( "end of update" )

    print_done()


if __name__ == "__main__":
    workerFunction()










