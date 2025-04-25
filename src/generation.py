import os
from conversions import markdown_to_html_node
from htmlnode import *

# rewrites the cwd within the input path as '.' if present, for easier reading
def omit_cd(path):
    return path.replace(os.getcwd(), '.')

def extract_title(md):
    h1_header = md.split('\n', 1)[0]
    if not h1_header.startswith('# '):
        raise Exception('The first line in the input markdown file must be an h1 header.')
    return h1_header.lstrip('#').strip()

# given an html file to use as a template, generates an HTML webpage using a markdown file and writes the result as dest_path.
def generate_page(from_path, template_path, dest_path, basepath="/"):
    # check that the directory for dest_path (the path of the file to write) exists.
    if not os.path.exists(os.path.dirname(dest_path)):
        print(f'Write-To directory "{os.path.dirname(dest_path)}" does not exist. Making relevant directories now...')
        os.makedirs(os.path.dirname(dest_path))
    print(f'Generating page from {omit_cd(from_path)} to {omit_cd(dest_path)} using {omit_cd(template_path)}.')
    with open(from_path, 'r') as file:
        md = file.read()
    HTML_template = open(template_path).read()
    HTML_content = markdown_to_html_node(md).to_html()
    HTML_page = HTML_template.replace('{{ Title }}', extract_title(md)).replace('{{ Content }}', HTML_content).replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
    with open(dest_path, 'w') as file:
        file.write(HTML_page)
    
