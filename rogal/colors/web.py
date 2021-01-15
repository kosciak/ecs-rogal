from .core import HEX
from .palette import ColorNames, ColorPalette


# Web colors
# Reference: https://en.wikipedia.org/wiki/Web_colors
WEB_COLORS = [
    # Base web colors
    HEX('#000000'), #   0 - black
    HEX('#800000'), #   1 - maroon
    HEX('#008000'), #   2 - green
    HEX('#808000'), #   3 - olive
    HEX('#000080'), #   4 - navy
    HEX('#800080'), #   5 - purple
    HEX('#008080'), #   6 - teal
    HEX('#C0C0C0'), #   7 - silver
    HEX('#808080'), #   8 - gray
    HEX('#FF0000'), #   9 - red
    HEX('#00FF00'), #  10 - lime
    HEX('#FFFF00'), #  11 - yellow
    HEX('#0000FF'), #  12 - blue
    HEX('#FF00FF'), #  13 - fuchsia
    HEX('#00FFFF'), #  14 - aqua
    HEX('#FFFFFF'), #  15 - white

    # Extended colors
    HEX('#F0F8FF'), #  16 - aliceblue
    HEX('#FAEBD7'), #  17 - antiquewhite
    HEX('#7FFFD4'), #  19 - aquamarine
    HEX('#F0FFFF'), #  20 - azure
    HEX('#F5F5DC'), #  21 - beige
    HEX('#FFE4C4'), #  22 - bisque
    HEX('#FFEBCD'), #  24 - blanchedalmond
    HEX('#8A2BE2'), #  26 - blueviolet
    HEX('#A52A2A'), #  27 - brown
    HEX('#DEB887'), #  28 - burlywood
    HEX('#5F9EA0'), #  29 - cadetblue
    HEX('#7FFF00'), #  30 - chartreuse
    HEX('#D2691E'), #  31 - chocolate
    HEX('#FF7F50'), #  32 - coral
    HEX('#6495ED'), #  33 - cornflowerblue
    HEX('#FFF8DC'), #  34 - cornsilk
    HEX('#DC143C'), #  35 - crimson
    HEX('#00FFFF'), #  36 - cyan
    HEX('#00008B'), #  37 - darkblue
    HEX('#008B8B'), #  38 - darkcyan
    HEX('#B8860B'), #  39 - darkgoldenrod
    HEX('#A9A9A9'), #  40 - darkgray
    HEX('#006400'), #  41 - darkgreen
    HEX('#A9A9A9'), #  42 - darkgrey
    HEX('#BDB76B'), #  43 - darkkhaki
    HEX('#8B008B'), #  44 - darkmagenta
    HEX('#556B2F'), #  45 - darkolivegreen
    HEX('#FF8C00'), #  46 - darkorange
    HEX('#9932CC'), #  47 - darkorchid
    HEX('#8B0000'), #  48 - darkred
    HEX('#E9967A'), #  49 - darksalmon
    HEX('#8FBC8F'), #  50 - darkseagreen
    HEX('#483D8B'), #  51 - darkslateblue
    HEX('#2F4F4F'), #  52 - darkslategray
    HEX('#2F4F4F'), #  53 - darkslategrey
    HEX('#00CED1'), #  54 - darkturquoise
    HEX('#9400D3'), #  55 - darkviolet
    HEX('#FF1493'), #  56 - deeppink
    HEX('#00BFFF'), #  57 - deepskyblue
    HEX('#696969'), #  58 - dimgray
    HEX('#696969'), #  59 - dimgrey
    HEX('#1E90FF'), #  60 - dodgerblue
    HEX('#B22222'), #  61 - firebrick
    HEX('#FFFAF0'), #  62 - floralwhite
    HEX('#228B22'), #  63 - forestgreen
    HEX('#DCDCDC'), #  65 - gainsboro
    HEX('#F8F8FF'), #  66 - ghostwhite
    HEX('#FFD700'), #  67 - gold
    HEX('#DAA520'), #  68 - goldenrod
    HEX('#ADFF2F'), #  71 - greenyellow
    HEX('#808080'), #  72 - grey
    HEX('#F0FFF0'), #  73 - honeydew
    HEX('#FF69B4'), #  74 - hotpink
    HEX('#CD5C5C'), #  75 - indianred
    HEX('#4B0082'), #  76 - indigo
    HEX('#FFFFF0'), #  77 - ivory
    HEX('#F0E68C'), #  78 - khaki
    HEX('#E6E6FA'), #  79 - lavender
    HEX('#FFF0F5'), #  80 - lavenderblush
    HEX('#7CFC00'), #  81 - lawngreen
    HEX('#FFFACD'), #  82 - lemonchiffon
    HEX('#ADD8E6'), #  83 - lightblue
    HEX('#F08080'), #  84 - lightcoral
    HEX('#E0FFFF'), #  85 - lightcyan
    HEX('#FAFAD2'), #  86 - lightgoldenrodyellow
    HEX('#D3D3D3'), #  87 - lightgray
    HEX('#90EE90'), #  88 - lightgreen
    HEX('#D3D3D3'), #  89 - lightgrey
    HEX('#FFB6C1'), #  90 - lightpink
    HEX('#FFA07A'), #  91 - lightsalmon
    HEX('#20B2AA'), #  92 - lightseagreen
    HEX('#87CEFA'), #  93 - lightskyblue
    HEX('#778899'), #  94 - lightslategray
    HEX('#778899'), #  95 - lightslategrey
    HEX('#B0C4DE'), #  96 - lightsteelblue
    HEX('#FFFFE0'), #  97 - lightyellow
    HEX('#32CD32'), #  99 - limegreen
    HEX('#FAF0E6'), # 100 - linen
    HEX('#FF00FF'), # 101 - magenta
    HEX('#66CDAA'), # 103 - mediumaquamarine
    HEX('#0000CD'), # 104 - mediumblue
    HEX('#BA55D3'), # 105 - mediumorchid
    HEX('#9370DB'), # 106 - mediumpurple
    HEX('#3CB371'), # 107 - mediumseagreen
    HEX('#7B68EE'), # 108 - mediumslateblue
    HEX('#00FA9A'), # 109 - mediumspringgreen
    HEX('#48D1CC'), # 110 - mediumturquoise
    HEX('#C71585'), # 111 - mediumvioletred
    HEX('#191970'), # 112 - midnightblue
    HEX('#F5FFFA'), # 113 - mintcream
    HEX('#FFE4E1'), # 114 - mistyrose
    HEX('#FFE4B5'), # 115 - moccasin
    HEX('#FFDEAD'), # 116 - navajowhite
    HEX('#FDF5E6'), # 118 - oldlace
    HEX('#6B8E23'), # 120 - olivedrab
    HEX('#FFA500'), # 121 - orange
    HEX('#FF4500'), # 122 - orangered
    HEX('#DA70D6'), # 123 - orchid
    HEX('#EEE8AA'), # 124 - palegoldenrod
    HEX('#98FB98'), # 125 - palegreen
    HEX('#AFEEEE'), # 126 - paleturquoise
    HEX('#DB7093'), # 127 - palevioletred
    HEX('#FFEFD5'), # 128 - papayawhip
    HEX('#FFDAB9'), # 129 - peachpuff
    HEX('#CD853F'), # 130 - peru
    HEX('#FFC0CB'), # 131 - pink
    HEX('#DDA0DD'), # 132 - plum
    HEX('#B0E0E6'), # 133 - powderblue
    HEX('#BC8F8F'), # 136 - rosybrown
    HEX('#4169E1'), # 137 - royalblue
    HEX('#8B4513'), # 138 - saddlebrown
    HEX('#FA8072'), # 139 - salmon
    HEX('#F4A460'), # 140 - sandybrown
    HEX('#2E8B57'), # 141 - seagreen
    HEX('#FFF5EE'), # 142 - seashell
    HEX('#A0522D'), # 143 - sienna
    HEX('#87CEEB'), # 145 - skyblue
    HEX('#6A5ACD'), # 146 - slateblue
    HEX('#708090'), # 147 - slategray
    HEX('#708090'), # 148 - slategrey
    HEX('#FFFAFA'), # 149 - snow
    HEX('#00FF7F'), # 150 - springgreen
    HEX('#4682B4'), # 151 - steelblue
    HEX('#D2B48C'), # 152 - tan
    HEX('#D8BFD8'), # 154 - thistle
    HEX('#FF6347'), # 155 - tomato
    HEX('#40E0D0'), # 156 - turquoise
    HEX('#EE82EE'), # 157 - violet
    HEX('#F5DEB3'), # 158 - wheat
    HEX('#F5F5F5'), # 160 - whitesmoke
    HEX('#9ACD32'), # 162 - yellowgreen
]


