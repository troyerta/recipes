
import itertools
import sys
import os
import re
import fnmatch
from os.path import isdir, isfile
from PIL import Image

IMAGE_STRUCT = '<p align="center">\n\
<img title="{}" src="{}">\n\
</p>'

def quit( msg ):
    if msg:
        print( "  " + "\033[91m " + msg + "\033[00m" )
    print("Exiting..")
    sys.exit()

"""
Return the given path as an ordered list of path components
Can be used to easily determine a file's depth
"""
def splitpath(path, maxdepth=20):
    (head, tail) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [tail] if maxdepth and head and head != path else [head or tail]


"""
Recursively find all files of a certain type under some root directory
"""
def list_files(rootdir, ext):
    file_list = list()
    for root, dirs, files in os.walk(rootdir):
        [file_list.append(os.path.join(root, file)) for file in files if file.endswith(ext)]
    return file_list

"""
Downscales the image target image size if necessary
"""


def enforce_image_width(image_filepath, target_width):
    img = Image.open(image_filepath)
    # print(img.format)
    # print(img.mode)
    # print(img.size[0])
    if img.size[0] > target_width:
        print("resizing", image_filepath)
        wpercent = target_width / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((target_width, hsize), Image.ANTIALIAS)
        img.save(image_filepath)

"""
Get something like "pork-brownies.jpg" from "src/desserts/pork-brownies.md"
"""


def recipe_filename_from_photo_filename(path):
    return os.path.splitext(os.path.basename(path))[0] + ".md"

"""
Get something like "pork-brownies.jpg" from "src/desserts/pork-brownies.md"
"""


def photo_filename_from_recipe_path(path):
    return os.path.splitext(os.path.basename(path))[0] + ".jpg"

"""
Get something like "../../assets/port-brownies.jpg" from "src/desserts/pork-brownies.md"
"""
def photo_relpath_from_recipe_path(path, photo_dir):
    image_rel_link = str()
    filename = photo_filename_from_recipe_path(path)

    for num in range(len(splitpath(os.path.normpath(path))) - 2):
        image_rel_link = os.path.join("..", image_rel_link)
    rel_path = os.path.join(image_rel_link, os.path.basename(photo_dir), filename)
    return rel_path

"""
Generate the image structure that can be pasted into a recipe.
"""


def image_struct_from_file(target_file, photo_dir):
    rel_path = photo_relpath_from_recipe_path(target_file, photo_dir)
    title = re.sub(r"-", " ", os.path.splitext(os.path.basename(target_file))[0])
    output = IMAGE_STRUCT.format(title.title(), rel_path)
    return output

"""
Place an image structure between the title and the next section
"""
def insert_image_link(target_file, photo_dir):
    with open(target_file, "r") as fi:
        file_data = fi.read()
        image_struct_str = image_struct_from_file(target_file, photo_dir)
        new_data = re.sub( r"^(# .+)\n((?:\s)*)(## .+)", r"\1\n\n" + image_struct_str + r"\n\n\3", file_data, flags=re.MULTILINE)

    with open(target_file, "w") as fi:
        fi.write(new_data)

"""
Replace the current image <p> structure in a recipe with a new one. Good for updating rel paths
"""
def fix_image_link(target_file, photo_dir):
    current_link = search_img_link_in_file(target_file)
    if current_link:
        with open(target_file, "r") as fi:
            file_data = fi.read()
            image_struct_str = image_struct_from_file(target_file, photo_dir)
            new_data = re.sub(r'^(#.+)\n*((?:<.+>\s)+)\n*(#.+)', r"\1\n\n" + image_struct_str + r"\n\n\3", file_data, flags=re.MULTILINE )
        with open(target_file, "w") as fi:
            fi.write(new_data)

    if file_data != new_data:
        return True
    else:
        return False

"""
Find a specific recipe file in the recipe src
"""
def find(root, file, first=True):
    for d, subD, f in os.walk(root):
        if file in f:
            # print("{0} : {1}".format(file, d))
            if first == True:
                return os.path.join(d, file)
    return None

"""
Search for the img <p> in a recipe file, returning the match object
The match object has two groups: the image title and rel link
"""

def search_img_link_in_file(file):
    with open(file, "r") as fi:
        file_data = fi.read()
        img_match = re.search(r"^(?:#.+)\n+((?:<.+>\s)+)", file_data, flags=re.MULTILINE )
        if img_match:
            return img_match
        else:
            return None

