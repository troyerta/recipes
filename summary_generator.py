#!./venv/bin/python3

import sys
import os
from os import listdir, sep
from os.path import abspath, basename, isdir, isfile
import re
import shutil
import fnmatch


PHOTO_DIR = "./src/assets"
SUMMARY_PATH = "./src/SUMMARY.md"


f = open(SUMMARY_PATH, "w")


def splitpath(path, maxdepth=20):
    (head, tail) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [tail] if maxdepth and head and head != path else [head or tail]


def produce_dirfile_name(dir):
    return os.path.join(dir, re.sub("\d+-", "", os.path.basename(dir).lower()) + ".md")


def ensure_dirfile(dirfile):
    # print("searching for file", dirfile)
    if not isfile(dirfile):
        base, ext = os.path.splitext(os.path.basename(dirfile))
        contents = re.sub("-", " ", base.title())
        # print("Creating", dirfile, "printing", "#", contents )
        with open(dirfile, "w") as fi:
            fi.write("# " + contents)
    # else:
    # print( "found", dirfile )


def title_from_path(path):
    num_temp = re.sub("\d+-", "", os.path.basename(path).title())
    with_temp = re.sub("With", "with", num_temp)
    and_temp = re.sub("And", "and", with_temp)
    return re.sub("-", " ", and_temp)


def dirfile_from_dir(dir):
    base = re.sub("\d+-", "", os.path.basename(dir).lower() + ".md")
    return os.path.join(dir, base)


# def section_line( path ):
#     return "[" + title_from_path( path ) + "](" + path + ")\n"


def recipe_line(path):
    file_base, ext = os.path.splitext(path)
    return "[" + title_from_path(file_base) + "](" + path + ")\n"


# def write_ch_contents( file, chapter ):
#     pass


def path_rel_to_summary(path):
    path_list = splitpath(path)
    path_list.remove(path_list[1])
    return os.path.join(*path_list)


def order_files_then_dirs(dir, paths):
    files = [x for x in paths if isfile(os.path.join(dir, x))]
    dirs = [x for x in paths if isdir(os.path.join(dir, x))]

    # print(paths)
    # print(files)
    # print(dirs)

    files = sorted(files)
    dirs = sorted(dirs)

    output = files + dirs
    return output


def print_tree(
    dir,
    padding,
    fPadding,
    chapter_dirs,
    section_dirs,
    dirfiles,
    recipes,
    about_file,
    print_files=False,
    isLast=False,
    isFirst=False,
):
    if isFirst:
        pass
        # print( padding[:-1] + dir )
    else:
        dfile = path_rel_to_summary(dirfile_from_dir(dir))
        # print(dfile)

        if isLast:
            # print( padding[:-1] + '└── ' + title_from_path(dir) )
            if dir in chapter_dirs:
                f.write("\n# " + title_from_path(dir) + "\n\n")
            f.write(fPadding[:-1] + "- [" + re.sub("-", " ", title_from_path(dir)) + "](" + dfile + ")\n")
        else:
            # print( padding[:-1] + '├── ' + basename(abspath(dir)) )
            if dir in chapter_dirs:
                f.write("\n# " + title_from_path(dir) + "\n\n")
            f.write(fPadding[:-1] + "- [" + re.sub("-", " ", title_from_path(dir)) + "](" + dfile + ")\n")
    files = []
    if print_files:
        files = listdir(dir)
    else:
        files = [x for x in listdir(dir) if isdir(dir + sep + x)]
    if not isFirst:
        padding = padding + "   "
        fPadding = fPadding + " "
    # files = sorted(files, key=lambda s: s.lower())
    files = order_files_then_dirs(dir, files)

    # print(files)
    # print("")

    count = 0
    last = len(files) - 1
    for i, file in enumerate(files):
        count += 1
        path = os.path.join(dir, file)
        isLast = i == last  # Marks the last file in the entire list
        if isdir(path) and not path.startswith(PHOTO_DIR):
            # if isdir(path):
            if count == len(files):
                if isFirst:
                    print_tree(
                        path,
                        padding + " ",
                        fPadding + " ",
                        chapter_dirs,
                        section_dirs,
                        dirfiles,
                        recipes,
                        about_file,
                        print_files,
                        isLast,
                        False,
                    )
                else:
                    print_tree(
                        path,
                        padding + " ",
                        fPadding + " ",
                        chapter_dirs,
                        section_dirs,
                        dirfiles,
                        recipes,
                        about_file,
                        print_files,
                        isLast,
                        False,
                    )
            else:
                print_tree(
                    path,
                    padding + "│",
                    fPadding + " ",
                    chapter_dirs,
                    section_dirs,
                    dirfiles,
                    recipes,
                    about_file,
                    print_files,
                    isLast,
                    False,
                )
        else:
            if isLast:
                # print("printing", file)
                # if not isDirFile(path,file) and path != about_file:
                # print( padding + '└── ' + file )
                pass
            else:
                # print("printing", file)
                # if not isDirFile(path,file) and path != about_file:
                # print( padding + '├── ' + file )
                pass
            if not path in dirfiles:
                # fpath = os.path.join(path,file)
                fpath = path_rel_to_summary(path)

                if path == about_file:
                    f.write(fPadding + recipe_line(fpath))
                elif path == SUMMARY_PATH:
                    pass
                elif path.startswith(PHOTO_DIR):
                    pass
                else:
                    f.write(fPadding + "- " + recipe_line(fpath))


