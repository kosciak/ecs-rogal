class UnicodeBlock(tuple):

    __slots__ = ()

    def __new__(cls, start, end):
        return super().__new__(cls, range(start, end+1))


CP437 = [
    0x0000, # 
    0x263a, # ☺
    0x263b, # ☻
    0x2665, # ♥
    0x2666, # ♦
    0x2663, # ♣
    0x2660, # ♠
    0x2022, # •
    0x25d8, # ◘
    0x25cb, # ○
    0x25d9, # ◙
    0x2642, # ♂
    0x2640, # ♀
    0x266a, # ♪
    0x266b, # ♫
    0x263c, # ☼
    0x25ba, # ►
    0x25c4, # ◄
    0x2195, # ↕
    0x203c, # ‼
    0x00b6, # ¶
    0x00a7, # §
    0x25ac, # ▬
    0x21a8, # ↨
    0x2191, # ↑
    0x2193, # ↓
    0x2192, # →
    0x2190, # ←
    0x221f, # ∟
    0x2194, # ↔
    0x25b2, # ▲
    0x25bc, # ▼
    0x0020, #  
    0x0021, # !
    0x0022, # "
    0x0023, # #
    0x0024, # $
    0x0025, # %
    0x0026, # &
    0x0027, # '
    0x0028, # (
    0x0029, # )
    0x002a, # *
    0x002b, # +
    0x002c, # ,
    0x002d, # -
    0x002e, # .
    0x002f, # /
    0x0030, # 0
    0x0031, # 1
    0x0032, # 2
    0x0033, # 3
    0x0034, # 4
    0x0035, # 5
    0x0036, # 6
    0x0037, # 7
    0x0038, # 8
    0x0039, # 9
    0x003a, # :
    0x003b, # ;
    0x003c, # <
    0x003d, # =
    0x003e, # >
    0x003f, # ?
    0x0040, # @
    0x0041, # A
    0x0042, # B
    0x0043, # C
    0x0044, # D
    0x0045, # E
    0x0046, # F
    0x0047, # G
    0x0048, # H
    0x0049, # I
    0x004a, # J
    0x004b, # K
    0x004c, # L
    0x004d, # M
    0x004e, # N
    0x004f, # O
    0x0050, # P
    0x0051, # Q
    0x0052, # R
    0x0053, # S
    0x0054, # T
    0x0055, # U
    0x0056, # V
    0x0057, # W
    0x0058, # X
    0x0059, # Y
    0x005a, # Z
    0x005b, # [
    0x005c, # \
    0x005d, # ]
    0x005e, # ^
    0x005f, # _
    0x0060, # `
    0x0061, # a
    0x0062, # b
    0x0063, # c
    0x0064, # d
    0x0065, # e
    0x0066, # f
    0x0067, # g
    0x0068, # h
    0x0069, # i
    0x006a, # j
    0x006b, # k
    0x006c, # l
    0x006d, # m
    0x006e, # n
    0x006f, # o
    0x0070, # p
    0x0071, # q
    0x0072, # r
    0x0073, # s
    0x0074, # t
    0x0075, # u
    0x0076, # v
    0x0077, # w
    0x0078, # x
    0x0079, # y
    0x007a, # z
    0x007b, # {
    0x007c, # |
    0x007d, # }
    0x007e, # ~
    0x007f, # 
    0x00c7, # Ç
    0x00fc, # ü
    0x00e9, # é
    0x00e2, # â
    0x00e4, # ä
    0x00e0, # à
    0x00e5, # å
    0x00e7, # ç
    0x00ea, # ê
    0x00eb, # ë
    0x00e8, # è
    0x00ef, # ï
    0x00ee, # î
    0x00ec, # ì
    0x00c4, # Ä
    0x00c5, # Å
    0x00c9, # É
    0x00e6, # æ
    0x00c6, # Æ
    0x00f4, # ô
    0x00f6, # ö
    0x00f2, # ò
    0x00fb, # û
    0x00f9, # ù
    0x00ff, # ÿ
    0x00d6, # Ö
    0x00dc, # Ü
    0x00a2, # ¢
    0x00a3, # £
    0x00a5, # ¥
    0x20a7, # ₧
    0x0192, # ƒ
    0x00e1, # á
    0x00ed, # í
    0x00f3, # ó
    0x00fa, # ú
    0x00f1, # ñ
    0x00d1, # Ñ
    0x00aa, # ª
    0x00ba, # º
    0x00bf, # ¿
    0x2310, # ⌐
    0x00ac, # ¬
    0x00bd, # ½
    0x00bc, # ¼
    0x00a1, # ¡
    0x00ab, # «
    0x00bb, # »
    0x2591, # ░
    0x2592, # ▒
    0x2593, # ▓
    0x2502, # │
    0x2524, # ┤
    0x2561, # ╡
    0x2562, # ╢
    0x2556, # ╖
    0x2555, # ╕
    0x2563, # ╣
    0x2551, # ║
    0x2557, # ╗
    0x255d, # ╝
    0x255c, # ╜
    0x255b, # ╛
    0x2510, # ┐
    0x2514, # └
    0x2534, # ┴
    0x252c, # ┬
    0x251c, # ├
    0x2500, # ─
    0x253c, # ┼
    0x255e, # ╞
    0x255f, # ╟
    0x255a, # ╚
    0x2554, # ╔
    0x2569, # ╩
    0x2566, # ╦
    0x2560, # ╠
    0x2550, # ═
    0x256c, # ╬
    0x2567, # ╧
    0x2568, # ╨
    0x2564, # ╤
    0x2565, # ╥
    0x2559, # ╙
    0x2558, # ╘
    0x2552, # ╒
    0x2553, # ╓
    0x256b, # ╫
    0x256a, # ╪
    0x2518, # ┘
    0x250c, # ┌
    0x2588, # █
    0x2584, # ▄
    0x258c, # ▌
    0x2590, # ▐
    0x2580, # ▀
    0x03b1, # α
    0x00df, # ß
    0x0393, # Γ
    0x03c0, # π
    0x03a3, # Σ
    0x03c3, # σ
    0x00b5, # µ
    0x03c4, # τ
    0x03a6, # Φ
    0x0398, # Θ
    0x03a9, # Ω
    0x03b4, # δ
    0x221e, # ∞
    0x03c6, # φ
    0x03b5, # ε
    0x2229, # ∩
    0x2261, # ≡
    0x00b1, # ±
    0x2265, # ≥
    0x2264, # ≤
    0x2320, # ⌠
    0x2321, # ⌡
    0x00f7, # ÷
    0x2248, # ≈
    0x00b0, # °
    0x2219, # ∙
    0x00b7, # ·
    0x221a, # √
    0x207f, # ⁿ
    0x00b2, # ²
    0x25a0, # ■
    0x00a0, #  
]


