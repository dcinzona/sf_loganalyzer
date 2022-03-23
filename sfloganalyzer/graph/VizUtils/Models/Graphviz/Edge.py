class Edge(object):
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
