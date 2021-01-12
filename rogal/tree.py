
class Tree:

    __slots__ = ('parent', 'children', )

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.children = []

    def clear(self):
        self.children = []

    @property
    def is_leaf(self):
        return not self.children

    def path(self):
        if self.parent:
            yield from self.parent.path()
        yield self

    @property
    def level(self):
        return len(list(self.path())) - 1

    def distance(self, other):
        path = set(self.path())
        other_path = set(other.path())
        common_parents = path & other_path
        if not common_parents:
            return None
        return len(path) + len(other_path) - 2*len(common_parents)

    def leaves(self):
        if self.is_leaf:
            yield self
        for child in self.children:
            if child is None:
                continue
            yield from child.leaves()

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

    def pprint_pre_order(self):
        for node in self.pre_order():
            print(f"{'  '*node.level}{node}")

    def pprint_post_order(self):
        for node in self.post_order():
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

    def pprint_in_order(self):
        for node in self.in_order():
            print(f"{'    '*node.level}{node}")

