import graphviz


class Node(graphviz.Node):
    def __init__(self, name, label, shape, color, style):
        self.name = name
        self.label = label
        self.shape = shape
        self.color = color
        self.style = style

    def __str__(self):
        return '{} [label="{}", shape={}, color={}, style={}];'.format(
            self.name, self.label, self.shape, self.color, self.style
        )


class Edge:
    def __init__(self, source, target, label, color, style):
        self.source = source
        self.target = target
        self.label = label
        self.color = color
        self.style = style

    def __str__(self):
        return '{} -> {} [label="{}", color={}, style={}];'.format(
            self.source, self.target, self.label, self.color, self.style
        )


class subgraph:
    def __init__(self, name, label, color, style):
        self.name = name
        self.label = label
        self.color = color
        self.style = style

    def __str__(self):
        return 'subgraph cluster_{} [label="{}", color={}, style={}];'.format(
            self.name, self.label, self.color, self.style
        )
