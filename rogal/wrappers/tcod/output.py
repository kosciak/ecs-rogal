import logging

from ...console.core import Align
from ...console.consoles import RGBConsole
from ...console.panels import EMPTY_TILE, RootPanel

from ..core import OutputWrapper


log = logging.getLogger(__name__)


class TcodRootPanel(RootPanel):

    def __str__(self):
        return str(self.console)

    def clear(self, colors=None, *args, **kwargs):
        fg = self.get_color(colors and colors.fg) or self.colors_manager.palette.fg.rgb
        bg = self.get_color(colors and colors.bg) or self.colors_manager.palette.bg.rgb
        return self._clear(fg=fg, bg=bg, *args, **kwargs)

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        # NOTE: Do NOT change already set colors!
        fg = self.get_color(colors and colors.fg)
        bg = self.get_color(colors and colors.bg)
        align = align or Align.LEFT
        return self._print(
            position.x, position.y, text, fg=fg, bg=bg, alignment=align, *args, **kwargs)

    def draw(self, glyph, colors, position, size=None, *args, **kwargs):
        fg = self.get_color(colors and colors.fg)
        bg = self.get_color(colors and colors.bg)
        if size:
            return self._draw_rect(
                position.x, position.y, size.width, size.height,
                ch=glyph, fg=fg, bg=bg, *args, **kwargs)
        else:
            return self._print(
                position.x, position.y, glyph.char, fg=fg, bg=bg, *args, **kwargs)

    def image(self, image, position, *args, **kwargs):
        return self._draw_semigraphics(
            image, position.x, position.y, *args, **kwargs)

    # TODO: Needs rework using Position, Size!
    def blit_from(self, x, y, src, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: src MUST be tcod.Console!
        src.blit(dest=self.console, dest_x=x, dest_y=y, *args, **kwargs)

    def blit_to(self, x, y, dest, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: dest MUST be tcod.Console!
        self.console.blit(dest=dest, src_x=x, src_y=y, *args, **kwargs)

    # NOTE: tcod.Console print/draw related methods:

    def _put_char(self, x, y, ch, *args, **kwargs):
        """tcod.Console.put_char(
            x: int, y: int,
            ch: int,
            bg_blend: int = 13)
        """
        return self.console.put_char(x, y, ch, *args, **kwargs)

    def _print(self, x, y, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Cosole.print(
            x: int, y: int,
            string: str,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None,
            bg_blend: int = 1,
            alignment: int = 0)
        """
        return self.console.print(
            x, y, text, fg=fg, bg=bg, *args, **kwargs)

    def _print_box(self, x, y, width, height, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.print_box(
            x: int, y: int,
            width: int, height: int,
            string: str,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None,
            bg_blend: int = 1,
            alignment: int = 0)-> int
        """
        return self.console.print_box(
            x, y, width, height, text, fg=fg, bg=bg, *args, **kwargs)

    def _get_height_rect(self, x, y, width, height, text, *args, **kwargs):
        """tcod.Console.get_height_rect(
            x: int, y: int,
            width: int, height: int,
            string: str)-> int
        """
        return self.console.get_height_rect(
            x, y, width, height, text, *args, **kwargs)

    def _draw_rect(self, x, y, width, height, ch, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_rect(
            x: int, y: int,
            width: int, height: int,
            ch: int,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None,
            bg_blend: int = 1)
        """
        return self.console.draw_rect(
            x, y, width, height, ch, fg=fg, bg=bg, *args, **kwargs)

    def _draw_frame(self, x, y, width, height, title=None, clear=True, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_frame(
            x: int, y: int,
            width: int, height: int,
            title: str = '',
            clear: bool = True,
            fg: Optional[Tuple[int, int, int]] = None,
            bg: Optional[Tuple[int, int, int]] = None,
            bg_blend: int = 1)
        """
        title = title or ''
        return self.console.draw_frame(
            x, y, width, height, title=title, clear=clear, fg=fg, bg=bg, *args, **kwargs)

    def _draw_semigraphics(self, pixels, x, y, *args, **kwargs):
        """tcod.Console.draw_semigraphics(
            pixels: Any,
            x: int = 0,
            y: int = 0)
        """
        return self.console.get_height_rect(pixels, x, y, *args, **kwargs)

    def _clear(self, ch=None, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.clear(
            Tilech: int = 32,
            fg: Tuple[int, int, int] = Ellipsis,
            bg: Tuple[int, int, int] = Ellipsis)
        """
        ch = ch or EMPTY_TILE
        return self.console.clear(ch, fg=fg, bg=bg, *args, **kwargs)

    # blit(
    #   dest: tcod.console.Console,
    #   dest_x: int = 0, dest_y: int = 0,
    #   src_x: int = 0, src_y: int = 0,
    #   width: int = 0, height: int = 0,
    #   fg_alpha: float = 1.0,
    #   bg_alpha: float = 1.0,
    #   key_color: Optional[Tuple[int, int, int]] = None)

    def show(self):
        from ..term import ansi
        ansi.show_rgb_console(self.console)


class TcodOutputWrapper(OutputWrapper):

    ROOT_PANEL_CLS = TcodRootPanel

    def __init__(self, context, colors_manager):
        super().__init__(colors_manager)
        self.context = context

    def create_console(self, size):
        # TODO: Check options and resizing behaviour
        # NOTE: new_console returns console with order=="C"
        return self.context.new_console(*size)

    def render(self, panel):
        # TODO: Check options and resizing behaviour
        self.context.present(panel.console)


class TcodNaiveOutputWrapper(OutputWrapper):

    """Use RGBConsole and render using double buffering and prints."""

    CONSOLE_CLS = RGBConsole

    def __init__(self, context, colors_manager):
        super().__init__(colors_manager)
        self.context = context
        self.console = None
        self._prev_tiles = None

    def create_panel(self, size):
        console = self.create_console(size)
        if self.console is None:
            self.console = self.context.new_console(*size)
        return self.ROOT_PANEL_CLS(console, self.colors_manager)

    def render_whole(self, panel):
        for x, y, ch, fg, bg in panel.console.tiles_gen(encode_ch=chr):
            self.console.print(x, y, ch, fg=list(fg), bg=list(bg))

    def render_diff(self, panel):
        for x, y, ch, fg, bg in panel.console.tiles_diff_gen(self._prev_tiles, encode_ch=chr):
            self.console.print(x, y, ch, fg=list(fg), bg=list(bg))

    def render(self, panel):
        if self._prev_tiles is None or not self._prev_tiles.shape == panel.console.tiles.shape:
            self.render_whole(panel)
        else:
            self.render_diff(panel)

        self._prev_tiles = panel.console.tiles.copy()

        self.context.present(self.console)

