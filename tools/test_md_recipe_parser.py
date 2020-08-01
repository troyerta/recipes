#!./venv/bin/python3

import os
from os.path import isfile
import sys
import re
from parser import *
from photoProc import *


SRC_DIR = "./test/fake_book_src"
TEST_RECIPES = "./test/fake_test_recipes"
FAKE_RECIPE_1 = os.path.join( TEST_RECIPES, "apple-pie.md" )

def expect_equal( a, b ):
    if a != b:
        msg = str(a) + " != " + str(b)
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

"""
This encapsulates a test recipe with the expected results of it's tests
"""
class RecipeTestGroup:
    def __init__( self, recipe_file ):
        self.recipe_file = recipe_file
        self.exp_title = title_from_filename( recipe_file )

        self.exp_img_section = False
        self.exp_img_title = None
        self.exp_img_link = None

        self.exp_overview_section = False
        self.exp_overview_lines = list()
        self.exp_overview_lines_count = 0

        self.exp_ingredients_sublists = list()
        self.exp_ingredients_sublist_count = 0
        self.exp_ingredients_section_lines = list()

        self.exp_method_lists = list()
        self.exp_method_list_count = 0
        self.exp_method_section_lines = list()

        self.exp_notes_section = False
        self.exp_notes_lines = list()
        self.exp_notes_lines_count = 0

        self.exp_reference_section = False
        self.exp_reference_title = None
        self.exp_reference_link = None

        self.exp_tag_section = False
        self.exp_tag_lines = list()
        self.exp_tag_lines_count = 0

    def valid_txt_list( self, input: items ) -> bool:
        if input is not None and len(input) > 0 and "" not in input:
            return True
        else:
            return False

    def expect_img( self, title: str = None, link: str = None ):
        if title or link:
            self.exp_img_section = True
            self.exp_img_title = title
            self.exp_img_link = link

    def expect_overview( self, lines: items = None ):
        if self.valid_txt_list(lines):
            self.exp_overview_section = True
            self.exp_overview_lines = lines
            self.exp_overview_lines_count = len( lines )

    def expect_ingredients( self,  ):
        self.exp_ingredients_sublists = list()
        self.exp_ingredients_sublist_count = 0
        self.exp_ingredients_section_lines = list()

    def expect_method( self,  ):
        self.exp_method_sublists = list()
        self.exp_method_sublist_count = 0
        self.exp_method_section_lines = list()

    def expect_notes( self, lines: items = None ):
        if self.valid_txt_list(lines):
            self.exp_notes_section = True
            self.exp_notes_lines_count = len( lines )
            self.exp_notes_lines = lines

    def expect_reference( self, title_link_tuple: tuple = (None, None) ):
        if title_link_tuple[0] or title_link_tuple[1]:
            self.exp_reference_section = True
            self.exp_reference_title = title_link_tuple[0]
            self.exp_reference_link = title_link_tuple[1]

    def expect_tags( self, tags_list: items = None ):
        if self.valid_txt_list( tags_list ):
            self.exp_tag_section = True
            self.exp_tag_lines = tags_list
            self.exp_tag_lines_count = len( tags_list )

requirements = RecipeTestGroup( "./test/fake_test_recipes/apple-pie.md" )
requirements.expect_img( "Apple Pie", "../assets/apple-pie.jpg" )
requirements.expect_overview( [ "Yield: 4 servings",
                         "Prep Time: 15 mins",
                         "Cook Time: 20 mins"] )
# requirements.expect_ingredients()
# requirements.expect_method()
requirements.expect_notes( [   "You can add salt and pepper to the filling for even more flavor.",
                        "If you like it on the fruitier side, add more apples to the filling."] )
requirements.expect_reference( ( "Apple Pie", "https://www.applepies.com/best-apple-pie" ) )
requirements.expect_tags( [ "fruity", "verified" ] )





