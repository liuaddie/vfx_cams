#!/usr/bin/env python
#
# Find all HTML files in folder
# Convert into flask jinja template
#
import sys
import os
import re
import bs4

folder = sys.argv[1]

def update_txt(old, new):
    for tag in soup.find_all(text = re.compile(old)):
        updated_tag = tag.replace(old, new)
        tag.replace_with(updated_tag)

for file in os.listdir(folder):
    if file.endswith(".html"):
        # load html into bs4
        path = os.path.join(folder, file)
        with open(path) as html_in:
            html_txt = html_in.read()
            soup = bs4.BeautifulSoup(html_txt, "html.parser")

        # convert head css into flask static
        for css in soup.find("head").find_all("link", attrs={"rel": "stylesheet", "href": True}):
            css["href"] = "{begin} url_for('static', filename='{css_path}') {end}".format(css_path = css["href"], begin="{{", end="}}")

        # convert body script into flask static
        for js in soup.find("body").find_all("script", attrs={"src": True}):
            js["src"] = "{begin} url_for('static', filename='{js_path}') {end}".format(js_path = js["src"], begin="{{", end="}}")

        # Update text into variable
        update_txt("Z999", "{{id}}") # Z999 => id

        # save bs4 into html, ready for flash template
        with open(path, "w") as html_out:
            html_out.write(str(soup.prettify()))
