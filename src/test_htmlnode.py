import unittest
from htmlnode import *

class TestHTMLNode(unittest.TestCase):

    def test_parent_values(self):
        node = HTMLNode(
            "div",
            "I wish I could read",
        )
        self.assertEqual(
            node.tag,
            "div",
        )
        self.assertEqual(
            node.value,
            "I wish I could read",
        )
        self.assertEqual(
            node.children,
            None,
        )
        self.assertEqual(
            node.props,
            None,
        )
    
    def test_repr(self):
        node = HTMLNode(
        tag="h1",
        value="Welcome to Boot.Dev",
        # no children; we're using value
        props={
                "href": "https://www.google.com",
                "target": "_blank",
            }
        )
        self.assertEqual(
            "HTMLNode(h1, Welcome to Boot.Dev, None, {'href': 'https://www.google.com', 'target': '_blank'})",
              node.__repr__()
        )

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", props={"href" : "https://www.boot.dev"})
        self.assertEqual(node.to_html(), "<a href=\"https://www.boot.dev\">Click me!</a>")
    
    def test_leaf_no_tag(self):
        node = LeafNode(None, "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "This is a paragraph of text.")

    def test_leaf_val_error_raised(self):
        node = LeafNode("p", "")
        node2 = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()
            node2.to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_nested_parents(self):
        arbitrary_leaf_node = LeafNode("p", "Let's talk about backend development.")
        bad_parent_node_no_children = ParentNode("div", [])
        good_parent_has_child = ParentNode("div", [bad_parent_node_no_children, arbitrary_leaf_node])
        with self.assertRaises(ValueError):
            good_parent_has_child.to_html()
    
    # props should only exist within the tags of nodes that have defined props!
    def test_check_props_in_nested_nodes(self):
        li_node_1 = LeafNode("li", "Python")
        li_node_2 = LeafNode("li", "Go")
        li_node_3 = LeafNode("li", "Rust")
        ul_node = ParentNode("ul", [li_node_1, li_node_2, li_node_3], props={"style" : "list-style-type:circle"})
        p_node = LeafNode("p", "Here are some languages that a backend developer might use in their career:")
        a_node = LeafNode("a", "Get studying now!", props={"href" : "https://www.boot.dev"})
        h1_node = LeafNode("h1", "Backend Languages")
        body_parent_node = ParentNode("body", [h1_node, p_node, ul_node, a_node])
        
        self.assertEqual(body_parent_node.children[0].props, None)
        self.assertEqual(body_parent_node.children[1].props, None)
        self.assertNotEqual(body_parent_node.children[2].props, None)
        self.assertEqual(body_parent_node.children[2].children[0].props, None)
        self.assertEqual(body_parent_node.children[2].children[1].props, None)
        self.assertEqual(body_parent_node.children[2].children[2].props, None)
        self.assertNotEqual(body_parent_node.children[3].props, None)
        self.maxDiff = None
        self.assertEqual(
            body_parent_node.to_html(),
            '<body><h1>Backend Languages</h1><p>Here are some languages that a backend developer might use in their career:</p><ul style="list-style-type:circle"><li>Python</li><li>Go</li><li>Rust</li></ul><a href="https://www.boot.dev">Get studying now!</a></body>'
        )
        


if __name__ == "__main__":
    unittest.main()