class WebColor(ColorNames):
    # Base web colors
    BLACK = 0
    MAROON = 1
    GREEN = 2
    OLIVE = 3
    NAVY = 4
    PURPLE = 5
    TEAL = 6
    SILVER = 7
    GRAY = 8
    RED = 9
    LIME = 10
    YELLOW = 11
    BLUE = 12
    FUCHSIA = 13
    AQUA = 14
    WHITE = 15

    # Extended colors
    ALICEBLUE = 16
    ANTIQUEWHITE = 17
    AQUAMARINE = 19
    AZURE = 20
    BEIGE = 21
    BISQUE = 22
    BLANCHEDALMOND = 24
    BLUEVIOLET = 26
    BROWN = 27
    BURLYWOOD = 28
    CADETBLUE = 29
    CHARTREUSE = 30
    CHOCOLATE = 31
    CORAL = 32
    CORNFLOWERBLUE = 33
    CORNSILK = 34
    CRIMSON = 35
    CYAN = 36
    DARKBLUE = 37
    DARKCYAN = 38
    DARKGOLDENROD = 39
    DARKGRAY = 40
    DARKGREEN = 41
    DARKGREY = 42
    DARKKHAKI = 43
    DARKMAGENTA = 44
    DARKOLIVEGREEN = 45
    DARKORANGE = 46
    DARKORCHID = 47
    DARKRED = 48
    DARKSALMON = 49
    DARKSEAGREEN = 50
    DARKSLATEBLUE = 51
    DARKSLATEGRAY = 52
    DARKSLATEGREY = 53
    DARKTURQUOISE = 54
    DARKVIOLET = 55
    DEEPPINK = 56
    DEEPSKYBLUE = 57
    DIMGRAY = 58
    DIMGREY = 59
    DODGERBLUE = 60
    FIREBRICK = 61
    FLORALWHITE = 62
    FORESTGREEN = 63
    GAINSBORO = 65
    GHOSTWHITE = 66
    GOLD = 67
    GOLDENROD = 68
    GREENYELLOW = 71
    GREY = 72
    HONEYDEW = 73
    HOTPINK = 74
    INDIANRED = 75
    INDIGO = 76
    IVORY = 77
    KHAKI = 78
    LAVENDER = 79
    LAVENDERBLUSH = 80
    LAWNGREEN = 81
    LEMONCHIFFON = 82
    LIGHTBLUE = 83
    LIGHTCORAL = 84
    LIGHTCYAN = 85
    LIGHTGOLDENRODYELLOW = 86
    LIGHTGRAY = 87
    LIGHTGREEN = 88
    LIGHTGREY = 89
    LIGHTPINK = 90
    LIGHTSALMON = 91
    LIGHTSEAGREEN = 92
    LIGHTSKYBLUE = 93
    LIGHTSLATEGRAY = 94
    LIGHTSLATEGREY = 95
    LIGHTSTEELBLUE = 96
    LIGHTYELLOW = 97
    LIMEGREEN = 99
    LINEN = 100
    MAGENTA = 101
    MEDIUMAQUAMARINE = 103
    MEDIUMBLUE = 104
    MEDIUMORCHID = 105
    MEDIUMPURPLE = 106
    MEDIUMSEAGREEN = 107
    MEDIUMSLATEBLUE = 108
    MEDIUMSPRINGGREEN = 109
    MEDIUMTURQUOISE = 110
    MEDIUMVIOLETRED = 111
    MIDNIGHTBLUE = 112
    MINTCREAM = 113
    MISTYROSE = 114
    MOCCASIN = 115
    NAVAJOWHITE = 116
    OLDLACE = 118
    OLIVEDRAB = 120
    ORANGE = 121
    ORANGERED = 122
    ORCHID = 123
    PALEGOLDENROD = 124
    PALEGREEN = 125
    PALETURQUOISE = 126
    PALEVIOLETRED = 127
    PAPAYAWHIP = 128
    PEACHPUFF = 129
    PERU = 130
    PINK = 131
    PLUM = 132
    POWDERBLUE = 133
    ROSYBROWN = 136
    ROYALBLUE = 137
    SADDLEBROWN = 138
    SALMON = 139
    SANDYBROWN = 140
    SEAGREEN = 141
    SEASHELL = 142
    SIENNA = 143
    SKYBLUE = 145
    SLATEBLUE = 146
    SLATEGRAY = 147
    SLATEGREY = 148
    SNOW = 149
    SPRINGGREEN = 150
    STEELBLUE = 151
    TAN = 152
    THISTLE = 154
    TOMATO = 155
    TURQUOISE = 156
    VIOLET = 157
    WHEAT = 158
    WHITESMOKE = 160
    YELLOWGREEN = 162


COLORS = WEB_COLORS
Color = WebColor


WEB = ColorPalette(
    name='Web colors',
    fg=WEB_COLORS[Color.WHITE],
    bg=WEB_COLORS[Color.BLACK],
    color_names=WebColor,
    colors=WEB_COLORS,
)

