
import os
from os import listdir
from os.path import isdir, isfile
import sys
import re

def splitpath( path, maxdepth=20 ):
    (head, tail) = os.path.split(path)
    return splitpath(head, maxdepth - 1) + [tail] if maxdepth and head and head != path else [head or tail]

def title_from_path(path):
    num_temp = re.sub("\d+-", "", os.path.basename(path).title())
    with_temp = re.sub("With", "with", num_temp)
    and_temp = re.sub("And", "and", with_temp)
    return re.sub("-", " ", and_temp)

def dirfile_from_dir(dir):
    base = re.sub("\d+-", "", os.path.basename(dir).lower() + ".md")
    return os.path.join(dir, base)

def path_is_parent(parent_path, child_path):
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def recipe_line(path):
    file_base, ext = os.path.splitext(path)
    return "[" + title_from_path(file_base) + "](" + path + ")\n"

def path_rel_to_summary(path):
    path_list = splitpath(path)
    path_list.remove(path_list[1])
    return os.path.join(*path_list)

def order_files_then_dirs(dir, paths):
    files = [x for x in paths if isfile(os.path.join(dir, x))]
    dirs = [x for x in paths if isdir(os.path.join(dir, x))]
    files = sorted(files)
    dirs = sorted(dirs)
    return dirs + files

class Summary:
    def __init__( self, src_dir, dirfiles, prefix_pages, ignored_pages, ignored_dirs, suffix_pages ):
        self.src_dir = src_dir
        self.filename = "SUMMARY.md"
        self.target_summary = os.path.join( src_dir, self.filename )
        self.dirfiles = dirfiles # [os.path.basename(path) for path in dirfiles]
        self.prefix_pages = [os.path.basename(path) for path in prefix_pages]
        self.suffix_pages = [os.path.basename(path) for path in suffix_pages]
        self.ignored_dirs = [os.path.basename(path) for path in ignored_dirs]
        self.ignored_pages = sorted( ignored_dirs + ignored_pages + prefix_pages + suffix_pages )
        self.ignored = [os.path.basename(item) for item in self.ignored_pages] + [self.filename]
        self.suffix_pages = suffix_pages

        # Make a complete list of all files ask the tree function to ignore
        self.prefix_relpaths = list()
        self.suffix_relpaths = list()
        self.ignored_file_relpaths = list()
        self.ignored_dirs_relpaths = list()

    def print_summary_tree( self, dir, file, padding, fPadding, print_files, isLast, isFirst ):
        if not isFirst:
            dirfile = path_rel_to_summary(dirfile_from_dir(dir))
            file.write(fPadding[:-1] + "- [" + re.sub("-", " ", title_from_path(dir)) + "](" + dirfile + ")\n")

        items = []
        if print_files:
            items = listdir(dir)
            # Remove the ignored files and dirs
            items = [os.path.normpath(item) for item in items if item not in self.ignored]
            items = order_files_then_dirs(dir, items)
        # else:
        #     items = [x for x in listdir(dir) if isdir(dir + sep + x)]

        if not isFirst:
            padding = padding + "   "
            fPadding = fPadding + " "

        count = 0
        last = len(items) - 1
        for i, item in enumerate(items):
            count += 1
            path = os.path.join(dir, item)
            isLast = i == last
            if isdir(path):
                self.print_summary_tree(path, file, padding+" ", fPadding+" ", print_files, isLast, False )

            elif not path in self.dirfiles:
                    relpath = path_rel_to_summary(path)
                    file.write(fPadding + "- " + recipe_line(relpath))

    def print_summary( self, verbose=False ):
        with open( self.target_summary, "w" ) as summary:

            # Print file header
            summary.write(
                "# Summary - This file is automatically generated by " + \
                os.path.normpath(sys.argv[0]) + \
                " - do not edit\n\n"
                )

            # Then print the prefix pages
            for file in self.prefix_pages:
                summary.write( recipe_line(file) )

            # Then print the chapter files
            self.print_summary_tree(
                                self.src_dir,
                                summary,
                                "",
                                "",
                                True,
                                False,
                                True
                                )

            # Then print the suffix pages
            for file in self.suffix_pages:
                summary.write( recipe_line(file) )


