
from parser import items

"""
This encapsulates a test recipe with the expected results of it's tests
"""
class TestRequirement:
    def __init__( self, recipe_file ):
        self.recipe_file = recipe_file
        self.exp_title = None

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

    def expect_title( self, title: str ):
        self.exp_title = title

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

    def expect_ingredients( self, ing_section ):
        self.exp_ingredients_sublists = ing_section
        self.exp_ingredients_sublist_count = ing_section.num_sublists()
        self.exp_ingredients_section_lines = list()

    def expect_method( self, method_section ):
        self.exp_method_sublists = method_section
        self.exp_method_sublist_count = method_section.num_sublists()
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
