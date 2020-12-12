
class Char:
    # Single line walls:
    HLINE = 9472            # ─
    VLINE = 9474            # │
    NE = 9488               # ┐
    NW = 9484               # ┌
    SE = 9496               # ┘
    SW = 9492               # └

    # Single line vertical/horizontal junctions (T junctions):
    TEEW = 9508             # ┤
    TEEE = 9500             # ├
    TEEN = 9524             # ┴
    TEES = 9516             # ┬

    # Cross-junction between two single line walls:
    CROSS = 9532            # ┼

    # Double lines walls:
    DHLINE = 9552           # ═
    DVLINE = 9553           # ║
    DNE = 9559              # ╗
    DNW = 9556              # ╔
    DSE = 9565              # ╝
    DSW = 9562              # ╚

    # Double line vertical/horizontal junctions (T junctions):
    DTEEW = 9571            # ╣
    DTEEE = 9568            # ╠
    DTEEN = 9577            # ╩
    DTEES = 9574            # ╦

    # Cross-junction between two single line walls:
    DCROSS = 9580           # ╬

    # Block characters:
    BLOCK1 = 9617           # ░
    BLOCK2 = 9618           # ▒
    BLOCK3 = 9619           # ▓
    BLOCK4 = 9608           # █
    FULL_BLOCK = 9608       # █

    # Arrows:
    ARROW_N = 8593          # ↑
    ARROW_S = 8595          # ↓
    ARROW_E = 8594          # →
    ARROW_W = 8592          # ←

    # Arrows without tail:
    ARROW2_N = 9650         # ▲
    ARROW2_S = 9660         # ▼
    ARROW2_E = 9658         # ►
    ARROW2_W = 9668         # ◄

    # Double arrows:
    ARROW_H = 8596          # ↔
    DARROW_H = 8596         # ↔
    ARROW_V = 8597          # ↕
    DARROW_V = 8597         # ↕

    # GUI stuff:
    # TODO: Some tilesets might have different glyphs, not matchin original CP437 charset
    CHECKBOX_UNSET = 945    # α
    CHECKBOX_SET = 223      # ß
    RADIO_UNSET = 9675      # ○
    RADIO_SET = 9689        # ◙

    # Sub-pixel resolution kit:
    # NOTE: original CP437 characters / replaced by SUBP_* in some tilesets
    SUBP_NW = 915           # Γ / ▘
    SUBP_NE = 960           # π / ▝
    SUBP_N = 931            # Σ / ▀
    SUBP_SE = 963           # σ / ▗
    SUBP_DIAG = 181         # µ / ▚
    SUBP_E = 964            # τ / ▐
    SUBP_SW = 934           # Φ / ▖

    # NOTE: Present in original CP437 character set
    HALFBLOCK_S = 9604      # ▄
    HALFBLOCK_W = 9612      # ▌
    HALFBLOCK_E = 9616      # ▐
    HALFBLOCK_N = 9600      # ▀

    # NOTE: Used by console.draw_semigraphics() method even though not all present in CP437 tileset!
    # NOTE: All present in TCOD characterset
    SEMIGRAPH_NW = 9624     # ▘
    SEMIGRAPH_NE = 9629     # ▝
    SEMIGRAPH_N = 9600      # ▀
    SEMIGRAPH_SE = 9623     # ▗
    SEMIGRAPH_DIAG = 9626   # ▚
    SEMIGRAPH_E = 9616      # ▐
    SEMIGRAPH_SW = 9622     # ▖

    # Miscellaneous characters:
    SMILY = 9786            # ☺
    SMILY_INV = 9787        # ☻
    SMILIE = 9786           # ☺
    SMILIE_INV = 9787       # ☻

    HEART = 9829            # ♥
    DIAMOND = 9830          # ♦
    CLUB = 9827             # ♣
    SPADE = 9824            # ♠

    BULLET = 8226           # •
    BULLET_INV = 9688       # ◘

    MALE = 9794             # ♂
    FEMALE = 9792           # ♀

    NOTE = 9834             # ♪
    NOTE_DOUBLE = 9835      # ♫

    LIGHT = 9788            # ☼

    QUESTION_INV = 191      # ¿
    EXCLAM_INV = 161        # ¡
    EXCLAM_DOUBLE = 8252    # ‼
    PILCROW = 182           # ¶
    SECTION = 167           # §
    POUND = 163             # £
    MULTIPLICATION = 8359   # ₧
    FUNCTION = 402          # ƒ

    LAQUO = 171             # «
    RAQUO = 187             # »

    HALF = 189              # ½
    ONE_QUARTER = 188       # ¼

    GRADE = 176             # °
    DIVISION = 247          # ÷
    POW2 = 178              # ²
    TRIPLE_BAR = 8801       # ≡
    PLUS_MINUS = 171        # ±
    GREATER_EQUAL = 8805    # ≥
    LESS_EQUAL = 8804       # ≤
    APPROXIMATION = 247     # ≈

    BULLET_SQUARE = 9632    # ■
    
    # NOTE: These might not be consistent among all tilesets!
    RESERVED = 8976         # ⌐
    COPYRIGHT = 9557        # ╕
    CENT = 9564             # ╜
    YEN = 9563              # ╛
    CURRENCY = 9575         # ╧
    THREE_QUARTERS = 8804   # ≤
    UMLAUT = 8729           # ∙
    POW1 = 8730             # √
    POW3 = 8319             # ⁿ


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