def isDirFile(path, file):
    filename, ext = os.path.splitext(file)
    if filename == os.path.basename(os.path.dirname(path)):
        return True
    # print("FN", filename, os.path.basename(os.path.dirname(path)))
    else:
        return False


def get_all_things():
    rootpath = "./src"
    rootpath_depth = len(splitpath(rootpath))

    root_list = list()
    dir_list = list()
    file_list = list()

    for root, dirs, files in os.walk(rootpath):
        # print( "root", root )
        root_list.append(root)
        for dir in dirs:
            # print( "dir", os.path.join(root, dir) )
            dir_list.append(os.path.join(root, dir))
        for file in files:
            # print( "file", os.path.join(root, file) )
            file_list.append(os.path.join(root, file))

    print("")
    [print(x) for x in dir_list]
    print("")
    [print(x) for x in file_list]
    print("")

    # Create sorted lists: chapter_dirs, section_dirs, dirfiles, recipes
    chapter_dirs = list()
    section_dirs = list()
    dirfiles = list()
    recipes = list()

    # From the all_dirs list, get the dirs that start with a number, and are at a depth of 1
    # Add those dirs to the chapter_list, remove them from the all_dirs list
    for dir in dir_list:
        if ((len(splitpath(dir)) - rootpath_depth) == 1) and not dir.startswith(PHOTO_DIR):
            chapter_dirs.append(dir)

    # [print(x) for x in chapter_dirs]
    [dir_list.remove(dir) for dir in chapter_dirs]
    [section_dirs.append(dir) for dir in dir_list if not dir.startswith(PHOTO_DIR)]
    # print('')
    # [print(x) for x in section_dirs]

    # For each dir that exists, there must be a dirfile. Create it if it does not exist

    # For each dir in the chapter list, there must be a dirfile.
    # If it exists, remove it from the files list, add it to the dirfiles list
    # Else, create it if it does not exist, and add it to the dirfile list,

    for dir in chapter_dirs:
        dirfile = produce_dirfile_name(dir)
        ensure_dirfile(dirfile)
        dirfiles.append(dirfile)
    # print('')
    # [print(x) for x in dirfiles]

    # For each dir in the section list, there must be a dirfile. Create it if it does not exist
    # If it exists, remove it from the files list, add it to the dirfiles list
    # Else, create it if it does not exist, and add it to the dirfile list,

    for dir in section_dirs:
        dirfile = produce_dirfile_name(dir)
        ensure_dirfile(dirfile)
        dirfiles.append(dirfile)
    # print('')
    # [print(x) for x in section_dirs]

    # From the files list, make sure the about.md file exists, make it if it does not
    # Remove it from the files list otherwise
    about_file = os.path.join(rootpath, "about.md")
    # print("About", about_file)
    if about_file in file_list:
        file_list.remove(about_file)
    # else:
    #     print( "No about.md found. Generating", about_file )
    #     with open( about_file, 'w' ) as fi:
    #         fi.write( "# About" )

    file_list.remove(SUMMARY_PATH)
    # [print(f) for f in file_list]

    # Add files from files list to the recipe list, if it is of a ".md" extension
    [recipes.append(path) for path in file_list if path.endswith(".md") and path not in dirfiles]
    recipes = sorted(recipes)
    dirfiles = sorted(dirfiles)
    chapter_dirs = sorted(chapter_dirs)
    section_dirs = sorted(section_dirs)

    print("Found", str(len(recipes)), "recipes in", str(len(chapter_dirs)), "chapters")

    # print('')
    # [print(x) for x in chapter_dirs]
    # print('')
    # [print(x) for x in section_dirs]
    # print('')
    # [print(x) for x in dirfiles]
    # print('')
    # [print(x) for x in recipes]

    assert len(dirfiles) == (len(chapter_dirs) + len(section_dirs))

    f.write(
        "# Summary - This file is automatically generated by " + os.path.normpath(sys.argv[0]) + " - do not edit\n\n"
    )

    print_tree(
        rootpath, "", "", chapter_dirs, section_dirs, dirfiles, recipes, about_file, True, False, True,
    )

    # Post process the Book

    # Generate TOCs for each Chapter and Section dirfile

    # If file is in chapter dir root, then back button should point back to about file
    # Else, point back up to the containing chapter or section dirfile
    ch = None
    # sect = None
    for dirfile in dirfiles:

        # ch will contain a result if this dirfile is a chapter dirfile
        ch = [dir for dir in chapter_dirs if os.path.dirname(dirfile) == dir]
        # print("")
        base, ext = os.path.splitext(os.path.basename(dirfile))
        contents = re.sub("-", " ", base.title())
        with open(dirfile, "w") as fi:
            fi.write("# " + contents + "\n\n")
            # print( "# " + contents + "\n" )

            if ch:
                fi.write("[<--- Home](../about.md)\n\n")
                # print( "[<--- Home](../about.md)" )

            else:
                # Get the pretty title of the parent section/chapter
                parent_base, ext = os.path.splitext(os.path.basename(os.path.dirname(os.path.dirname(dirfile))))
                # parent_base_pretty = re.sub('-', ' ', parent_base.title() )
                parent_base_pretty = title_from_path(parent_base.title())

                # Get that parent section/chapter's dirfile name
                par_dirfile = produce_dirfile_name(os.path.dirname(os.path.dirname(dirfile)))

                fi.write("[<--- " + parent_base_pretty + "](../" + os.path.basename(par_dirfile) + ")\n\n")
                # print( "[<--- " + parent_base_pretty + "](../" + os.path.basename(par_dirfile) + ")" )

            # Now print a TOC for the current chapter/section, just 1 layer deep is all
            # Each things is either a link to a file in the current dir
            # Or a link to a dirfile in a lower dir
            # Don't print a link to the dirfile of the current dir
            # print('')
            # print(dirfile)
            # print('')
            dir_listing = os.listdir(os.path.dirname(dirfile))

            # Get a sorted mini list of recipes - minus current dirfile
            curr_files = [f for f in dir_listing if isfile(os.path.join(os.path.dirname(dirfile), f))]
            curr_files.remove(os.path.basename(dirfile))
            curr_files.sort()
            # print(curr_files)

            # Get a list of the subsections
            curr_subsections = [f for f in dir_listing if isdir(os.path.join(os.path.dirname(dirfile), f))]
            curr_subsections.sort()
            # print(curr_subsections)

            for sub_sect in curr_subsections:
                # print( '- [' + re.sub( '-', ' ', title_from_path( sub_sect ) ) + '](./' + produce_dirfile_name( sub_sect ) + ')<br><br>\n' )
                fi.write(
                    "["
                    + re.sub("-", " ", title_from_path(sub_sect))
                    + " --->](./"
                    + produce_dirfile_name(sub_sect)
                    + ")<br><br>\n"
                )

            for curr_fi in curr_files:
                file_base, ext = os.path.splitext(curr_fi)
                # print( '- [' + re.sub( '-', ' ', title_from_path( file_base ) ) + '](./' + curr_fi + ')<br><br>\n' )
                fi.write("[" + re.sub("-", " ", title_from_path(file_base)) + "](./" + curr_fi + ")<br><br>\n")

    # Lastly, open the about.md file and make a TOC in it
    with open(about_file, "w") as fi:
        fi.write("# About\n\n")

        """
        Write some tips and tools here if necessary
        """

        for ch in chapter_dirs:
            rel_path = "./" + os.path.join(
                os.path.basename(ch), re.sub("\d+-", "", os.path.basename(ch).lower()) + ".md",
            )

            # print( '- [' + re.sub( '-', ' ', title_from_path( ch ) ) + '](' + produce_dirfile_name( ch ) + ')<br><br>\n' )
            fi.write("[" + re.sub("-", " ", title_from_path(ch)) + "](" + rel_path + ")<br><br>\n")


def workerFunction():
    get_all_things()


    if __name__ == "__main__":
        workerFunction()

f.close()
