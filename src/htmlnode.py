
class HTMLNode:
    """
    A class used to represent a single HTML element

    ...

    Attributes
    ----------
    should_pretty_print : bool
        a value dependnet on user input that determines whether or not the HTML result should be pretty printed, or in one line
    tag : str
        an enum type used to assign this HTMLNode a predefined set of behaviors
    value : str
        a string used by the node to display text, describe an image, or for some other such a purpose
    children : HTMLNode[]
        a list of HTMLNodes owned by and nested within this HTMLNode
    props : str[]
        a list of HTML attributes (properties) for this HTMLNode
    nest_depth : int
        a value representing how deeply this HTMLNode may be nested within others

    Methods
    -------
    to_html()
        A template method for returning a finalized HTML tag for use on a webpage

        _generate_html()
            A method for generating a valid HTML tag for use on a webpage
            
    props_to_html()
        Takes in a list of props and prepares them for use in an HTML tag
    """

    should_pretty_print = False


    def __init__(self, tag=None, value=None, children=None, props=None, nest_depth=0):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
        self.nest_depth = nest_depth

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

    def __eq__(self, other):
        return (
            self.tag == other.tag
            and self.value == other.value
            and self.children == other.children
            and self.props == other.props
        )


    def to_html(self):
        """A template method for returning a finalized HTML tag for use on a webpage.
        
        Takes in html generated from markdown with _generate_html, applies this HTMLNode's
        properties to the HTML tag where needed, and returns the result for use on a webpage.
        The purpose is purely to ensure that any relevant props are added to the opening tag
        of the generated HTML.

        Parameters ; None || Raises ; None
        """
        raw_html = self._generate_html(pretty=self.should_pretty_print)  # Subclasses implement this
        if self.tag and self.props:
            # replace the lead opening (or otherwise self-closing!) tag with itself, and the props
            return f'<{self.tag}{self.props_to_html()}' + raw_html.replace(f'<{self.tag}', '', 1)
        return raw_html

    def _generate_html(self, pretty=False):
        """A method for generating a valid HTML tag for use on a webpage
        
        Used internally within subclasses (hence the leading "_").
        In the LeafNode subclass, generation is as simple as closing content within tags.
        In the ParentNode subclass, generation must handle any relevant pretty printing,
        as well as recursively convert children to HTML, before returning a valid HTML tag.

        Parameters
        ----------
        pretty : bool, optional
            Whether or not the html should be generated in pretty-printed format

        Raises
        ------
        ValueError
            If, as a ParentNode, this HTMLNode has no children or has no tag
        NotImplementedError
            If called on the HTMLNode class directly, and not on a subclass
        """
        raise NotImplementedError("Subclasses must implement _generate_html")

    def props_to_html(self):
        attributes_s = ""
        for i in self.props:
            attributes_s += f' {i}="{self.props.get(i)}"'
        return attributes_s


class LeafNode(HTMLNode):
    '''A subclass of HTMLNode made to represent an HTML tag with a value, but no children
    '''
    def __init__(self, tag, value, props=None, nest_depth=1):
        super().__init__(tag=tag, value=value, children=None, props=props, nest_depth=nest_depth)
        # any tags in this given list will follow a <tag ...> structure
        self.__closes_self = tag in ["img", "br", "hr", "input", "meta", "link"]

    def _generate_html(self, pretty=False):
        if self.value == None:
            raise ValueError("all leaf nodes must have a value")
        if self.tag == None:
            return self.value
        if self.__closes_self:
            return f'<{self.tag}>'
        else:
            return f'<{self.tag}>{self.value}</{self.tag}>'


class ParentNode(HTMLNode):
    '''A type of HTMLNode representing an HTML tag with children, & therefore no value
    '''
    def __init__(self, tag, children, props=None, nest_depth=0):
        # Call parent constructor with no value
        super().__init__(tag=tag, value=None, children=children, props=props, nest_depth=nest_depth)
        if self.should_pretty_print == True:
            if len(self.children) > 0:
                for c in self.children:
                    c.nest_depth = self.nest_depth + 1

    def _generate_html(self, pretty=False):

        def prettify(child=None):
            '''Returns an indentation whose depth is 2 * nest_depth of the subject the (subject being self or child)
            '''
            if pretty is False:
                return ''
            if len(self.children) == 1 or self.tag == 'p' or self.tag == 'li':
                return ''
            target_depth = self.nest_depth if child is None else child.nest_depth
            indent = '\n'
            for i in range(0, target_depth + 1):
                indent += '  '
            return indent

        if self.tag ==  None:
            raise ValueError("ParentNode must have a tag")
        if self.children == None or len(self.children) == 0:
            raise ValueError("ParentNode must have one or more children")
        # generate an html string from children and wrap it in self.tag
        children_html = ''
        for child in self.children:
            children_html += prettify(child=child) + child.to_html()
        return f'<{self.tag}>{children_html}{prettify()}</{self.tag}>'