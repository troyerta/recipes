#!./venv/bin/python3

import sys
import os
import re
import fnmatch
from os.path import isdir, isfile
from PIL import Image

PHOTO_DIR = 'assets'
PHOTO_WIDTH = 1024
IMAGE_STRUCT = "<p align=\"center\">\n\
<img title=\"{}\" src=\"{}\">\n\
</p>\n"

'''
Add

<p align="center">
<img title="F3" src="../assets/f3.jpg">
</p>
'''

def quit():
    print("Exiting..")
    sys.exit()

'''

'''
def resize_image( image_filepath, target_width ):
    img = Image.open(image_filepath)
    # print(img.format)
    # print(img.mode)
    # print(img.size)
    wpercent = (target_width/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((target_width,hsize), Image.ANTIALIAS)
    img.save(image_filepath)

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
[DONE] Go through each recipe, and look for the PHOTO tag. If found, then find a corresponding photo in the assets folder.
[DONE] If not found, then write an error message and exit.
[DONE] If found, then resize the photo, re-saving as a jpg.
[DONE]    Then, re.sub the PHOTO tag with the <p> section with the correct relative link to the file.

[DONE] To track the sources better - go through EVERY recipe, and look for recipe text, collecting the cited photo name
[DONE] Make sure the specified photo path is correct

If photo is present in assets, enforce the correct width / height.

If photo is not present, throw an error detailing the issue, then exit.

Each photo called out through the book is recorded in a local list.

After checking each recipe for for a photo, compare the recorded list of "handled" photos with the contents of the asserts dir.

If they differ by this point, then there is at least 1 unhandled photo in /assets.

For each unhandled photo, look for a recipe under the same title.

If such a recipe file exists, open it and search for a photo section

If a photo section match is found, then throw a detailed error, since this was not found earlier.
It might mean the recipe is trying to call out a photo under a mismatched name.

If no photo section match is found, then insert the photo text structure where it belongs.

Then run another giant search to make sure each photo is accounted for, and each recipe's photo exists.

If a photo moves around, or it's name changes, we should still have everything we need in order to fix the rel links

There, easy!

'''

def search_img_link_in_file( file ):
    with open( file, 'r' ) as fi:
        file_data = fi.read()
        img_match = re.search( r'.*\n<p.*\n<img title=\"(.*)\" src=\"(.*)\">\n</p>\n', file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

def search_img_tag_in_file( file ):
    with open( file, 'r' ) as fi:
        file_data = fi.read()
        img_match = re.search( r'^PHOTO$\n', file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

def splitpath(path, maxdepth=20):
     ( head, tail ) = os.path.split(path)
     return splitpath(head, maxdepth - 1) + [ tail ] \
         if maxdepth and head and head != path \
         else [ head or tail ]

'''
Get something like "pork-brownies.jpg" from "src/desserts/pork-brownies.md"
'''
def photo_filename_from_recipe_path( path ):
    return os.path.splitext( os.path.basename( path ) )[0] + ".jpg"

'''
Get something like "../../assets/port-brownies.jpg" from "src/desserts/pork-brownies.md"
'''
def photo_relpath_from_recipe_path( path ):
    image_rel_link = str()
    filename = photo_filename_from_recipe_path( path )
    for num in range( len( splitpath( path ) ) - 1 ):
        image_rel_link = os.path.join( "..", image_rel_link )
    rel_path = os.path.join( image_rel_link, PHOTO_DIR, filename )
    return rel_path

'''
Generate the image structure that can be pasted into a recipe.
'''
def image_struct_from_file( target_file ):
    rel_path = photo_relpath_from_recipe_path( target_file )
    title = re.sub( r'-', ' ', os.path.splitext(os.path.basename( target_file ))[0] )
    # print(rel_path,title)
    output = IMAGE_STRUCT.format( title, rel_path )
    return output

'''
Replace the PHOTO tag in a recipe with an image structure
'''
def insert_image_link( target_file ):
    with open( target_file, 'r' ) as fi:
        file_data = fi.read()
        image_struct_str = image_struct_from_file(target_file)
        # print(image_struct_str)
        new_data = re.sub( r'^PHOTO$\n', image_struct_str, file_data, flags=re.MULTILINE )
        # new_data = file_data.replace( "PHOTO\n", image_struct_str )

    with open( target_file, 'w' ) as fi:
        fi.write( new_data )

def proc_photos():
    # Make a list of every md file in the src dir
    md_files = list_files( "src", ".md" )

    print("Checking recipes for image tags..")
    for md_file in md_files:
        tag_match = search_img_tag_in_file( md_file )

        if tag_match:
            # Try to find it's corresponding photo file
            img_filepath = os.path.join( PHOTO_DIR, photo_filename_from_recipe_path( md_file ) )
            if not isfile( img_filepath ):
                print("Could not find", img_filepath, "for", md_file)
                quit()

            # Image is present: Resize it and insert a link into the recipe
            # resize_image( img_filepath, PHOTO_WIDTH )
            insert_image_link( md_file )

    print("Checking recipes for image references..")
    for md_file in md_files:
        img_match = search_img_link_in_file( md_file )

        if img_match:
            image_rel_link = photo_relpath_from_recipe_path( md_file )

            if( image_rel_link != img_match.group(2) ):
                print(md_file, "contains mismatched image link.\nExpected " + "\'" + image_rel_link + "\'" + " - was " + "\'" + img_match.group(2) + "\'" )
                quit()

            # print("searching for", image_should)
            # if isfile( image_should ):
            #     print( "found", image_should, "referenced in", md_file )


def workerFunction():
    proc_photos()

if __name__ == "__main__":
    workerFunction()
