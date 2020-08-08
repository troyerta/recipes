#!./venv/bin/python3

import os
from os.path import isfile
import sys
import re
import copy
from parser import *
from test_requirements import *

SRC_DIR = "./test/fake_book_src"
TEST_RECIPES = "./test/fake_test_recipes"

# test_list = [
# os.path.join( TEST_RECIPES, "apple-pie.md" ),
# os.path.join( TEST_RECIPES, "apple-pie-compressed.md" ),
# os.path.join( TEST_RECIPES, "apple-pie-weirdly-spaced.md" )
# ]

# Expected value is a, tested value is b
def expect_equal( a, b, description:str="" ):
    if description != "":
        description += " "
    if a != b:
        print("\033[91m" + description + "FAIL: expected \033[93m\"" + str(b) + "\"\033[91m" + " but got \033[92m\"" + str(a) + "\"\033[00m")

def compare_multisections( expected_section, section_under_test ):
    assert(expected_section)
    expect_equal( expected_section.num_items(), section_under_test.num_items() )
    assert( expected_section.num_items() == section_under_test.num_items() )
    expect_equal( expected_section.num_sublists(), section_under_test.num_sublists() )
    assert( expected_section.num_sublists() == section_under_test.num_sublists() )

    # Make sure each sublist is correct
    for num, sublist in enumerate( expected_section.sublists ):
        expect_equal( len(sublist), len(section_under_test.sublists[num]) )
        assert( len(sublist) == len(section_under_test.sublists[num]) )

        if len(sublist.items) == 1:
            assert(sublist.title is None)
        else:
            assert(len(sublist.items) > 1)
            assert(sublist.title is not None)

        expect_equal( sublist.title, section_under_test.sublists[num].title )
        assert( sublist.title == section_under_test.sublists[num].title )
        for idx, item in enumerate( sublist.items ):
            # print("Testing", item, section_under_test.sublists[num].items[idx])
            expect_equal( item, section_under_test.sublists[num].items[idx] )
            assert( item == section_under_test.sublists[num].items[idx] )


def test_recipe( recipe_file: str(), reqs: TestRequirement):
    print("Testing", recipe_file)
    assert( isfile(recipe_file) )
    txt = None

    """
    File
    """
    with open( recipe_file, 'r') as f:
        txt = f.read()
    assert(txt)

    """
    Title
    """
    title = get_title( txt )
    assert(title)
    expect_equal( title, reqs.exp_title )
    assert( title == reqs.exp_title )

    """
    Image reference
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

    """
    Overview
    """
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

    """
    Ingredients
    """
    ingredients = get_ingredients( txt )
    expected_ings = reqs.exp_ingredients_sublists
    compare_multisections( expected_ings, ingredients )

    """
    Method
    """
    method = get_method( txt )
    expected_mthd = reqs.exp_method_sublists
    compare_multisections(expected_mthd, method)

    """
    Notes
    """
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

    """
    Recipe Reference / link
    """
    ref_title, ref_link = get_reference( txt )
    if reqs.exp_reference_section:
        expect_equal(ref_title, reqs.exp_reference_title)
        assert(ref_title == reqs.exp_reference_title)
        expect_equal(ref_link, reqs.exp_reference_link)
        assert(ref_link == reqs.exp_reference_link)
    else:
        assert( ref_title is None )
        assert( ref_link is None )

    """
    Tags
    """
    tags = get_tags( txt )
    if reqs.exp_tag_section:
        assert( tags is not None )
        expect_equal( len(tags), reqs.exp_tag_lines_count, "Num tags" )
        assert( len(tags) == reqs.exp_tag_lines_count )
        for line in range( reqs.exp_tag_lines_count ):
            expect_equal( tags[line], reqs.exp_tag_lines[line] )
            assert( tags[line] == reqs.exp_tag_lines[line] )
    else:
        assert( tags is None )

def workerFunction():
    print("Running tests..")

    requirements = TestRequirement( "./test/fake_test_recipes/apple-pie.md" )
    requirements.expect_title( "Apple Pie" )
    requirements.expect_img( "Apple Pie", "../assets/apple-pie.jpg" )
    requirements.expect_overview( [ "Yield: 4 servings",
                            "Prep Time: 15 mins",
                            "Cook Time: 20 mins"] )

    ing_first_sublist = Sublist( ["Flour for dough work surface"] )
    ing_second_sublist = Sublist( title = "Crust",
                                items = [
                                    "2 cups Flour",
                                    "2 eggs",
                                    "2 tps baking powder",
                                    "1 tsp salt",
                                    "1 cup water"
                                    ] )
    ing_third_sublist = Sublist( title = "Filling",
                                items = [
                                    "Some apples",
                                    "10 cups Sugar",
                                    "2 cups hot water",
                                    "Pinch of molasses"
                                    ] )
    ing_section = Section( sublists = [ing_first_sublist, ing_second_sublist, ing_third_sublist] )
    requirements.expect_ingredients( ing_section )

    mtd_first_sublist = Sublist( ["Preheat the oven to 42523 deg C"] )
    mtd_second_sublist = Sublist( title = "Crust",
                                items = [
                                    "Gather crust ingredients",
                                    "Mix them together",
                                    "Flatten out formed dough and knead it up"
                                    ] )
    mtd_third_sublist = Sublist( title = "Filling",
                                items = [
                                    "Mix filling ingredients together",
                                    "Dump them into the formed pie crust"
                                    ] )
    method_sect = Section( sublists = [mtd_first_sublist, mtd_second_sublist, mtd_third_sublist] )
    requirements.expect_method( method_sect )

    requirements.expect_notes( [ "You can add salt and pepper to the filling for even more flavor.",
                                "If you like it on the fruitier side, add more apples to the filling."] )

    requirements.expect_reference( ( "Apple Pie", "https://www.applepies.com/best-apple-pie" ) )

    requirements.expect_tags( [ "fruity", "verified" ] )

    modded_requirements = copy.deepcopy(requirements)
    modded_requirements.exp_img_section = False

    test_recipe( os.path.join( TEST_RECIPES, "apple-pie.md" ), requirements )
    test_recipe( os.path.join( TEST_RECIPES, "apple-pie-compressed.md" ), requirements )
    test_recipe( os.path.join( TEST_RECIPES, "apple-pie-weirdly-spaced.md" ), requirements )
    test_recipe( os.path.join( TEST_RECIPES, "apple-pie-no-img.md" ), modded_requirements )

if __name__ == "__main__":
    workerFunction()
