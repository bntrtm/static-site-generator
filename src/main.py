import os
import shutil

import argparse
parser = argparse.ArgumentParser()
#-dp DISABLE PRETTY PRINTING #
parser.add_argument("-bp", "--basepath", nargs=1, type=str, help="Configure custom basepath", default="/")
parser.add_argument("-p", "--pretty", help="Use pretty printing", action="store_true")
args = parser.parse_args()

from textnode import *
from htmlnode import *
from conversions import *
from generation import *

# save root, content, static, & docs directories for use in function definitions
root_dir = os.getcwd()
content_path = os.path.join(root_dir, 'content')
static_dir = os.path.join(root_dir, 'static')
docs_dir = os.path.join(root_dir, 'docs')
# save path to default template, located in the root directory
template_path = os.path.join(root_dir, 'template.html')


def copy_dir(from_dir, to_dir, b_clean=False):
    '''Copies the contents of one directory to another, deleting any existing destination directory, if desired.
    '''
    # check that the from_dir is valid and has files to work with
    if not os.path.exists(from_dir):
        raise ValueError(f'Copy-From directory "{from_dir}" does not exist.')
    # a list of paths within the "from_dir" directory that could be files, or directories themselves
    from_paths = os.listdir(from_dir)
    if len(from_paths) == 0:
        if b_clean:
            raise Exception(f'{from_dir} contains no files to copy!')
        print(f'{omit_cd(from_dir)} contains no files to copy. Skipping directory.')
        return
    # delete any existing to_dir if b_clean is true
    if b_clean:
        if os.path.exists(to_dir):
            shutil.rmtree(to_dir)
    # remake to_dir
    if not os.path.exists(to_dir):
        os.mkdir(to_dir)
    # here, we acknowledge that shutil.copytree exists, but use shutil.copy anyway, for recursion practice
    print(f'Copying contents of {omit_cd(from_dir)} to {omit_cd(to_dir)}...')
    for p in from_paths:
        new_from_path = os.path.join(from_dir, p)
        new_to_path = os.path.join(to_dir, p)
        if os.path.isfile(new_from_path):
            shutil.copy(new_from_path, new_to_path)
        else:
            # recursively copy over any subdirectories
            copy_dir(new_from_path, new_to_path)


def generate_pages_recursive(path, generate_dir):
    '''Generates webpages from given path

    Given a path, check that the path is an 'index.md' file. If so, use any relevant
    template to generate an 'index.html' file in the 'generate_dir/...'. If the path
    is a directory, recursively generates htmls from any paths within it.
    '''
    if not os.path.isfile(path):
        subpaths = os.listdir(path)
        if len(subpaths) > 0:
            for s in subpaths:
                generate_pages_recursive(os.path.join(path, s), generate_dir)
    if path.endswith('index.md'):
            # set the template path to default, located in the root directory
            template = template_path
            theoretical_template_path = os.path.join(os.path.dirname(path), 'template.html')
            if os.path.exists(theoretical_template_path):
                # if there exists a template more specific to this webpage, use that in lieu of default
                template = theoretical_template_path
            # set a generation path for 'index.html' in ./docs that mirrors 'index.md' seen in ./content
            relpath = os.path.dirname(path).replace(content_path, '').lstrip('/')
            generation_path = os.path.join(generate_dir, relpath, 'index.html')
            # Generate a page from ./content/.../index.md using ./template.html and write the result to ./docs/.../index.html
            generate_page(path, template, generation_path, basepath=args.basepath[0])

def main():
    print(args.basepath[0])
    copy_dir(static_dir, docs_dir, b_clean=True)
    # parse arguments to determine whether we should disable pretty printing
    HTMLNode.should_pretty_print = args.pretty
    if args.pretty:
        print(f'Using pretty printing...')
    # find all 'index.md' and relevant 'template.html' files in the content directory and generate 'index.html' files within the docs directory
    generate_pages_recursive(content_path, docs_dir)

main()