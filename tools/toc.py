import os
from os.path import isdir, isfile
import re
from summary import title_from_path

def produce_dirfile_name(dir):
    return os.path.join(dir, re.sub("\d+-", "", os.path.basename(dir).lower()) + ".md")

def print_subsection_link( file, path ):
    file.write(
        "["
        + re.sub("-", " ", title_from_path(path))
        + " --->](./"
        + produce_dirfile_name(path)
        + ")<br><br>\n"
    )

def print_recipe_link( file, path ):
    file_base, ext = os.path.splitext(path)
    file.write("[" + re.sub("-", " ", title_from_path(file_base)) + "](./" + path + ")<br><br>\n")

def print_parent_link( target_file, dirfile, chapter_dirs, about_file ):
    # If this is a chapter dirfile
    if os.path.dirname(dirfile) in chapter_dirs:
        target_file.write("[<--- Home](../" + os.path.basename(about_file) + ")\n\n")
    # This is a section dirfile
    else:
        # Get the path of the parent section/chapter
        # Get './src/09-Main-Dishes/' from './src/09-Main-Dishes/Thai/thai.md'
        par_dir = os.path.dirname(os.path.dirname(dirfile))

        # Get '09-Main-Dishes' from './src/09-Main-Dishes/Thai/thai.md'
        parent_base, ext = os.path.splitext(os.path.basename(par_dir))

        # Get that parent section/chapter's dirfile name
        # Get './src/main-dishes.md' from ./src/09-Main-Dishes/Thai/thai.md
        par_dirfile = produce_dirfile_name(par_dir)

        # Change '09-Main-Dishes' to 'Main Dishes', and './src/main-dishes.md' to '../main-dishes.md'
        # Write them to the top of the TOC as a "Back" or "Up" navigation target
        target_file.write("[<--- " + title_from_path(parent_base.title()) + "](../" + os.path.basename(par_dirfile) + ")\n\n")

def update_sub_level_toc( dirfile, chapter_dirs, about_file ):
    # Get ('thai', 'md') from 'thai.md'
    base, ext = os.path.splitext(os.path.basename(dirfile))

    with open( dirfile, "w" ) as fi:

        # Write a title line for the dirfile TOC page
        # Write "Thai" from "thai", or "Main Dishes" from "main-dishes.md"
        fi.write("# " + re.sub("-", " ", base.title()) + "\n\n")

        # Print the "Back" or "out" link
        print_parent_link( fi, dirfile, chapter_dirs, about_file )

        # Get all the files in the dirfile's directory
        dir_listing = os.listdir(os.path.dirname(dirfile))

        # Filter all the files to file_list
        file_list = [f for f in dir_listing if isfile(os.path.join(os.path.dirname(dirfile), f))]

        # Don't include the current dirfile in the TOC
        file_list.remove(os.path.basename(dirfile))
        file_list.sort()

        # Filter all the subsections/directories to dir_list
        dir_list = [f for f in dir_listing if isdir(os.path.join(os.path.dirname(dirfile), f))]
        dir_list.sort()

        # Print out the subsections first
        [print_subsection_link( fi, subsection ) for subsection in dir_list]

        # Then any recipes
        [print_recipe_link( fi, recipe ) for recipe in file_list]

def write_top_level_toc( chapter_dirs, target_file ):
    # print(chapter_dirs, target_file)
    with open( target_file, "w" ) as fi:
        fi.write( "# About\n\n" )

        """
        Write some tips and tools here if necessary
        """
        for ch in chapter_dirs:
            # Chapter dirs might already be prefixed with './'
            # Normalize, then prefix with './'
            # print(ch)
            rel_path = "./" + os.path.normpath(produce_dirfile_name(os.path.basename(ch)))
            # print(rel_path)
            fi.write("[" + re.sub("-", " ", title_from_path(ch)) + "](" + rel_path + ")<br><br>\n")