def test_recipe( recipe_file: str(), reqs: RecipeTestGroup):
    print("Testing", FAKE_RECIPE_1)
    assert( isfile(recipe_file) )
    txt = None

    """
    File must exist and be read correctly
    """
    with open( FAKE_RECIPE_1, 'r') as f:
        txt = f.read()
    assert(txt)

    """
    A title must present
    The title must be correctly named after the filename
    """
    title = get_title( txt )
    assert(title)
    expect_equal( title, reqs.exp_title )
    assert( title == reqs.exp_title )

    """
    THe image link is optional
    """
    img_title, img_link = get_img_link( txt )
    if reqs.exp_img_section:
        expect_equal(img_title, reqs.exp_img_title)
        assert(img_title == reqs.exp_img_title)
        expect_equal(img_link, reqs.exp_img_link)
        assert(img_link == reqs.exp_img_link)
    else:
        assert( img_title is None )
        assert( img_link is None )

    # Each line of the Overview section must be correctly collected
    # here in a list 3 elements long. Bullet points should be gone.
    overview = get_overview( txt )
    if reqs.exp_overview_section:
        assert( overview is not None )
        expect_equal( len(overview), reqs.exp_overview_lines_count )
        assert( len(overview) == reqs.exp_overview_lines_count )
        for line in range( reqs.exp_overview_lines_count ):
            expect_equal( overview[line], reqs.exp_overview_lines[line] )
            assert( overview[line] == reqs.exp_overview_lines[line] )
    else:
        assert( overview is None )

    ingredients = get_ingredients( txt )
    assert(ingredients)
    assert( ingredients.num_items() == 10 )
    assert(ingredients.num_sublists() == 3)
    assert( len(ingredients.sections[0]) == 1 )
    assert( len(ingredients.sections[1]) == 5 )
    assert( len(ingredients.sections[2]) == 4 )

    for num, sublist in enumerate(ingredients.sections):
        # Just single item
        if len(sublist.items) == 1:
            assert(sublist.title is None)
            # print(num+1, sublist.items[0])
        # A sublist of items
        else:
            assert(len(sublist.items) > 1)
            assert(sublist.title is not None)
            # print(num+1, sublist.title + ":")
            # for nu, item in enumerate( sublist.items ):
                # print( " ", nu+1, "- " + item )

    method = get_method( txt )
    assert(method)
    for num, sublist in enumerate(method.sections):
    #     # Just single item
        if len(sublist.items) == 1:
            assert(sublist.title is None)
            # print(str(num+1)+")", sublist.items[0])
        # A sublist of items
        else:
            assert(len(sublist.items) > 1)
            assert(sublist.title is not None)
            # print(str(num+1)+")", sublist.title + ":")
            # for nu, item in enumerate( sublist.items ):
                # print( "   " + str(nu+1)+".", item )

    notes = get_notes( txt )
    if reqs.exp_notes_section:
        assert( notes is not None )
        expect_equal( len(notes), reqs.exp_notes_lines_count )
        assert( len(notes) == reqs.exp_notes_lines_count )
        for line in range( reqs.exp_notes_lines_count ):
            expect_equal( notes[line], reqs.exp_notes_lines[line] )
            assert( notes[line] == reqs.exp_notes_lines[line] )
    else:
        assert( notes is None )

    ref_title, ref_link = get_reference( txt )
    if reqs.exp_reference_section:
        expect_equal(ref_title, reqs.exp_reference_title)
        assert(ref_title == reqs.exp_reference_title)
        expect_equal(ref_link, reqs.exp_reference_link)
        assert(ref_link == reqs.exp_reference_link)
    else:
        assert( ref_title is None )
        assert( ref_link is None )

    tags = get_tags( txt )
    if reqs.exp_tag_section:
        assert( tags is not None )
        expect_equal( len(tags), reqs.exp_tag_lines_count )
        assert( len(tags) == reqs.exp_tag_lines_count )
        for line in range( reqs.exp_tag_lines_count ):
            expect_equal( tags[line], reqs.exp_tag_lines[line] )
            assert( tags[line] == reqs.exp_tag_lines[line] )
    else:
        assert( tags is None )

def workerFunction():
    print("Running tests..")

    # [test_recipe( recipe, requirements ) for recipe in test_recipes]
    test_recipe( FAKE_RECIPE_1, requirements )


if __name__ == "__main__":
    workerFunction()