"""
Adds an image link if it does not yet exist. Only call this for files
that definitely should have a link
"""
def enforce_image_link_exists( file, photo_dir ):
    img_match = search_img_link_in_file(file)
    if not img_match:
        insert_image_link( file, photo_dir )

"""
Fixes an already-existing image link
"""
def enforce_image_link_correct( md_file, photo_dir ):
    img_match = search_img_link_in_file(md_file)
    if img_match and fix_image_link(md_file, photo_dir):
        print("  Adjusted image reference in", md_file)

"""
Ensures a linked image actually exists (only use after all links are added)
"""
def enforce_linked_image_exists( file, photo_dir ):
    img_match = search_img_link_in_file(file)
    asset_img = os.path.join(photo_dir, photo_filename_from_recipe_path(md_file))
    if img_match and not isfile(asset_img):
        print("Could not find", asset_img, "for", md_file)
        quit()

"""
Main photo processing function
"""
def photo_processor( src_path, src_excludes, assets_dir, target_width_px, photo_excludes ):

    print( "Collecting photos from", assets_dir )
    image_files = list_files(assets_dir, ".jpg")
    md_files = list_files(src_path, ".md")
    md_exclude_paths = [os.path.join( src_path, md) for md in src_excludes]
    [md_files.remove( md ) for md in md_exclude_paths if md in md_files]
    md_file_basenames = [os.path.basename(fi) for fi in md_files]
    photo_exclude_paths = [os.path.join( assets_dir, img ) for img in photo_excludes]
    [image_files.remove( img ) for img in photo_exclude_paths if img in image_files]
    print( "Checking photo sizes" )
    [enforce_image_width( img, target_width_px ) for img in image_files ]
    print( "Verifying recipes for photos" )
    orphaned_photos = [img for img in image_files if recipe_filename_from_photo_filename(img) not in md_file_basenames ]
    if orphaned_photos:
        quit( "Error: these photos are orphaned: " + str(orphaned_photos) )

    # print( "If recipe file exists, open and check for photo link, add one if not present" )
    # Open each theretical recipe file, and look inside it, check for correct link, add if not present, correct if wrong
    recipes_to_check = [find(src_path, recipe_filename_from_photo_filename(img)) for img in image_files]
    assert(len(recipes_to_check) == len(image_files))

    [enforce_image_link_exists(recipe, assets_dir) for recipe in recipes_to_check]

    photod_recipes = [file for file in md_files if search_img_link_in_file( file )]
    # [print(rp) for rp in photod_recipes]

    # These need to be done for ALL md files
    [enforce_image_link_correct(recipe, assets_dir) for recipe in photod_recipes]

    # [enforce_linked_image_exists(recipe) for recipe in photod_recipes]
    #
    # Open open every recipe with a image link at all, and do the same thing, but also check that each photo exists

    # TODO
    # [add_tags( recipe, ["verified"]) for recipe in photod_recipes]

'''
    # This can find all the rows of the image tag exactly - g1 has the image tag
    ^(?:#.+)\n+((?:<.+>\s)+)

    # This gets the title and the image tag in groups 1 and 2
    ^(#.+)\n+((?:<.+>\s)+)

    # This searches within an img tag and finds the title and the rel link
    <(?:.*title\s*=\s*\")(.+)(?:\"\s*src\s*=\s*\")(.*)(?:\"\s*>)

    # This grabs the entire img tag along with it's surrounding whitepsace, so it can be trimmed
    ^(?:#.+)\n((?:\s*<.+>\s*)+)(?:## \S*)

    # This grabs all the whitespace rows between the title and the next section
    ^(?:#.+)\n((?:\s*)+)(?:## \S*)

    # This grabs the title, img link, and next header section in groups 1,2,3. All white space included in full match
    ^(#.+)\n+((?:<.+>\s)+)\n+(#.+)

    # This grabs the title, whitespace and next header in groups 1,2,3
    ^(#.+)\n((?:\s)*)(#.+)
'''
    # print( "If already present, test the image title and link, to make sure they're valid (does photo exist, etc.)" )
    # print( "If photo tag is present and valid, make sure the verified tag is in place" )
    # print( "Now get all recipes that have photo links, and make sure the photos exist and enforce \"verified\" tags." )

