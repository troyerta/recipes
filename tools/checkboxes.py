import sys
import os
import re
import copy
from parser import *

rm_sidebar_regx = r'(?:.*sidebar.*contents.*\s)(^(?:.*\s)*?)\s*(?:\s*?<\/nav>$)'
# Can contain 1 or more <ul>..,/ul> pairings...
ing_html_regx = r'(?:.*header.*ingredients.*?\s)(^(?:.*?\s)*?)\s*(?:^<.*header.*(method|direction|directions).*$)'
# Grab this group 0
method_html_regx = r'(?:.*header.*(method|direction|directions).*?\s)(^(?:.*?\s)*)'

rm_notes_regx = r'(.*header.*[Nn]otes.*?\s^(?:.*?\s)*)'

# Then remove this group(1) from it:
rm_tags_regx = r'(.*header.*tags.*?\s^(?:.*?\s)*)'
# Then remove references group(0) from it:
rm_refs_regx = r'(.*header.*(?:refer|ack|source|credit).*?\s^(?:.*?\s)*)'


# target_file = "book/08-Curry/bengali-chicken-curry.html"
# target_file = "book/08-Curry/chicken-tikka-masala.html"

ids_on_page = list()

# Ensure the id is unique on the page
def gen_html_id():
	my_id = "chkbx_" + str( len(ids_on_page) + 1 )
	assert( my_id not in ids_on_page )
	ids_on_page.append( my_id )
	return my_id

def new_html_header2( name ):
	normalized1 = re.sub( r'[^a-zA-Z0-9:]', "-", name )
	normalized2 = re.sub( r'-+', "-", normalized1 ).lower()
	output = "<h2><a class=\"header\" href=\"#" + normalized2 + "\" id=\"" + normalized2 + "\">" + name + "</a></h2>"
	return output

def new_html_header4( name ):
	normalized1 = re.sub( r'[^a-zA-Z0-9:]', "-", name )
	normalized2 = re.sub( r'-+', "-", normalized1 ).lower()
	output = "<h4><a class=\"header\" href=\"#" + normalized2 + "\" id=\"" + normalized2 + "\">" + name + "</a></h4>"
	return output

def new_method_item_txt( step_num, input_str ):
	'''
	<ol start="2">
	<li>
	<input disabled="" type="checkbox" id="step-box" style="display:none" onclick="change(this)"/>
	<label for="step-box"> In a large bowl, combine the chicken, yogurt, half of the garlic, half of the ginger, and half of the spice mixture, reserving the rest for later. Stir, cover, and allow to marinate for at least 15 minutes, or overnight.</label>
	</li>
	</ol>
	'''
	new_id = gen_html_id()
	new_tag_contents = "<ol start=\"" + str(step_num) + "\">\n"
	new_tag_contents += "<li>\n"
	new_tag_contents += "<input disabled=\"\" type=\"checkbox\" id=\"" + new_id + "\" style=\"display:none\" onclick=\"methToggleHandler(this)\"/>\n"
	new_tag_contents += "<label for=\"" + new_id + "\"> " + input_str + "</label>\n"
	new_tag_contents += "</li>\n"
	new_tag_contents += "</ol>\n"
	new_tag_contents += "<hr />\n"
	return new_tag_contents

def new_ing_item_txt( input_str ):
	rst = gen_html_id()
	txt = str()
	txt += "<br>\n<input disabled=\"\" type=\"checkbox\" id=\"" + rst + "\" onclick=\"ingToggleHandler(this)" "\"/>\n"
	txt += "<label for=\"" + rst + "\"> " + input_str + "</label>\n"
	txt +=  "<br>\n"
	return txt

def read_file( target_file ):
	# Read in the entire html file
	with open(target_file, "r") as fi:
		return fi.read()

def rm_html_sidebar( html ):
	return re.sub( rm_sidebar_regx, "",  html, flags=re.MULTILINE )

def get_ing_section_text( html ):
	match = re.search( ing_html_regx, html, flags=re.MULTILINE )
	if match:
		return match.group(1)
	else:
		return match

def get_meth_section_text( html ):
	methods_to_end = re.search( method_html_regx, html, flags=re.MULTILINE )
	notes_removed = re.sub( rm_notes_regx, "", methods_to_end.group(0), flags=re.MULTILINE )
	tags_removed = re.sub( rm_tags_regx, "", notes_removed, flags=re.MULTILINE )
	refs_removed = re.sub( rm_refs_regx, "", tags_removed, flags=re.MULTILINE ).strip()
	return refs_removed

