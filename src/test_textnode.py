import unittest
from textnode import *


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_different_text(self):
        node = TextNode("This is a text node with lame text.", TextType.BOLD)
        node2 = TextNode("Boom! Bam! Alakazam!", TextType.BOLD)
        self.assertNotEqual(node, node2)
    
    def test_uneq_text_type(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
    
    def test_uneq_url(self):
        node = TextNode("This is a text node", TextType.TEXT, "https:://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertNotEqual(node, node2)
    
    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.TEXT, "https:://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.TEXT, "https:://www.boot.dev")
        self.assertEqual(node, node2)
    
    def test_repr(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")
        self.assertEqual(
            "TextNode(This is a text node, text, https://www.boot.dev)", repr(node)
        )
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_text_img_conversion(self):
        img_url = "https://preview.redd.it/something-always-has-to-go-wrong-with-it-v0-g1xbe9pwkg3d1.jpeg?auto=webp&s=a7e380424067fe8c2809bb2255c14d0dd4e057be"
        node = TextNode("Internet meme referencing hit franchise Shrek and financial ruin", TextType.IMAGE, img_url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node.to_html(),
            f'<img src="{img_url}" alt="Internet meme referencing hit franchise Shrek and financial ruin">'
        )
    
    def test_text_link_conversion(self):
        url = "https://youtu.be/r6-JlK04sDs?t=53"
        node = TextNode("Click here to see Turtle Boy dance!", TextType.LINK, url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node.to_html(),
            f'<a href="{url}">Click here to see Turtle Boy dance!</a>'
        )

if __name__ == "__main__":
    unittest.main()