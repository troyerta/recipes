
"""
Regex notes:

Get recipe title
(?:^# (.*)\s+)

Get the img tag or whatever is between the title line and the next section
(?:^# .*\s*)(^(?:.*\s)*?)\s*(?:##[^#])

Get the overview section rows in a single group
(?:^## Overview\s+)(^(?:.*\s)*?)\s*(?:##[^#])

Get the entire ingredients sections, including blanks rows, and all sub lists of ingredients
(?:^## Ingredients\s+)(^(?:.*\s)*?)\s*(?:##[^#])

Get the entire methods section including blank rows, '---' rows, and sub method rows and titles
(?:^## Method\s+)(^(?:.*\s)*?)\s*(?:##[^#])

Get the Note section rows, including any blank lines
(?:^## Notes\s*)(^(?:.*\s)*?)\s*(?:##[^#])

Get the reference section, if it is named with "References" or with "Acknowledgements"
(?:^## (?:(?:Ref)|(?:Ack)).*\s*)(^(?:.*\s)*?)\s*(?:##[^#])

Get the tags section, including any blank lines. Must be last section
(?:^## Tags\s*)(^(?:.*\s)*)
















"""
