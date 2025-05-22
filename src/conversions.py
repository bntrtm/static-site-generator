import re
from textnode import *
from htmlnode import *
from enum import Enum

# ===================================
# ======== EXCLUSIVE CLASSES ========
# ===================================

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ULIST = "unordered_list"
    OLIST = "ordered_list"

# ==================================
# ======== HELPER FUNCTIONS ========
# ==================================

# returns a list of tuples, each containing two strings: (alt text, link_url)
def extract_markdown_images(md_text):
    md_images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", md_text)
    return md_images

# returns a list of tuples, each containing two strings: (anchor text, image_link)
def extract_markdown_links(md_text):
    md_links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", md_text)
    return md_links

# ===================================
# ========= NODE CONVERSION =========
# ===================================

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    '''Split a markdown block into multiple html blocks within the boundaries of a given delimiter

    The markdown block is interpreted as a TextNode with the enum text_type: TextType.TEXT.
    The 'html blocks' are TextNodes of TextType.TEXT OR of TextType.{?}, where '?' is dependent on
    a the input parameter text_type, which should be defined by what the corresponding delimiter is.
    '''
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT and delimiter in node.text:
            # if an odd number of the delimiter exists in a string, then one was left unclosed
            if node.text.count(delimiter) % 2 == 1:
                raise Exception(f"invalid Markdown syntax; ensure closing delimiter \" {delimiter} \" ")
            # REMEMBER: str.split() WILL create empty strings, and these must be kept! Just don't add them as nodes!
            text_bodies = node.text.split(delimiter)
            for i in range(0, len(text_bodies)):
                if text_bodies[i] != "":
                    # if the iteration is odd, then the delimiter wrapped this text in the node's text
                    new_text_type = TextType.TEXT if i % 2 == 0 else text_type
                    new_node = TextNode(text_bodies[i], new_text_type)
                    new_nodes.append(new_node)
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_image(old_nodes):
    '''Reinterprets markdown image syntax as HTML image syntax
    '''
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.IMAGE:
            new_nodes.append(node)
        images = extract_markdown_images(node.text)
        if len(images) != 0:
            s = node.text
            for i in images:
                # split 's' at each image
                image_alt = i[0]
                image_link = i[1]
                sections = s.split(f"![{image_alt}]({image_link})", 1)
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
                if len(sections) > 1:
                    s = sections[1]
                else:
                    s = ""
            if s != "":
                # if there's any text left...
                new_nodes.append(TextNode(s, TextType.TEXT))
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_link(old_nodes):
    '''Reinterprets markdown image syntax as HTML image syntax
    '''
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.LINK:
            new_nodes.append(node)
        links = extract_markdown_links(node.text)
        if len(links) != 0:
            s = node.text
            for l in links:
                # split 's' at each image
                anchor_text = l[0]
                link_url = l[1]
                sections = s.split(f"[{anchor_text}]({link_url})", 1)
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(anchor_text, TextType.LINK, link_url))
                if len(sections) > 1:
                    s = sections[1]
                else:
                    s = ""
            if s != "":
                # if there's any text left...
                new_nodes.append(TextNode(s, TextType.TEXT))
        else:
            new_nodes.append(node)
    return new_nodes

def text_to_textnodes(text):
    '''Interprets input text string as one giant TextNode of TextType.TEXT, then splits it into multiple TextNodes at images, links, & delimiters
    '''
    old_nodes = []
    old_nodes.append(TextNode(text, TextType.TEXT))
    
    # md images first, because they're just like links but with the ! before them
    old_nodes = split_nodes_image(old_nodes)
    # now we can do links
    old_nodes = split_nodes_link(old_nodes)
    # now bold first, since it uses 2 asterisks, while markdown uses one
    old_nodes = split_nodes_delimiter(old_nodes, '**', TextType.BOLD)
    # now italics; both the asterisk and underscore notations
    old_nodes = split_nodes_delimiter(old_nodes, '*', TextType.ITALIC)
    old_nodes = split_nodes_delimiter(old_nodes, '_', TextType.ITALIC)
    # finally, we can do code markdown
    old_nodes = split_nodes_delimiter(old_nodes, '`', TextType.CODE)
    return old_nodes

# ==================================
# ======== BLOCK CONVERSION ========
# ==================================

def block_to_block_type(md_block):
    '''Dependent on expected markdown conventions, interprets the enum BlockType of a markdown block
    '''
    if bool(re.search("#{1,6} ", md_block[0:7])):
        return BlockType.HEADING
    if md_block.startswith("```") and md_block.endswith("```"):
        return BlockType.CODE
    if all(list(map(lambda x: x.startswith('>'), md_block.split('\n')))):
        return BlockType.QUOTE
    if all(list(map(lambda x: x.startswith('- '), md_block.split('\n')))):
        return BlockType.ULIST
    if md_block.startswith("1. "):
        lines = md_block.split("\n")
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH

