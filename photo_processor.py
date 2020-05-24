#!./venv/bin/python3

import sys
import os
import re
import fnmatch
from os.path import isdir, isfile
from PIL import Image



'''
Add

<p align="center">
<img title="F3" src="../assets/f3.jpg">
</p>
'''

'''
Find a specific recipe file in the recipe src
'''
def find(root, file, first=True):
    for d, subD, f in os.walk(root):
        if file in f:
            # print("{0} : {1}".format(file, d))
            if first == True:
                return os.path.join(d,file)
    return None

'''
Find photos in the assets directory
'''
def find_file_by_glob( dir='assets', glob=r'*' ):
    matches = list()

    for file in os.listdir( dir ):
        if fnmatch.fnmatch(file, glob):
            matches.append( file )

    if matches:
        return [os.path.join( dir, match ) for match in matches ]
    else:
        return list()

    file_list = list()

def list_files( rootdir, ext ):
    file_list = list()
    for root, dirs, files in os.walk(rootdir):
        [file_list.append( os.path.join( root, file ) ) for file in files if file.endswith(ext)]
    return file_list

# images = find_file_by_glob('assets', glob=r'*')

# [print(img) for img in images]

# recipe = find( 'src', 'asian-lemon-chicken.md', True )

# print(recipe)

'''
To track the sources better - go through EVERY recipe, and look for recipe text, collecting the cited photo name

If photo is present in assets, enforce the correct width / height.

If photo is not present, throw an error detailing the issue, then exit.

Make sure the photo path is valid from the relative location of the md file

Each photo called out through the book is recorded in a local list.

After checking each recipe for for a photo, compare the recorded list of "handled" photos with the contents of the asserts dir.

If they differ by this point, then there is at least 1 unhandled photo in /assets.

For each unhandled photo, look for a recipe under the same title.

If such a recipe file exists, open it and search for a photo section

If a photo section match is found, then throw a detailed error, since this was not found earlier.
It might mean the recipe is trying to call out a photo under a mismatched name.

If no photo section match is found, then insert the photo text structure where it belongs.

Then run another giant search to make sure each photo is accounted for, and each recipe's photo exists.

There, easy!

'''

def search_img_tag_in_file( file ):
    with open( file, 'r' ) as fi:
        file_data = fi.read()
        img_match = re.search( r'.*\n<p.*\n<img title=\"(.*)\" src=\"(.*)\">\n</p>\n', file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

def splitpath(path, maxdepth=20):
     ( head, tail ) = os.path.split(path)
     return splitpath(head, maxdepth - 1) + [ tail ] \
         if maxdepth and head and head != path \
         else [ head or tail ]

def proc_photos():
    # Make a list of every md file in the src dir
    # md_files = find_file_by_glob( "src", r'*.md' )
    md_files = list_files( "src", ".md" )

    # [print(rp) for rp in md_files]

    print("Checking recipes for image references..")
    for md_file in md_files:
        img_match = search_img_tag_in_file( md_file )

        if img_match:
            image_rel_link = str()

            # Compute what the image link should be
            for num in range(len(splitpath(md_file)) - 2):
                image_rel_link = os.path.join( "..", image_rel_link )

            image_rel_link = os.path.join( image_rel_link, "assets", os.path.splitext( os.path.basename( md_file ) )[0] + ".jpg" )

            if( image_rel_link != img_match.group(2) ):
                print(md_file, "contains bad image link.\nExpected " + "\'" + image_rel_link + "\'" + " - was " + "\'" + img_match.group(2) + "\'" )
                sys.exit()

            # print("searching for", image_should)
            # if isfile( image_should ):
            #     print( "found", image_should, "referenced in", md_file )


def workerFunction():
    proc_photos()

if __name__ == "__main__":
    workerFunction()
