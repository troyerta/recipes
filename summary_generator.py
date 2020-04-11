#!/usr/bin/env python3

import sys
import os
from os import listdir, sep
from os.path import abspath, basename, isdir, isfile
import re
import shutil
import fnmatch

# Update the SUMMARY.md file according to the sorted contents found in src/

SRC_DIR = "src/src_sorted"
SRC_NEW = "src/src_renamed"

SUMMARY_PATH = "src/SUMMARY_new.md"

def usage():
    return '''Usage: %s [-f]
Print tree structure of path specified.
Options:
-f      Print files as well as directories
PATH    Path to process''' % basename(argv[0])

# f = open("summary_test.md", "w")
# f.write("Summary test!\n\n")

f = open("./src/SUMMARY.md", "w")
# f.write("# Summary2 test!\n\n")

def splitpath(path, maxdepth=20):
     ( head, tail ) = os.path.split(path)
     return splitpath(head, maxdepth - 1) + [ tail ] \
         if maxdepth and head and head != path \
         else [ head or tail ]

def produce_dirfile_name( dir ):
    return os.path.join( dir, re.sub( '\d+-', '', os.path.basename( dir ).lower() ) + ".md" )

def ensure_dirfile( dirfile ):
    # print("searching for file", dirfile)
    if( not isfile( dirfile ) ):
        base, ext = os.path.splitext( os.path.basename( dirfile ) )
        contents = re.sub('-', ' ', base.title() )
        # print("Creating", dirfile, "printing", "#", contents )
        with open( dirfile, 'w' ) as fi:
            fi.write( "# " + contents )
    # else:
        # print( "found", dirfile )

def title_from_path( path ):
    num_temp = re.sub('\d+-', '', os.path.basename( path ).title() )
    with_temp = re.sub('With', 'with', num_temp )
    and_temp = re.sub('And', 'and', with_temp )
    return re.sub('-', ' ', and_temp )

def dirfile_from_dir( dir ):
    base = re.sub( '\d+-', '', os.path.basename(dir).lower() + ".md" )
    return os.path.join( dir, base )

# def section_line( path ):
#     return "[" + title_from_path( path ) + "](" + path + ")\n"

def recipe_line( path ):
    file_base, ext = os.path.splitext( path )
    return "[" + title_from_path( file_base ) + "](" + path + ")\n"

# def write_ch_contents( file, chapter ):
#     pass

def path_rel_to_summary( path ):
    path_list = splitpath(path)
    path_list.remove( path_list[1] )
    return os.path.join( *path_list )

def order_files_then_dirs( dir, paths ):
    files = [x for x in paths if isfile( os.path.join( dir, x ) )]
    dirs = [x for x in paths if isdir( os.path.join( dir, x ) )]

    # print(paths)
    # print(files)
    # print(dirs)

    files = sorted(files)
    dirs = sorted(dirs)

    output = files + dirs
    return output

def print_tree( dir, padding, fPadding, chapter_dirs, section_dirs, dirfiles, recipes, about_file, print_files=False, isLast=False, isFirst=False,  ):
    if isFirst:
        pass
        # print( padding[:-1] + dir )
    else:
        dfile = path_rel_to_summary( dirfile_from_dir(dir) )
        # print(dfile)

        if isLast:
            # print( padding[:-1] + '└── ' + title_from_path(dir) )
            if dir in chapter_dirs:
                f.write( '\n# ' + title_from_path(dir) + "\n\n" )
            f.write( fPadding[:-1] + '- [' + re.sub( '-', ' ', title_from_path(dir) ) + '](' + dfile + ')\n' )
        else:
            # print( padding[:-1] + '├── ' + basename(abspath(dir)) )
            if dir in chapter_dirs:
                f.write( '\n# ' + title_from_path(dir) + "\n\n" )
            f.write( fPadding[:-1] + '- [' + re.sub( '-', ' ', title_from_path(dir) ) + '](' + dfile + ')\n' )
    files = []
    if print_files:
        files = listdir(dir)
    else:
        files = [x for x in listdir(dir) if isdir(dir + sep + x)]
    if not isFirst:
        padding = padding + '   '
        fPadding = fPadding + ' '
    # files = sorted(files, key=lambda s: s.lower())
    files = order_files_then_dirs( dir, files )

    # print(files)
    # print("")

    count = 0
    last = len(files) - 1
    for i, file in enumerate(files):
        count += 1
        path = os.path.join( dir, file )
        isLast = i == last  # Marks the last file in the entire list
        if isdir(path):
            if count == len(files):
                if isFirst:
                    print_tree(path, padding + ' ', fPadding + ' ', chapter_dirs, section_dirs, dirfiles, recipes, about_file, print_files, isLast, False )
                else:
                    print_tree(path, padding + ' ', fPadding + ' ', chapter_dirs, section_dirs, dirfiles, recipes, about_file, print_files, isLast, False )
            else:
                print_tree(path, padding + '│', fPadding + ' ', chapter_dirs, section_dirs, dirfiles, recipes, about_file, print_files, isLast, False )
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
                fpath = path_rel_to_summary( path )

                if path == about_file:
                    f.write( fPadding + recipe_line(fpath) )
                else:
                    f.write( fPadding + '- ' + recipe_line(fpath) )