def block_to_block_text(md_block):
    '''Based on the input BlockType, removes markdown formatting from a markdown block to return the intended text value
    '''
    # determine block type
    block_type = block_to_block_type(md_block)
    match block_type:
        case BlockType.PARAGRAPH:
            # browsers will handle newlines
            return ' '.join(md_block.split('\n'))
        case BlockType.CODE:
            # newlines in code blocks must be preserved, but not the ones off the beginning and end
            # the following should skip the first three backticks ``` and first newline, and include characters all the way up to the final newline
            return md_block[4:-3]
            # return '\n'.join(list(map(lambda x: x.strip('`'), md_block.split('\n')))[1:-1:1])
        case BlockType.QUOTE:
            # browsers will render newlines where appropriate for quotes blocks, just like paragraph blocks 
            return ' '.join(list(map(lambda x: x.lstrip('> '), md_block.split('\n'))))
        case BlockType.HEADING:
            # Headings shouldn't have any newlines whatsoever to worry about
            return md_block.lstrip('# ')
            #return '\n'.join(list(map(lambda x: x.lstrip('# '), md_block.split('\n'))))
        case _:
            raise ValueError(f'Enum input "{block_type}" not valid for function "block_to_block_text"')

def generate_leaf_nodes_from_block_text(md_block_text):
    '''Given a markdown block, construct multiple HTMLNode objects to represent varying font styles or text formatting (italics, bold, lists, etc)
    
    This function is the equivalent to the boot.dev course's function: "text_to_children(text)".
    '''
    child_html_nodes = []
    text_nodes = text_to_textnodes(md_block_text)
    for node in text_nodes:
        child_html_nodes.append(text_node_to_html_node(node))
    return child_html_nodes
            
def block_to_html_node(md_block):
    '''Perform markdown-to-HTML conversion based on enum BlockType
    '''
    # determine block type
    block_type = block_to_block_type(md_block)
    match block_type:
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(md_block)
        case BlockType.CODE:
            return code_to_html_node(md_block)
        case BlockType.QUOTE:
            return quote_to_html_node(md_block)
        case BlockType.HEADING:
            return heading_to_html_node(md_block)
        case BlockType.ULIST:
            return ulist_to_html_node(md_block)
        case BlockType.OLIST:
            return olist_to_html_node(md_block)
        case _:
            raise ValueError(f'Enum input "{block_type}" not valid for function "block_to_html_node"')

def paragraph_to_html_node(block):
    block_text = block_to_block_text(block)
    node = ParentNode(tag="p", children=generate_leaf_nodes_from_block_text(block_text))
    return node

def code_to_html_node(block):
    block_text = block_to_block_text(block)
    node = ParentNode(tag="code", children=[text_node_to_html_node(TextNode(block_text, TextType.TEXT))])
    node_wrapped = ParentNode(tag="pre", children=[node])
    return node_wrapped

def quote_to_html_node(block):
    block_text = block_to_block_text(block)
    node = ParentNode(tag="blockquote", children=generate_leaf_nodes_from_block_text(block_text))
    return node

def heading_to_html_node(block):
    '''Return an HTML heading tag

    Input "block" must be of type BlockType.HEADING.
    The heading tag string is based on the number of leading '#' symbols
    '''
    def interpret_heading_size():
        return f"h{block[0:6].count('#')}"

    block_text = block_to_block_text(block)
    node = ParentNode(tag=interpret_heading_size(), children=generate_leaf_nodes_from_block_text(block_text))
    return node

def ulist_to_html_node(block):
    list_items = block.split('\n')
    html_items = []
    for item in list_items:
        item_text = item[2:]
        children = generate_leaf_nodes_from_block_text(item_text)
        html_items.append(ParentNode("li", children))
    node = ParentNode(tag="ul", children=html_items)
    return node

def olist_to_html_node(block):
    list_items = block.split('\n')
    html_items = []
    for item in list_items:
        item_text = item[3:]
        children = generate_leaf_nodes_from_block_text(item_text)
        html_items.append(ParentNode("li", children))
    node = ParentNode(tag="ol", children=html_items)
    return node


# =====================================
# ======== MARKDOWN CONVERSION ========
# =====================================

def markdown_to_blocks(md):
    '''Interpret every line break within a markdown document as a divisor between two 'markdown blocks'
    '''
    return list(filter(lambda x: x != '', list(map( lambda x: x.strip(), md.split('\n\n')))))

# converts a full markdown document into a single parent HTMLNode containing any relevant child ParentNode's and LeafNodes
def markdown_to_html_node(md):
    '''Top-level function generates HTMLNode given a markdown document 'md'

    1) Establishes an HTMLNode ParentNode object; all contents of the conversion will be placed within a <div></div> tag.
    2) Generates markdown blocks for the program to break down further for conversion.
    3) Returns a tree of HTMLNode objects representing all interpreted images, links, & text with appropriate emphasis.
    '''
    div_html = ParentNode("div", children=[], props=None, nest_depth=3)
    # generate blocks from the full doc
    blocks = markdown_to_blocks(md)
    for md_block in blocks:
        div_html.children.append(block_to_html_node(md_block))
    return div_html