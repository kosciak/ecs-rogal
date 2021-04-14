from .core import Glyph


class Symbol:
    NONE = Glyph(0)
    EMPTY = Glyph(0)

    # Single line walls:
    HLINE = Glyph(9472)            # ─
    VLINE = Glyph(9474)            # │
    NE = Glyph(9488)               # ┐
    SE = Glyph(9496)               # ┘
    NW = Glyph(9484)               # ┌
    SW = Glyph(9492)               # └

    # Single line vertical/horizontal junctions (T junctions):
    TEES = Glyph(9516)             # ┬
    TEEW = Glyph(9508)             # ┤
    TEEE = Glyph(9500)             # ├
    TEEN = Glyph(9524)             # ┴

    # Cross-junction between two single line walls:
    CROSS = Glyph(9532)            # ┼

    # Double lines walls:
    DHLINE = Glyph(9552)           # ═
    DVLINE = Glyph(9553)           # ║
    DNE = Glyph(9559)              # ╗
    DSE = Glyph(9565)              # ╝
    DNW = Glyph(9556)              # ╔
    DSW = Glyph(9562)              # ╚

    # Double line vertical/horizontal junctions (T junctions):
    DTEES = Glyph(9574)            # ╦
    DTEEW = Glyph(9571)            # ╣
    DTEEE = Glyph(9568)            # ╠
    DTEEN = Glyph(9577)            # ╩

    # Cross-junction between two single line walls:
    DCROSS = Glyph(9580)           # ╬

    # Single line horizontal / double line vertical
    SDNE = Glyph(9558)             # ╖
    SDSE = Glyph(9564)             # ╜
    SDNW = Glyph(9555)             # ╓
    SDSW = Glyph(9561)             # ╙

    SDTEES = Glyph(9573)           # ╥
    SDTEEW = Glyph(9570)           # ╢
    SDTEEE = Glyph(9567)           # ╟
    SDTEEN = Glyph(9576)           # ╨

    SDCROSS = Glyph(9579)          # ╫

    # Double line horizontal / single line vertical
    DSNE = Glyph(9557)             # ╕
    DSSE = Glyph(9563)             # ╛
    DSNW = Glyph(9554)             # ╒
    DSSW = Glyph(9560)             # ╘

    DSTEES = Glyph(9572)           # ╤
    DSTEEW = Glyph(9569)           # ╡
    DSTEEE = Glyph(9566)           # ╞
    DSTEEN = Glyph(9575)           # ╧

    DSCROSS = Glyph(9578)          # ╪

    # Block characters:
    BLOCK1 = Glyph(9617)           # ░
    BLOCK2 = Glyph(9618)           # ▒
    BLOCK3 = Glyph(9619)           # ▓
    BLOCK4 = Glyph(9608)           # █
    FULL_BLOCK = Glyph(9608)       # █

    # Arrows:
    ARROW_N = Glyph(8593)          # ↑
    ARROW_S = Glyph(8595)          # ↓
    ARROW_E = Glyph(8594)          # →
    ARROW_W = Glyph(8592)          # ←

    # Arrows without tail:
    ARROW2_N = Glyph(9650)         # ▲
    ARROW2_S = Glyph(9660)         # ▼
    ARROW2_E = Glyph(9658)         # ►
    ARROW2_W = Glyph(9668)         # ◄

    # Double arrows:
    ARROW_H = Glyph(8596)          # ↔
    DARROW_H = Glyph(8596)         # ↔
    ARROW_V = Glyph(8597)          # ↕
    DARROW_V = Glyph(8597)         # ↕

    # GUI stuff:
    # TODO: Some tilesets might have different glyphs, not matchin original CP437 charset
    CHECKBOX_UNSET = Glyph(945)    # α
    CHECKBOX_SET = Glyph(223)      # ß
    RADIO_UNSET = Glyph(9675)      # ○
    RADIO_SET = Glyph(9689)        # ◙

    # Sub-pixel resolution kit:
    # NOTE: original CP437 characters / replaced by SUBP_* in some tilesets
    SUBP_NW = Glyph(915)           # Γ / ▘
    SUBP_NE = Glyph(960)           # π / ▝
    SUBP_N = Glyph(931)            # Σ / ▀
    SUBP_SE = Glyph(963)           # σ / ▗
    SUBP_DIAG = Glyph(181)         # µ / ▚
    SUBP_E = Glyph(964)            # τ / ▐
    SUBP_SW = Glyph(934)           # Φ / ▖

    # NOTE: Present in original CP437 character set
    HALFBLOCK_S = Glyph(9604)      # ▄
    HALFBLOCK_W = Glyph(9612)      # ▌
    HALFBLOCK_E = Glyph(9616)      # ▐
    HALFBLOCK_N = Glyph(9600)      # ▀

    # NOTE: Used by console.draw_semigraphics() method even though not all present in CP437 tileset!
    # NOTE: All present in TCOD characterset
    SEMIGRAPH_NW = Glyph(9624)     # ▘
    SEMIGRAPH_NE = Glyph(9629)     # ▝
    SEMIGRAPH_N = Glyph(9600)      # ▀
    SEMIGRAPH_SE = Glyph(9623)     # ▗
    SEMIGRAPH_DIAG = Glyph(9626)   # ▚
    SEMIGRAPH_E = Glyph(9616)      # ▐
    SEMIGRAPH_SW = Glyph(9622)     # ▖

    # Miscellaneous characters:
    SMILY = Glyph(9786)            # ☺
    SMILY_INV = Glyph(9787)        # ☻
    SMILIE = Glyph(9786)           # ☺
    SMILIE_INV = Glyph(9787)       # ☻

    HEART = Glyph(9829)            # ♥
    DIAMOND = Glyph(9830)          # ♦
    CLUB = Glyph(9827)             # ♣
    SPADE = Glyph(9824)            # ♠

    BULLET = Glyph(8226)           # •
    BULLET_INV = Glyph(9688)       # ◘

    CIRCLE = Glyph(9675)           # ○
    CIRCLE_INV = Glyph(9689)       # ◙

    MALE = Glyph(9794)             # ♂
    FEMALE = Glyph(9792)           # ♀

    NOTE = Glyph(9834)             # ♪
    NOTE_DOUBLE = Glyph(9835)      # ♫

    LIGHT = Glyph(9788)            # ☼

    QUESTION_INV = Glyph(191)      # ¿
    EXCLAM_INV = Glyph(161)        # ¡
    EXCLAM_DOUBLE = Glyph(8252)    # ‼
    PILCROW = Glyph(182)           # ¶
    SECTION = Glyph(167)           # §
    POUND = Glyph(163)             # £
    MULTIPLICATION = Glyph(8359)   # ₧
    FUNCTION = Glyph(402)          # ƒ

    LAQUO = Glyph(171)             # «
    RAQUO = Glyph(187)             # »

    HALF = Glyph(189)              # ½
    ONE_QUARTER = Glyph(188)       # ¼

    GRADE = Glyph(176)             # °
    DIVISION = Glyph(247)          # ÷
    POW2 = Glyph(178)              # ²
    TRIPLE_BAR = Glyph(8801)       # ≡
    PLUS_MINUS = Glyph(171)        # ±
    GREATER_EQUAL = Glyph(8805)    # ≥
    LESS_EQUAL = Glyph(8804)       # ≤
    APPROXIMATION = Glyph(247)     # ≈

    DOT_OPERATOR = Glyph(8729)     # ∙
    MIDDLE_DOT = Glyph(183)        # ·

    BULLET_SQUARE = Glyph(9632)    # ■

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

    @classmethod
    def get(cls, name):
        if not isinstance(name, str):
            return name
        return getattr(cls, name, name)


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