def isDirFile(path, file):
    filename, ext = os.path.splitext(file)
    if( filename == os.path.basename(os.path.dirname(path)) ):
        return True
    # print("FN", filename, os.path.basename(os.path.dirname(path)))
    else:
        return False

# def tree():
#     path = './src/src_renamed'
#     if isdir(path):
#         print_tree( path, '', '', True, False, True )
#     else:
#         print( 'ERROR: \'' + path + '\' is not a directory' )

def get_all_things():
    rootpath = './src/recipes'
    rootpath_depth = len( splitpath( rootpath ) )

    root_list = list()
    dir_list = list()
    file_list = list()

    for root, dirs, files in os.walk(rootpath):
        # print( "root", root )
        root_list.append( root )
        for dir in dirs:
            # print( "dir", os.path.join(root, dir) )
            dir_list.append( os.path.join( root, dir ) )
        for file in files:
            # print( "file", os.path.join(root, file) )
            file_list.append( os.path.join( root, file ) )

    # print('')
    # [print(x) for x in dir_list]
    # print('')
    # [print(x) for x in file_list]
    # print('')

    # Create sorted lists: chapter_dirs, section_dirs, dirfiles, recipes
    chapter_dirs = list()
    section_dirs = list()
    dirfiles = list()
    recipes = list()

    # From the all_dirs list, get the dirs that start with a number, and are at a depth of 1
    # Add those dirs to the chapter_list, remove them from the all_dirs list
    for dir in dir_list:
        if( ( len( splitpath( dir ) ) - rootpath_depth ) == 1 ):
            chapter_dirs.append( dir )

    # [print(x) for x in chapter_dirs]
    [dir_list.remove(dir) for dir in chapter_dirs]
    [section_dirs.append(dir) for dir in dir_list]
    # print('')
    # [print(x) for x in section_dirs]

    # For each dir that exists, there must be a dirfile. Create it if it does not exist

    # For each dir in the chapter list, there must be a dirfile.
    # If it exists, remove it from the files list, add it to the dirfiles list
    # Else, create it if it does not exist, and add it to the dirfile list,

    for dir in chapter_dirs:
        dirfile = produce_dirfile_name( dir )
        ensure_dirfile( dirfile )
        dirfiles.append( dirfile )
    # print('')
    # [print(x) for x in dirfiles]

    # For each dir in the section list, there must be a dirfile. Create it if it does not exist
    # If it exists, remove it from the files list, add it to the dirfiles list
    # Else, create it if it does not exist, and add it to the dirfile list,

    for dir in section_dirs:
        dirfile = produce_dirfile_name( dir )
        ensure_dirfile( dirfile )
        dirfiles.append( dirfile )
    # print('')
    # [print(x) for x in section_dirs]

    # From the files list, make sure the about.md file exists, make it if it does not
    # Remove it from the files list otherwise
    about_file = os.path.join( rootpath, "about.md" )
    # print("About", about_file)
    if( about_file in file_list ):
        file_list.remove( about_file )
    else:
        print( "No about.md found. Generating", about_file )
        with open( about_file, 'w' ) as fi:
            fi.write( "# About" )

    # Add files from files list to the recipe list, if it is of a ".md" extension
    [recipes.append( path ) for path in file_list if path.endswith(".md") and path not in dirfiles]
    recipes = sorted(recipes)
    dirfiles = sorted( dirfiles )
    chapter_dirs = sorted( chapter_dirs )
    section_dirs = sorted( section_dirs )

    print( "Found", str(len(recipes)), "recipes in", str(len(chapter_dirs)), "chapters" )

    print('')
    [print(x) for x in chapter_dirs]
    # print('')
    # [print(x) for x in section_dirs]
    # print('')
    # [print(x) for x in dirfiles]
    # print('')
    # [print(x) for x in recipes]

    assert( len(dirfiles) == ( len( chapter_dirs ) + len( section_dirs ) ) )
    # f.write( "# Summary\n\n[About](./about.md)\n\n" )

    print_tree( rootpath, '', '', chapter_dirs, section_dirs, dirfiles, recipes, about_file, True, False, True )

    # for chapter in chapter_dirs:
        # Call a recursive thing to do the job
        # f.write( "# " + re.sub('\d+-', '', os.path.basename( chapter ).title() ) + "\n\n\n" )

def find_files( dir='.', glob=r'*' ):
    matches = list()

    for file in os.listdir( dir ):
        if fnmatch.fnmatch(file, glob):
            matches.append( file )
    # print(glob)
    # print(os.listdir( dir ))
    # print(matches)
    # sys.exit()

    if matches:
        return [os.path.join( dir, match ) for match in matches ]
    else:
        return list()

def rename_files():
    print("processing files" )

    # Get recipe name:
    file_list = find_files( dir=SRC_DIR, glob=r'*.md' )
    # print( file_list )

    for fi in file_list:
        basename = os.path.basename( fi )
        new_path = os.path.join( SRC_NEW, re.sub('ch\d*-\d*-', '', basename.lower() ) )
        shutil.copy(fi, new_path)

    sys.exit()

def workerFunction():
    # tree()
    get_all_things()
    # rename_files()

if __name__ == "__main__":
    workerFunction()

f.close()