# def gen_fixed_ing_section( orig_section ):
# 	# Remove the <li> and <ul> tags so it's just <p> tags and <h> headers
# 	# Get a list of the paragraph tag matches
# 	li_tags_rm = re.sub( r'<\/?li>', "", orig_section, flags=re.MULTILINE )
# 	ul_tags_rm = re.sub( r'<\/?ul>', "", li_tags_rm, flags=re.MULTILINE )
# 	p_tags_rm = re.sub( r'<\/?p>', "", ul_tags_rm, flags=re.MULTILINE )
# 	p_tags_rm = re.sub( r'<\/?p>', "", ul_tags_rm, flags=re.MULTILINE )
# 	blank_lines_rm = re.sub( r'\s\s', "", p_tags_rm, flags=re.MULTILINE )
# 	print(blank_lines_rm)
# 	p_tag_matches = re.finditer( r'^([^<].*)$', blank_lines_rm, flags=re.MULTILINE )
# 	# sys.exit()
# 	# Get a working copy of the new ingredients section
# 	new_txt = copy.deepcopy(ul_tags_rm)
# 	for match in p_tag_matches:
# 		# print(match.group(1))
# 		new_item_txt = new_ing_item_txt( match.group(1) )
# 		new_txt = re.sub( re.escape(match.group(0)), new_item_txt, new_txt, count=1, flags=re.MULTILINE )
# 	# Find/replace the <p> items that are first in the list after each header tag
# 	# Remove the leading <br> from the first item after a header tag
# 	return re.sub( r'(<\/h(\d)>$\s*)(^<br>\n)', "\g<1>", new_txt, flags=re.MULTILINE )

def replace_ingredients( input_text, original_text, new_text ):
	# Find the original ingredients section text
	# Replace the original text in the ORIGINAL html text
	full_rgx = re.escape(original_text)
	full_match = re.search( full_rgx, input_text, flags=re.MULTILINE )
	if full_match:
		new_html = re.sub( full_rgx, new_text, input_text, flags=re.MULTILINE )
		return new_html
	else:
		print("Could not replace ingredients text")
		sys.exit(1)

# def gen_fixed_meth_section( orig_section ):
# 	# Create a working copy of the methods section, and replace list item match, one at a time
# 	method_item_txt = copy.deepcopy(orig_section)

# 	ul_tags_rm = re.sub( r'^<\/?ol>\s?', "", method_item_txt, flags=re.MULTILINE )
# 	method_matches = re.finditer( r'^<li>(.*)<\/li>$', ul_tags_rm, flags=re.MULTILINE )

# 	for match in method_matches:
# 		# print(match.group(1), match.group(0))
# 		new_item_txt = new_method_item_txt( match.group(1) )
# 		method_item_txt = re.sub( re.escape(match.group(1)), new_item_txt, method_item_txt, count=1, flags=re.MULTILINE )
# 	return method_item_txt

def replace_methods( input_text, original_text, new_text ):
	# Search for the original methods section in the html file, and replace it with the new section
	current_method_section_regx = re.escape(original_text)
	html_new_methods = str()
	full_match = re.search( current_method_section_regx, input_text, flags=re.MULTILINE )
	if full_match:
		new_html = re.sub( current_method_section_regx, new_text, input_text, flags=re.MULTILINE )
		return new_html
	else:
		print("Could not replace methods text")
		sys.exit(1)

def generate_html_checkboxes( target_md_file, target_html_file ):

	# Read in the ingredients
	md_txt = read_file( target_md_file )




	# Read in the html text
	html = read_file( target_html_file )

	# Remove sidebar to speed up regex searches for other sections
	html_no_sidebar = rm_html_sidebar( html )

	# Grab the ingredients section of the text
	orig_ing_section = get_ing_section_text( html_no_sidebar )
	if orig_ing_section is None:
		print( "warning: ingredient section not found in " + target_html_file )

	# Grab the methods section of the text
	orig_meth_section = get_meth_section_text( html_no_sidebar )

	'''
	Work on the ingredients section
	'''
	# Generate the new ingredient section text
	ing = get_ingredients( md_txt )
	# print(ing)
	new_ing_section = str()
	for sublist in ing.sublists:
		# print(sublist.title)
		# sys.exit()
		if sublist.title:
			new_ing_section += new_html_header4( sublist.title )
		for item in sublist.items:
			new_ing_section += new_ing_item_txt(item)
	# print(new_ing_section)

	# Replace the original html text, with a new ingredients section
	new_html = replace_ingredients( html, orig_ing_section, new_ing_section )


	'''
	Work on the methods section
	'''
	# Generate the new methods section text
	meth = get_method( md_txt )
	new_meth_section = new_html_header2("Method:")
	counter = 0
	for subsect in meth.sublists:
		if subsect.title:
			new_meth_section += new_html_header4( subsect.title )
		for step in subsect.items:
			counter += 1
			new_meth_section += new_method_item_txt( counter, step )
	# print(new_meth_section)

	# Get a new version of the new_html text, with a new methods section
	final_html = replace_methods( new_html, orig_meth_section, new_meth_section )

	with open(target_html_file, "w") as fi:
		fi.write( final_html )



# Work on a runner - which starts, monitors, and orders the preprocessing,
# the mdbook rendering, and postprocessing one step at a time, using separate processes, which
# can halt in case something returns a bad error code != 0

# Then everything will be "one-step" changes again. Even the git steps and deployment
# should move to the python script. Then the makefile just runs this python script.

# Or perhaps remove make entirely. Or does make stop automatically, if something returns not-zero?
