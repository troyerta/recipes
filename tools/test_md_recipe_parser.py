#!./venv/bin/python3

import os
import sys
import re
from parser import *
from photoProc import *

SRC_DIR = "./test/fake_book_src"
TEST_RECIPES = "./test/fake_test_recipes"
FAKE_RECIPE_1 = os.path.join( TEST_RECIPES, "apple-pie.md" )
# SUMMARY_FILE = "SUMMARY.md"
# DRAFTS_DIR = "./fdrafts"
# ABOUT_FILE = "about.md"
# REDIR_404_FILE = "404.md"
# REDIR_404_PHOTO = "404.jpg"
# PHOTO_DIR = os.path.join( SRC_DIR, "assets" )
# PHOTO_WIDTH = 600

def require_equal( a, b ):
    if a != b:
        msg = a + " != " + b
        print("\033[91m" + msg + "\033[00m")

def title_from_filename( md_file ):
    base_temp = os.path.splitext(os.path.basename(md_file))[0]
    num_temp = re.sub("\d+-", "", os.path.basename(base_temp).title())
    with_temp = re.sub("with", "with", num_temp, flags=re.IGNORECASE)
    and_temp = re.sub("and", "and", with_temp, flags=re.IGNORECASE)
    the_temp = re.sub("the", "", and_temp, flags=re.IGNORECASE)
    best_temp = re.sub("best", "", the_temp, flags=re.IGNORECASE)
    u_score_temp = re.sub("_", " ", best_temp)
    hyphen_temp = re.sub("-", " ", u_score_temp)
    tasty_temp = re.sub("by tasty", "", hyphen_temp, flags=re.IGNORECASE)
    recipe_temp = re.sub("recipes?", "", tasty_temp, flags=re.IGNORECASE)
    comma_temp = re.sub(",", "", recipe_temp)
    return comma_temp.strip()

# Opens and reads a recipe file for internal consistency
# and correct formatting
# Can be ran in "warn" mode, which prints potential problems
# or in "repair" mode, which tries for fix problems
def workerFunction():
    print("Running tests..")
    print("Testing", FAKE_RECIPE_1)
    txt = None
    correct_title = title_from_filename(FAKE_RECIPE_1)

    with open( FAKE_RECIPE_1, 'r') as f:
        txt = f.read()

    # File must be readable
    assert(txt)
    title = get_title( txt )
    # Recipe MUST have a Printed title
    assert(title)
    # Recipes' title MUST be consistent with the filename
    require_equal( title, correct_title )
    assert(title == correct_title)

    (ref_title, ref_link) = get_img_link( txt )
    if ref_title:
        require_equal(ref_title, correct_title)
        assert(ref_title == correct_title)
    if ref_link:
        ref_link_basename = os.path.splitext( os.path.basename(ref_link) )[0]
        recipe_basename = os.path.splitext( os.path.basename(FAKE_RECIPE_1) )[0]
        require_equal( ref_link_basename, recipe_basename )
        assert( ref_link_basename == recipe_basename )

    # Overview section is optional
    # But if the ## Overview header is present:
    # At least one line with .*:.* must be present
    overview = get_overview( txt )
    if overview:
        print(overview)


if __name__ == "__main__":
    workerFunction()



