
class HTMLNode:
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
    

    # template method that ensures any relevant props are added to the leading tag
    def to_html(self):
        # Template method that handles props automatically
        raw_html = self._generate_html(pretty=self.should_pretty_print)  # Subclasses implement this
        if self.tag and self.props:
            # replace the leading opening (or otherwise self-closing!) tag with itself, and the props
            return f'<{self.tag}{self.props_to_html()}' + raw_html.replace(f'<{self.tag}', '', 1)
        return raw_html
        #raise NotImplementedError("to_html method not implemented")

    # NOTE TO SELF: leading "_" is a convention to mean this method is intended for internal use in subclasses
    def _generate_html(self, pretty=False):
        raise NotImplementedError("Subclasses must implement _generate_html")
    
    def props_to_html(self):
        attributes_s = ""
        for i in self.props:
            attributes_s += f' {i}="{self.props.get(i)}"'
        return attributes_s


# a type of HTMLNode representing an HTML tag with a value, but no children
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None, nest_depth=1):
        # Call parent constructor with no children
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

# a type of HTMLNode representing an HTML tag with children, & therefore no value
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None, nest_depth=0):
        # Call parent constructor with no value
        super().__init__(tag=tag, value=None, children=children, props=props, nest_depth=nest_depth)
        if self.should_pretty_print == True:
            if len(self.children) > 0:
                for c in self.children:
                    c.nest_depth = self.nest_depth + 1
        
    def _generate_html(self, pretty=False):
        
        # returns an indentation whose depth is 2 * nest_depth of the subject the (subject being self or child)
        def prettify(child=None):
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