#!./venv/bin/python3

import sys
import os
import re
import fnmatch
from os.path import isdir, isfile
from PIL import Image

'''
Requirements:

If a PHOTO tag is found in a recipe, the tag should be replaced with a link to the image.
If the image can't be found, then throw an error.

If a image file link in a recipe does not correctly point back to an existing file, or looks in the wrong place for a file, then
throw and warning, and try to fix the link to the correct link.

If an image is not linked or referred to anywhere in the recipe book, then print a warning message.

./photo_processor.py
Checking for new photo links..
Testing photo links..
Looking for unreferenced photos..

'''

PHOTO_DIR = 'src/assets'
PHOTO_WIDTH = 600
IMAGE_STRUCT = "<p align=\"center\">\n\
<img title=\"{}\" src=\"{}\">\n\
</p>\n"

'''
Bail out early with a message
'''
def quit():
    print("Exiting..")
    sys.exit()

'''
Downscales the image target image size if necessary
'''
def enforce_image_width( image_filepath, target_width ):
    img = Image.open(image_filepath)
    # print(img.format)
    # print(img.mode)
    # print(img.size[0])
    if img.size[0] > target_width:
        print("resizing", image_filepath)
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
Recursively find all files of a certain type under some root directory
'''
def list_files( rootdir, ext ):
    file_list = list()
    for root, dirs, files in os.walk(rootdir):
        [file_list.append( os.path.join( root, file ) ) for file in files if file.endswith(ext)]
    return file_list

'''
Search for the img <p> in a recipe file, returning the match object
The match object has two groups: the image title and rel link
'''
def search_img_link_in_file( file ):
    with open( file, 'r' ) as fi:
        file_data = fi.read()
        img_match = re.search( r'.*\n<p.*\n<img title=\"(.*)\" src=\"(.*)\">\n</p>\n', file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

'''
Return the match object the 'PHOTO' tag in a recipe if it is found, else None
'''
def search_img_tag_in_file( file ):
    with open( file, 'r' ) as fi:
        file_data = fi.read()
        img_match = re.search( r'^PHOTO$\n', file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

'''
Return the given path as an ordered list of path components
Can be used to easily determine a file's depth
'''
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
    for num in range( len( splitpath( path ) ) - 2 ):
        image_rel_link = os.path.join( "..", image_rel_link )
    rel_path = os.path.join( image_rel_link, os.path.basename( PHOTO_DIR ), filename )
    return rel_path

'''
Generate the image structure that can be pasted into a recipe.
'''
def image_struct_from_file( target_file ):
    rel_path = photo_relpath_from_recipe_path( target_file )
    title = re.sub( r'-', ' ', os.path.splitext(os.path.basename( target_file ))[0] )
    # print(rel_path,title)
    output = IMAGE_STRUCT.format( title.title(), rel_path )
    return output

'''
Replace the PHOTO tag in a recipe with an image structure
'''
def insert_image_link( target_file ):
    with open( target_file, 'r' ) as fi:
        file_data = fi.read()
        image_struct_str = image_struct_from_file(target_file)
        new_data = re.sub( r'^PHOTO$\n', image_struct_str, file_data, flags=re.MULTILINE )

    with open( target_file, 'w' ) as fi:
        fi.write( new_data )

'''
Replace the current image <p> structure in a recipe with a new one. Good for updating rel paths
'''
def fix_image_link( target_file ):
    current_link = search_img_link_in_file(target_file)
    if current_link:
        with open( target_file, 'r' ) as fi:
            file_data = fi.read()
            image_struct_str = image_struct_from_file(target_file)
            new_data = re.sub( current_link.group(0), "\n"+image_struct_str, file_data, flags=re.MULTILINE )

        with open( target_file, 'w' ) as fi:
            fi.write( new_data )
        return True
    else:
        return False

'''
Worker function for the script. Runs the 3 major tasks of the photo processor
'''
def proc_photos():
    # Make a list of every md file in the src dir, a list of their basenames, and a list of each jpg file in the assets dir
    image_files = list_files( PHOTO_DIR, ".jpg" )
    md_files = list_files( "src", ".md" )
    md_file_basenames = [os.path.basename( fi ) for fi in md_files]

    print("Checking for new photo links..")
    for md_file in md_files:
        tag_match = search_img_tag_in_file( md_file )

        if tag_match:
            # Try to find it's corresponding photo file
            img_filepath = os.path.join( PHOTO_DIR, photo_filename_from_recipe_path( md_file ) )
            if not isfile( img_filepath ):
                print("Could not find", img_filepath, "for", md_file)
                quit()

            # Found the corresponding image file Resize it and insert a link into the recipe
            enforce_image_width( img_filepath, PHOTO_WIDTH )
            insert_image_link( md_file )

    print("Testing image links..")
    for md_file in md_files:
        img_match = search_img_link_in_file( md_file )

        if img_match:
            image_rel_link = photo_relpath_from_recipe_path( md_file )
            asset_img = os.path.join( PHOTO_DIR, photo_filename_from_recipe_path( md_file ) )

            if( image_rel_link != img_match.group(2) ):
                if fix_image_link( md_file ) == True:
                    print("\tUpdated image reference in", md_file)
                    image_files.remove( os.path.join( PHOTO_DIR, photo_filename_from_recipe_path( md_file ) ) )
                else:
                    print("\t" + md_file, "contains mismatched image link.\n\tExpected " + "\'" + image_rel_link + "\'" + "\n\twas " + "\'" + img_match.group(2) + "\'" )
                    print("\tI tried to update the link, but failed to find the current image reference")
                    quit()
            elif not isfile( asset_img ):
                print("Could not find", asset_img, "for", md_file)
                quit()
            else:
                image_files.remove( os.path.join( PHOTO_DIR, photo_filename_from_recipe_path( md_file ) ) )

    print("Looking for unreferenced photos..")
    if len(image_files) > 0:
        print("\tWarning - unreferenced images found:")
        for image in image_files:
            print("\t\t" + image)
            possible_recipe = os.path.splitext( os.path.basename( image ) )[0] + ".md"
            if possible_recipe in md_file_basenames:
                print("\t\tDid you mean to reference the", possible_recipe, "recipe?")
                print("\t\tJust add a \'PHOTO\' tag somewhere in the recipe to reference this photo")

def workerFunction():
    proc_photos()
    sys.exit()

if __name__ == "__main__":
    workerFunction()
