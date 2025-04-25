import unittest
from textnode import *
from htmlnode import *
from conversions import *
from blocks import BlockType

class TestConversionsOnNodes(unittest.TestCase):
    def test_given_node(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '`', TextType.CODE)
        compare_against = [
        TextNode("This is text with a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" word", TextType.TEXT),
        ]

        self.assertEqual(new_nodes, compare_against)
    
    def test_raises_delimiter_exception(self):
        node1 = TextNode("This is text with a `code block' word", TextType.TEXT)
        node2 = TextNode("This is text with a `code block word", TextType.TEXT)
        with self.assertRaises(Exception):
            new_nodes = split_nodes_delimiter([node1, node2], '`', TextType.CODE)

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and _italic_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        self.assertEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_adds_non_text_type_and_multiple_blocks(self):
        node1 = TextNode("This is text with no special formatting", TextType.TEXT)
        node2 = TextNode("This is some bold text", TextType.BOLD)
        node3 = TextNode("This **is text** with **two separate** bold blocks", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2, node3], '**', TextType.BOLD)
        compare_against = [
        TextNode("This is text with no special formatting", TextType.TEXT),
        TextNode("This is some bold text", TextType.BOLD),
        TextNode("This ", TextType.TEXT),
        TextNode("is text", TextType.BOLD),
        TextNode(" with ", TextType.TEXT),
        TextNode("two separate", TextType.BOLD),
        TextNode(" bold blocks", TextType.TEXT)
        ]
        self.assertEqual(new_nodes, compare_against)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "I love Shrek memes. [Check this one out on Google Images!](https://www.google.com/search?sca_esv=622bcc00fce5d9ed&q=meme&udm=2&fbs=ABzOT_CWdhQLP1FcmU5B0fn3xuWpA-dk4wpBWOGsoR7DG5zJBuFKUuwGzOl4g2iN2Y9K8vVHXoU7bsT5GKiaQzCTkBGk2wFqe04jSpDqa2zA7E8ogR-USNvUq7PLX3U3MkT0hzqMSgu95wbLh6NS_4ULdjvcP_7iKS-Z9JxrMHOuiPe9_WCkkwTHdRjjC7MpZZilM74aWoXTuWRPI28vT4GhNodx9J54TA&sa=X&ved=2ahUKEwio48L5392MAxXKvokEHbALJ08QtKgLegQIDRAB&biw=1278&bih=1313&dpr=1#vhid=lW1I9I8qK7B4AM&vssid=mosaic)"
        )
        self.assertListEqual([("Check this one out on Google Images!", "https://www.google.com/search?sca_esv=622bcc00fce5d9ed&q=meme&udm=2&fbs=ABzOT_CWdhQLP1FcmU5B0fn3xuWpA-dk4wpBWOGsoR7DG5zJBuFKUuwGzOl4g2iN2Y9K8vVHXoU7bsT5GKiaQzCTkBGk2wFqe04jSpDqa2zA7E8ogR-USNvUq7PLX3U3MkT0hzqMSgu95wbLh6NS_4ULdjvcP_7iKS-Z9JxrMHOuiPe9_WCkkwTHdRjjC7MpZZilM74aWoXTuWRPI28vT4GhNodx9J54TA&sa=X&ved=2ahUKEwio48L5392MAxXKvokEHbALJ08QtKgLegQIDRAB&biw=1278&bih=1313&dpr=1#vhid=lW1I9I8qK7B4AM&vssid=mosaic")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        self.maxDiff = None
        node = TextNode(
            "Check out this link to a Shrek meme! [Click here to see it](https://www.tiktok.com/@markfuryz/video/7260505127180668165)! Trust me, bro, it's safe. [Here are some gifs, too.](https://tenor.com/search/shrek-meme-gifs)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Check out this link to a Shrek meme! ", TextType.TEXT),
                TextNode("Click here to see it", TextType.LINK, "https://www.tiktok.com/@markfuryz/video/7260505127180668165"),
                TextNode("! Trust me, bro, it's safe. ", TextType.TEXT),
                TextNode(
                    "Here are some gifs, too.", TextType.LINK, "https://tenor.com/search/shrek-meme-gifs"
                ),
            ],
            new_nodes,
        )
    
    def test_split_md_img_link_empty_text(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual = (new_nodes, [])
        new_nodes = split_nodes_link([node])
        self.assertListEqual = (new_nodes, [])
    
    def test_split_md_img_link_text_only(self):
        node = TextNode("Just plain text here", TextType.TEXT)
        # Should return the original node
        self.assertEqual(split_nodes_image([node]), [TextNode("Just plain text here", TextType.TEXT)])
    
    def test_malformed_syntax_split_link(self):
        node = TextNode("This has a [broken link](missing closing parenthesis", TextType.TEXT)
        self.assertEqual(len(split_nodes_link([node])), 1)
        # should just return the original node as the single element, since the link is broken
    
    def test_md_img_link_split_img_or_link_text_type(self):
        node1 = TextNode("Here are some gifs, too.", TextType.LINK, "https://tenor.com/search/shrek-meme-gifs")
        node2 = TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png")
        self.assertEqual(split_nodes_image([node1, node2])[0], node1)
        # because "node" is already of TexType.LINK, it should just be added to the resulting list.
        self.assertEqual(split_nodes_image([node1, node2])[1], node2)
        # because "node" is already of TexType.IMAGE, it should just be added to the resulting list.
    
    def test_text_to_textnodes(self):
        result = text_to_textnodes('This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)')
        answer_key = [
        TextNode("This is ", TextType.TEXT),
        TextNode("text", TextType.BOLD),
        TextNode(" with an ", TextType.TEXT),
        TextNode("italic", TextType.ITALIC),
        TextNode(" word and a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" and an ", TextType.TEXT),
        TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        TextNode(" and a ", TextType.TEXT),
        TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(result, answer_key)

class TestMarkdownToHTML(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
        
This is **bolded** paragraph




This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ]
        )

class TestConversionsOnBlocks(unittest.TestCase):
    def test_return_types(self):
        # test various heading blocks, accounting for typos, etc
        md_text = "#### this is a heading block"
        self.assertEqual(block_to_block_type(md_text), BlockType.HEADING) # SHOULD BE HEADING
        md_text = "# this is a heading block"
        self.assertEqual(block_to_block_type(md_text), BlockType.HEADING) # SHOULD BE HEADING
        md_text = "###### this is a heading block"
        self.assertEqual(block_to_block_type(md_text), BlockType.HEADING) # SHOULD BE HEADING
        md_text = "####### this was meant to be a heading block, but there's a typo in it"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.HEADING) # SHOULD NOT BE HEADING BLOCK;
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE PARAGRAPH BLOCK

        md_text = "```this is a code block ```"
        self.assertEqual(block_to_block_type(md_text), BlockType.CODE)
        md_text = "``` this is a code block ```"
        self.assertEqual(block_to_block_type(md_text), BlockType.CODE)
        md_text = "``` this is a code block\nit has two lines in it ```"
        self.assertEqual(block_to_block_type(md_text), BlockType.CODE)
        md_text = "`` this was meant to be a code block, but it has a typo in it ```"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.CODE) # SHOULD NOT BE A CODE BLOCK;
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK;

        md_text = ">this is a quote block\n>It has two lines in it"
        self.assertEqual(block_to_block_type(md_text), BlockType.QUOTE)
        md_text = ">this was meant to be a quote block\nbut the second line is missing a > character..."
        self.assertNotEqual(block_to_block_type(md_text), BlockType.QUOTE) # SHOULD NOT BE A QUOTE BLOCK;
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE PARAGRAPH BLOCK
        md_text = ">this is a one-line code block"
        self.assertEqual(block_to_block_type(md_text), BlockType.QUOTE)

        md_text = "- this is an unordered list\n- because each of the newlines begins with a dash\n- followed by space"
        self.assertEqual(block_to_block_type(md_text), BlockType.ULIST)
        md_text = "- this was meant to be an unordered list\n-but one of the newlines begins with a dash\n- not followed by space"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.ULIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK
        md_text = ". this is a paragraph block\n- because the writer mixed up\n. the list syntax"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.ULIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK
        
        
        md_text = "1. this is an ordered list\n2. because each of the newlines begins with a sequential digit and period\n3. that is followed by space"
        self.assertEqual(block_to_block_type(md_text), BlockType.OLIST)
        md_text = "1. this was meant to be an ordered list\n2.but one of the newlines begins with a sequential digit and period\n3. not followed by space"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.OLIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK
        md_text = "1. this was meant to be an ordered list\n. but one of the newlines is missing its\n3. a sequential digit!"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.OLIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK
        md_text = "1. this was meant to be an ordered list\n3. but one of the newlines has the wrong\n2. a sequential digit!"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.OLIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK
        md_text = ". this is a paragraph block\n- because the writer mixed up\n. the list syntax"
        self.assertNotEqual(block_to_block_type(md_text), BlockType.OLIST)
        self.assertEqual(block_to_block_type(md_text), BlockType.PARAGRAPH) # RATHER, SHOULD BE A PARAGRAPH BLOCK

class TestFullMarkdownConversions(unittest.TestCase):
    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and _more_ items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_code(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()