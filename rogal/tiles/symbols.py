from .core import Glyph


class Symbol:
    NONE = Glyph(0x0000)
    EMPTY = Glyph(0x0000)

    # Single line walls:
    HLINE = Glyph(0x2500)          # ─
    VLINE = Glyph(0x2502)          # │
    NE = Glyph(0x2510)             # ┐
    SE = Glyph(0x2518)             # ┘
    NW = Glyph(0x250c)             # ┌
    SW = Glyph(0x2514)             # └

    # Single line vertical/horizontal junctions (T junctions):
    TEES = Glyph(0x252c)           # ┬
    TEEW = Glyph(0x2524)           # ┤
    TEEE = Glyph(0x251c)           # ├
    TEEN = Glyph(0x2534)           # ┴

    # Cross-junction between two single line walls:
    CROSS = Glyph(0x253c)          # ┼

    # Double lines walls:
    DHLINE = Glyph(0x2550)         # ═
    DVLINE = Glyph(0x2551)         # ║
    DNE = Glyph(0x2557)            # ╗
    DSE = Glyph(0x255d)            # ╝
    DNW = Glyph(0x2554)            # ╔
    DSW = Glyph(0x255a)            # ╚

    # Double line vertical/horizontal junctions (T junctions):
    DTEES = Glyph(0x2566)          # ╦
    DTEEW = Glyph(0x2563)          # ╣
    DTEEE = Glyph(0x2560)          # ╠
    DTEEN = Glyph(0x2569)          # ╩

    # Cross-junction between two single line walls:
    DCROSS = Glyph(0x256c)         # ╬

    # Single line horizontal / double line vertical
    SDNE = Glyph(0x2556)           # ╖
    SDSE = Glyph(0x255c)           # ╜
    SDNW = Glyph(0x2553)           # ╓
    SDSW = Glyph(0x2559)           # ╙

    SDTEES = Glyph(0x2565)         # ╥
    SDTEEW = Glyph(0x2562)         # ╢
    SDTEEE = Glyph(0x255f)         # ╟
    SDTEEN = Glyph(0x2568)         # ╨

    SDCROSS = Glyph(0x256b)        # ╫

    # Double line horizontal / single line vertical
    DSNE = Glyph(0x2555)           # ╕
    DSSE = Glyph(0x255b)           # ╛
    DSNW = Glyph(0x2552)           # ╒
    DSSW = Glyph(0x2558)           # ╘

    DSTEES = Glyph(0x2564)         # ╤
    DSTEEW = Glyph(0x2561)         # ╡
    DSTEEE = Glyph(0x255e)         # ╞
    DSTEEN = Glyph(0x2567)         # ╧

    DSCROSS = Glyph(0x256a)        # ╪

    # Block characters:
    BLOCK1 = Glyph(0x2591)         # ░
    BLOCK2 = Glyph(0x2592)         # ▒
    BLOCK3 = Glyph(0x2593)         # ▓
    BLOCK4 = Glyph(0x2588)         # █
    FULL_BLOCK = Glyph(0x2588)     # █

    # Arrows:
    ARROW_N = Glyph(0x2191)        # ↑
    ARROW_S = Glyph(0x2193)        # ↓
    ARROW_E = Glyph(0x2192)        # →
    ARROW_W = Glyph(0x2190)        # ←

    # Arrows without tail:
    ARROW2_N = Glyph(0x25b2)       # ▲
    ARROW2_S = Glyph(0x25bc)       # ▼
    ARROW2_E = Glyph(0x25ba)       # ►
    ARROW2_W = Glyph(0x25c4)       # ◄

    # Double arrows:
    ARROW_H = Glyph(0x2194)        # ↔
    DARROW_H = Glyph(0x2194)       # ↔
    ARROW_V = Glyph(0x2195)        # ↕
    DARROW_V = Glyph(0x2195)       # ↕

    # GUI stuff:
    CHECKBOX_UNSET = Glyph(0x2610) # ☐
    CHECKBOX_SET = Glyph(0x2611)   # ☑
    RADIO_UNSET = Glyph(0x25cb)    # ○
    RADIO_SET = Glyph(0x25c9)      # ◉

    # Sub-pixel resolution kit:
    # NOTE: Present in original CP437 character set
    HALFBLOCK_S = Glyph(0x2584)    # ▄
    HALFBLOCK_W = Glyph(0x258c)    # ▌
    HALFBLOCK_E = Glyph(0x2590)    # ▐
    HALFBLOCK_N = Glyph(0x2580)    # ▀

    # NOTE: Used by console.draw_semigraphics() method even though not all present in CP437 tileset!
    # NOTE: All present in TCOD characterset
    SEMIGRAPH_S = Glyph(0x2584)    # ▄
    SEMIGRAPH_W = Glyph(0x258c)    # ▌
    SEMIGRAPH_E = Glyph(0x2590)    # ▐
    SEMIGRAPH_N = Glyph(0x2580)    # ▀

    SEMIGRAPH_NW = Glyph(0x2598)   # ▘
    SEMIGRAPH_NE = Glyph(0x259d)   # ▝
    SEMIGRAPH_SE = Glyph(0x2597)   # ▗
    SEMIGRAPH_SW = Glyph(0x2596)   # ▖

    SEMIGRAPH_DIAG = Glyph(0x259a) # ▚

    # Miscellaneous characters:
    SMILY = Glyph(0x263a)          # ☺
    SMILY_INV = Glyph(0x263b)      # ☻
    SMILIE = Glyph(0x263a)         # ☺
    SMILIE_INV = Glyph(0x263b)     # ☻

    HEART = Glyph(0x2665)          # ♥
    DIAMOND = Glyph(0x2666)        # ♦
    CLUB = Glyph(0x2663)           # ♣
    SPADE = Glyph(0x2660)          # ♠

    BULLET = Glyph(0x2022)         # •
    BULLET_INV = Glyph(0x25d8)     # ◘

    CIRCLE = Glyph(0x25cb)         # ○
    CIRCLE_INV = Glyph(0x25d9)     # ◙

    MALE = Glyph(0x2642)           # ♂
    FEMALE = Glyph(0x2640)         # ♀

    NOTE = Glyph(0x266a)           # ♪
    NOTE_DOUBLE = Glyph(0x266b)    # ♫

    LIGHT = Glyph(0x263c)          # ☼

    QUESTION_INV = Glyph(0x00bf)   # ¿
    EXCLAM_INV = Glyph(0x00a1)     # ¡
    EXCLAM_DOUBLE = Glyph(0x203c)  # ‼
    PILCROW = Glyph(0x00b6)        # ¶
    SECTION = Glyph(0x00a7)        # §
    POUND = Glyph(163)             # £
    MULTIPLICATION = Glyph(8359)   # ₧
    FUNCTION = Glyph(402)          # ƒ

    LAQUO = Glyph(0x00ab)          # «
    RAQUO = Glyph(0x00bb)          # »

    HALF = Glyph(0x00bd)           # ½
    ONE_QUARTER = Glyph(0x00bc)    # ¼

    GRADE = Glyph(0x00b0)          # °
    DIVISION = Glyph(0x00f7)       # ÷
    POW2 = Glyph(0x00b2)           # ²
    TRIPLE_BAR = Glyph(0x2229)     # ≡
    PLUS_MINUS = Glyph(0x00b1)     # ±
    GREATER_EQUAL = Glyph(0x2265)  # ≥
    LESS_EQUAL = Glyph(0x2264)     # ≤
    APPROXIMATION = Glyph(0x2248)  # ≈

    DOT_OPERATOR = Glyph(0x2219)   # ∙
    MIDDLE_DOT = Glyph(0x00b7)     # ·

    BULLET_SQUARE = Glyph(0x25a0)  # ■

    @classmethod
    def get(cls, name):
        if not isinstance(name, str):
            return name
        return getattr(cls, name, name)