TCOD = [
    0x0020, #  
    0x0021, # !
    0x0022, # "
    0x0023, # #
    0x0024, # $
    0x0025, # %
    0x0026, # &
    0x0027, # '
    0x0028, # (
    0x0029, # )
    0x002a, # *
    0x002b, # +
    0x002c, # ,
    0x002d, # -
    0x002e, # .
    0x002f, # /
    0x0030, # 0
    0x0031, # 1
    0x0032, # 2
    0x0033, # 3
    0x0034, # 4
    0x0035, # 5
    0x0036, # 6
    0x0037, # 7
    0x0038, # 8
    0x0039, # 9
    0x003a, # :
    0x003b, # ;
    0x003c, # <
    0x003d, # =
    0x003e, # >
    0x003f, # ?
    0x0040, # @
    0x005b, # [
    0x005c, # \
    0x005d, # ]
    0x005e, # ^
    0x005f, # _
    0x0060, # `
    0x007b, # {
    0x007c, # |
    0x007d, # }
    0x007e, # ~
    0x2591, # ░
    0x2592, # ▒
    0x2593, # ▓
    0x2502, # │
    0x2500, # ─
    0x253c, # ┼
    0x2524, # ┤
    0x2534, # ┴
    0x251c, # ├
    0x252c, # ┬
    0x2514, # └
    0x250c, # ┌
    0x2510, # ┐
    0x2518, # ┘
    0x2598, # ▘
    0x259d, # ▝
    0x2580, # ▀
    0x2596, # ▖
    0x259a, # ▚
    0x2590, # ▐
    0x2597, # ▗
    0x2191, # ↑
    0x2193, # ↓
    0x2190, # ←
    0x2192, # →
    0x25b2, # ▲
    0x25bc, # ▼
    0x25c4, # ◄
    0x25ba, # ►
    0x2195, # ↕
    0x2194, # ↔
    0x2610, # ☐
    0x2611, # ☑
    0x25cb, # ○
    0x25c9, # ◉
    0x2551, # ║
    0x2550, # ═
    0x256c, # ╬
    0x2563, # ╣
    0x2569, # ╩
    0x2560, # ╠
    0x2566, # ╦
    0x255a, # ╚
    0x2554, # ╔
    0x2557, # ╗
    0x255d, # ╝
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0041, # A
    0x0042, # B
    0x0043, # C
    0x0044, # D
    0x0045, # E
    0x0046, # F
    0x0047, # G
    0x0048, # H
    0x0049, # I
    0x004a, # J
    0x004b, # K
    0x004c, # L
    0x004d, # M
    0x004e, # N
    0x004f, # O
    0x0050, # P
    0x0051, # Q
    0x0052, # R
    0x0053, # S
    0x0054, # T
    0x0055, # U
    0x0056, # V
    0x0057, # W
    0x0058, # X
    0x0059, # Y
    0x005a, # Z
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0061, # a
    0x0062, # b
    0x0063, # c
    0x0064, # d
    0x0065, # e
    0x0066, # f
    0x0067, # g
    0x0068, # h
    0x0069, # i
    0x006a, # j
    0x006b, # k
    0x006c, # l
    0x006d, # m
    0x006e, # n
    0x006f, # o
    0x0070, # p
    0x0071, # q
    0x0072, # r
    0x0073, # s
    0x0074, # t
    0x0075, # u
    0x0076, # v
    0x0077, # w
    0x0078, # x
    0x0079, # y
    0x007a, # z
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
    0x0000, # 
]


# Unicode blocks - just some interesting blocks that might come handy
UNICODE_BASIC_LATIN =       UnicodeBlock(0x0000, 0x007f)

UNICODE_CURRENCY_SYMBOLS =  UnicodeBlock(0x20a0, 0x20cf)

UNICODE_ARROWS =            UnicodeBlock(0x2190, 0x21ff)

UNICODE_BOX_DRAWING =       UnicodeBlock(0x2500, 0x257f)
UNICODE_BLOCK_ELEMENTS =    UnicodeBlock(0x2580, 0x259f)
UNICODE_GEOMETRIC_SHAPES =  UnicodeBlock(0x25a0, 0x25ff)
UNICODE_MISC_SYMBOLS =      UnicodeBlock(0x2600, 0x26ff)
UNICODE_DINGBATS =          UnicodeBlock(0x2700, 0x27bf)

UNICODE_BRAILLE_PATTERNS =  UnicodeBlock(0x2800, 0x28ff)

