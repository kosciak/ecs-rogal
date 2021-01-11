
class Tree:

    __slots__ = ('parent', 'children', )

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.children = []

    def clear(self):
        self.children = []

    def path(self):
        if self.parent:
            yield from self.parent.path()
        yield self

    @property
    def level(self):
        return len(list(self.path())) - 1

    def pre_order(self):
        yield self
        for child in self.children:
            if child is None:
                continue
            yield from child.pre_order()

    def post_order(self):
        for child in self.children:
            if child is None:
                continue
            yield from child.post_order()
        yield self

    def pprint(self):
        for node in self.pre_order():
            print(f"{'  '*node.level}{node}")


class BinaryTree(Tree):

    __slots__ = ()

    @property
    def left(self):
        if self.children:
            return self.children[0]

    @left.setter
    def left(self, value):
        if len(self.children) < 2:
            self.children.extend([None, ]*(2-len(self.children)))
        self.children[0] = value
        value.parent = self

    @property
    def right(self):
        if len(self.children) > 1:
            return self.children[1]

    @right.setter
    def right(self, value):
        if len(self.children) < 2:
            self.children.extend([None, ]*(2-len(self.children)))
        self.children[1] = value
        value.parent = self

    def in_order(self):
        if self.left:
            yield from self.left.in_order()
        yield self
        if self.right:
            yield from self.right.in_order()