class SymbolExtra(Symbol):

    # GUI stuff:
    CHECKBOX_UNSET = Glyph(945)    # α
    CHECKBOX_SET = Glyph(223)      # ß

    # NOTE: original CP437 characters / replaced by SUBP_* in some tilesets
    SUBP_NW = Glyph(915)           # Γ / ▘
    SUBP_NE = Glyph(960)           # π / ▝
    SUBP_N = Glyph(931)            # Σ / ▀
    SUBP_SE = Glyph(963)           # σ / ▗
    SUBP_DIAG = Glyph(181)         # µ / ▚
    SUBP_E = Glyph(964)            # τ / ▐
    SUBP_SW = Glyph(934)           # Φ / ▖

    # NOTE: These might not be consistent among all tilesets!
    RESERVED = Glyph(8976)         # ⌐
    COPYRIGHT = Glyph(9557)        # ╕
    CENT = Glyph(9564)             # ╜
    YEN = Glyph(9563)              # ╛
    CURRENCY = Glyph(9575)         # ╧
    THREE_QUARTERS = Glyph(8804)   # ≤
    UMLAUT = Glyph(8729)           # ∙
    POW1 = Glyph(8730)             # √
    POW3 = Glyph(8319)             # ⁿ


def show_charmap(charmap, columns=16):
    elements = []
    for ch in charmap:
        element = chr(ch)
        elements.append(element)
        if len(elements) == columns:
            print(' '.join(elements))
            elements = []
    if elements:
        print(' '.join(elements))


"""
CP437 charmap:
  ☺ ☻ ♥ ♦ ♣ ♠ • ◘ ○ ◙ ♂ ♀ ♪ ♫ ☼
► ◄ ↕ ‼ ¶ § ▬ ↨ ↑ ↓ → ← ∟ ↔ ▲ ▼
  ! " # $ % & ' ( ) * + , - . /
0 1 2 3 4 5 6 7 8 9 : ; < = > ?
@ A B C D E F G H I J K L M N O
P Q R S T U V W X Y Z [ \ ] ^ _
` a b c d e f g h i j k l m n o
p q r s t u v w x y z { | } ~
Ç ü é â ä à å ç ê ë è ï î ì Ä Å
É æ Æ ô ö ò û ù ÿ Ö Ü ¢ £ ¥ ₧ ƒ
á í ó ú ñ Ñ ª º ¿ ⌐ ¬ ½ ¼ ¡ « »
░ ▒ ▓ │ ┤ ╡ ╢ ╖ ╕ ╣ ║ ╗ ╝ ╜ ╛ ┐
└ ┴ ┬ ├ ─ ┼ ╞ ╟ ╚ ╔ ╩ ╦ ╠ ═ ╬ ╧
╨ ╤ ╥ ╙ ╘ ╒ ╓ ╫ ╪ ┘ ┌ █ ▄ ▌ ▐ ▀
α ß Γ π Σ σ µ τ Φ Θ Ω δ ∞ φ ε ∩
≡ ± ≥ ≤ ⌠ ⌡ ÷ ≈ ° ∙ · √ ⁿ ² ■ 

TCOD charmap:
  ! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; < = > ?
@ [ \ ] ^ _ ` { | } ~ ░ ▒ ▓ │ ─ ┼ ┤ ┴ ├ ┬ └ ┌ ┐ ┘ ▘ ▝ ▀ ▖ ▚ ▐ ▗
↑ ↓ ← → ▲ ▼ ◄ ► ↕ ↔ ☐ ☑ ○ ◉ ║ ═ ╬ ╣ ╩ ╠ ╦ ╚ ╔ ╗ ╝
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z

"""
