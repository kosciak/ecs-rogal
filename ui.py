class AbstractDrawable:

    """Representation of rectangle area of tcod.Console.

    Allows manipulation of data using local coordinates (relative to self).

    """

    def __init__(self, parent, x, y, width=None, height=None):
        self.parent = parent
        # Coordinates relative to parent
        self.x = x
        self.y = y
        # Dimensions
        self.width = width or parent.width
        self.height = height or parent.height

    def _translate_parent(self, x, y):
        """Translate coordinates relative to self, to coordinates relative to parent."""
        parent_x = self.x + x
        parent_y = self.y + y
        #print('_translate_parent:',x,y,'->',parent_x,parent_y, '?', self)
        return parent_x, parent_y

    def _translate_root(self, x, y):
        return self.parent._translate_root(self.x+x, self.y+y)

    # NOTE: Direct access to console.tiles, console.tiles_rgb fragments

    @property
    def tiles(self):
        """Translate coordinates relative to self, to coordinates relative to root."""
        return self.parent.tiles[self.x:self.x+self.width, self.y:self.y+self.height]

    @tiles.setter
    def tiles(self, tiles):
        self.parent.tiles[self.x:self.x+self.width, self.y:self.y+self.height] = tiles

    @property
    def tiles_rgb(self):
        return self.parent.tiles[self.x:self.x+self.width, self.y:self.y+self.height]

    @tiles_rgb.setter
    def tiles_rgb(self, tiles_rgb):
        self.parent.tiles_rgb[self.x:self.x+self.width, self.y:self.y+self.height] = tiles_rgb

    def __repr__(self):
        return f'<{self.__class__.__name__} x={self.x}, y={self.y}, width={self.width}, height={self.height}>'

    # NOTE: tcod.Console print/draw related methods:

    def put_char(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.put_char(parent_x, parent_y, *args, **kwargs)

    def print(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.print(parent_x, parent_y, *args, **kwargs)

    def print_box(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.print_box(parent_x, parent_y, *args, **kwargs)

    def draw_rect(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.draw_rect(parent_x, parent_y, *args, **kwargs)

    def draw_frame(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.draw_frame(parent_x, parent_y, *args, **kwargs)
    
    # Other methods

    def frame(self, *args, **kwargs):
        return self.draw_frame(0, 0, width=self.width, height=self.height, *args, **kwargs)

    def fill(self, char, *args, **kwargs):
        return self.draw_rect(0, 0, ch=ord(char), width=self.width, height=self.height, *args, **kwargs)


class Container(AbstractDrawable):
    pass

class HorizontalContainer(Container):

    def split(self, height, top=None, bottom=None):
        if top:
            top = Panel(
                self, 
                0, 0, 
                self.width, self.height-height,
            )
            bottom = Panel(
                self, 
                0, self.height-height, 
                self.width, height,
            )
            return top, bottom
        elif bottom:
            top = Panel(
                self, 
                0, 0,
                self.width, height,
            )
            bottom = Panel(
                self, 
                0, height,
                self.width, self.height-height,
            )
            return top, bottom


class VerticalContainer(Container):

    def split(self, width, left=None, right=None):
        if left:
            left = Panel(
                self, 
                0, 0,
                self.width-width, self.height,
            )
            right = Panel(
                self, 
                self.width-width, 0, 
                width, self.height,
            )
            return left, right
        elif right:
            left = Panel(
                self, 
                0, 0, 
                width, self.height,
            )
            right = Panel(
                self, 
                width, 0, 
                self.width-width, self.height,
            )
            return left, right


class Panel(AbstractDrawable):

    def _create_split_container(self, width, height):
        if width:
            container_cls = VerticalContainer
        elif height:
            container_cls = HorizontalContainer
        container = container_cls(
            isinstance(self, RootPanel) and self or self.parent, 
            self.x, self.y,
            width=isinstance(self.parent, (Container, Frame)) and self.width or self.parent.width,
            height=isinstance(self.parent, (Container, Frame)) and self.height or self.parent.height,
        )
        return container

    def split(self, left=None, right=None, top=None, bottom=None):
        """Split Panel vertically or horizontally by providing width of new Panel
           placed to the right / left / top / bottom."""
        width = left or right
        height = top or bottom
        container = self._create_split_container(width, height)
        if width:
            return container.split(width, left=right and self, right=left and self)
        if height:
            return container.split(height, top=bottom and self, bottom=top and self)


class Frame(AbstractDrawable):
    # TODO: Setting title, adding buttons(?) on top/bottom border, scrollbars?
    #       For example setting things like: 
    #       .- Title ------[X]-.
    #       |                  |
    #       '-----------(more)-'
    pass


class Window:
    # TODO: For now it's just proof of concept
    # NOTE: splitting window.panel leaves original panel reference!

    def __init__(self, parent, x, y, width, height):
        self.frame = Frame(parent, x, y, width, height)
        self.frame.frame()
        self.panel = Panel(self.frame, 1, 1, width-2, height-2)

    def print(self, x, y, *args, **kwargs):
        return self.panel.print(x, y, *args, **kwargs)

    def print_box(self, x, y, *args, **kwargs):
        return self.panel.print_box(x, y, *args, **kwargs)

    def draw_rect(self, x, y, *args, **kwargs):
        return self.panel.draw_rect(x, y, *args, **kwargs)

    def draw_frame(self, x, y, *args, **kwargs):
        return self.panel.draw_frame(x, y, *args, **kwargs)

    def fill(self, char, *args, **kwargs):
        return self.panel.fill(char)


class RootPanel(Panel):

    def __init__(self, console):
        super().__init__(console, 0, 0)

    def _translate_root(self, x, y):
        return x, y

    def create_window(x, y, width, height):
        return Window(self, x, y, width, height)

    def clear(self, *args, **kwargs):
        return self.parent.clear(*args, **kwargs)


# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: Scrollable Panels?
# TODO: Window/Dialog?
# TODO: event handlers?
