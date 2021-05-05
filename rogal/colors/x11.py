from .core import HEX
from .palette import ColorMap, ColorNames, ColorPalette


# X11 default colors
# Reference: https://jonasjacek.github.io/colors/
#            https://en.wikipedia.org/wiki/X11_color_names
X11_COLORS = [
    # System colors
    HEX('#000000'), #   0 - Black
    HEX('#800000'), #   1 - Maroon # TODO: #b03060
    HEX('#008000'), #   2 - Green
    HEX('#808000'), #   3 - Olive
    HEX('#000080'), #   4 - Navy
    HEX('#800080'), #   5 - Purple # TODO: #a020f0
    HEX('#008080'), #   6 - Teal
    HEX('#c0c0c0'), #   7 - Silver
    HEX('#808080'), #   8 - Grey # TODO: #bebebe
    HEX('#ff0000'), #   9 - Red
    HEX('#00ff00'), #  10 - Lime
    HEX('#ffff00'), #  11 - Yellow
    HEX('#0000ff'), #  12 - Blue
    HEX('#ff00ff'), #  13 - Fuchsia
    HEX('#00ffff'), #  14 - Aqua
    HEX('#ffffff'), #  15 - White

    # 216 ANSI colors
    HEX('#000000'), #  16 - Grey0
    HEX('#00005f'), #  17 - NavyBlue
    HEX('#000087'), #  18 - DarkBlue
    HEX('#0000af'), #  19 - Blue3
    HEX('#0000d7'), #  20 - Blue3
    HEX('#0000ff'), #  21 - Blue1
    HEX('#005f00'), #  22 - DarkGreen
    HEX('#005f5f'), #  23 - DeepSkyBlue4
    HEX('#005f87'), #  24 - DeepSkyBlue4
    HEX('#005faf'), #  25 - DeepSkyBlue4
    HEX('#005fd7'), #  26 - DodgerBlue3
    HEX('#005fff'), #  27 - DodgerBlue2
    HEX('#008700'), #  28 - Green4
    HEX('#00875f'), #  29 - SpringGreen4
    HEX('#008787'), #  30 - Turquoise4
    HEX('#0087af'), #  31 - DeepSkyBlue3
    HEX('#0087d7'), #  32 - DeepSkyBlue3
    HEX('#0087ff'), #  33 - DodgerBlue1
    HEX('#00af00'), #  34 - Green3
    HEX('#00af5f'), #  35 - SpringGreen3
    HEX('#00af87'), #  36 - DarkCyan
    HEX('#00afaf'), #  37 - LightSeaGreen
    HEX('#00afd7'), #  38 - DeepSkyBlue2
    HEX('#00afff'), #  39 - DeepSkyBlue1
    HEX('#00d700'), #  40 - Green3
    HEX('#00d75f'), #  41 - SpringGreen3
    HEX('#00d787'), #  42 - SpringGreen2
    HEX('#00d7af'), #  43 - Cyan3
    HEX('#00d7d7'), #  44 - DarkTurquoise
    HEX('#00d7ff'), #  45 - Turquoise2
    HEX('#00ff00'), #  46 - Green1
    HEX('#00ff5f'), #  47 - SpringGreen2
    HEX('#00ff87'), #  48 - SpringGreen1
    HEX('#00ffaf'), #  49 - MediumSpringGreen
    HEX('#00ffd7'), #  50 - Cyan2
    HEX('#00ffff'), #  51 - Cyan1
    HEX('#5f0000'), #  52 - DarkRed
    HEX('#5f005f'), #  53 - DeepPink4
    HEX('#5f0087'), #  54 - Purple4
    HEX('#5f00af'), #  55 - Purple4
    HEX('#5f00d7'), #  56 - Purple3
    HEX('#5f00ff'), #  57 - BlueViolet
    HEX('#5f5f00'), #  58 - Orange4
    HEX('#5f5f5f'), #  59 - Grey37
    HEX('#5f5f87'), #  60 - MediumPurple4
    HEX('#5f5faf'), #  61 - SlateBlue3
    HEX('#5f5fd7'), #  62 - SlateBlue3
    HEX('#5f5fff'), #  63 - RoyalBlue1
    HEX('#5f8700'), #  64 - Chartreuse4
    HEX('#5f875f'), #  65 - DarkSeaGreen4
    HEX('#5f8787'), #  66 - PaleTurquoise4
    HEX('#5f87af'), #  67 - SteelBlue
    HEX('#5f87d7'), #  68 - SteelBlue3
    HEX('#5f87ff'), #  69 - CornflowerBlue
    HEX('#5faf00'), #  70 - Chartreuse3
    HEX('#5faf5f'), #  71 - DarkSeaGreen4
    HEX('#5faf87'), #  72 - CadetBlue
    HEX('#5fafaf'), #  73 - CadetBlue
    HEX('#5fafd7'), #  74 - SkyBlue3
    HEX('#5fafff'), #  75 - SteelBlue1
    HEX('#5fd700'), #  76 - Chartreuse3
    HEX('#5fd75f'), #  77 - PaleGreen3
    HEX('#5fd787'), #  78 - SeaGreen3
    HEX('#5fd7af'), #  79 - Aquamarine3
    HEX('#5fd7d7'), #  80 - MediumTurquoise
    HEX('#5fd7ff'), #  81 - SteelBlue1
    HEX('#5fff00'), #  82 - Chartreuse2
    HEX('#5fff5f'), #  83 - SeaGreen2
    HEX('#5fff87'), #  84 - SeaGreen1
    HEX('#5fffaf'), #  85 - SeaGreen1
    HEX('#5fffd7'), #  86 - Aquamarine1
    HEX('#5fffff'), #  87 - DarkSlateGray2
    HEX('#870000'), #  88 - DarkRed
    HEX('#87005f'), #  89 - DeepPink4
    HEX('#870087'), #  90 - DarkMagenta
    HEX('#8700af'), #  91 - DarkMagenta
    HEX('#8700d7'), #  92 - DarkViolet
    HEX('#8700ff'), #  93 - Purple
    HEX('#875f00'), #  94 - Orange4
    HEX('#875f5f'), #  95 - LightPink4
    HEX('#875f87'), #  96 - Plum4
    HEX('#875faf'), #  97 - MediumPurple3
    HEX('#875fd7'), #  98 - MediumPurple3
    HEX('#875fff'), #  99 - SlateBlue1
    HEX('#878700'), # 100 - Yellow4
    HEX('#87875f'), # 101 - Wheat4
    HEX('#878787'), # 102 - Grey53
    HEX('#8787af'), # 103 - LightSlateGrey
    HEX('#8787d7'), # 104 - MediumPurple
    HEX('#8787ff'), # 105 - LightSlateBlue
    HEX('#87af00'), # 106 - Yellow4
    HEX('#87af5f'), # 107 - DarkOliveGreen3
    HEX('#87af87'), # 108 - DarkSeaGreen
    HEX('#87afaf'), # 109 - LightSkyBlue3
    HEX('#87afd7'), # 110 - LightSkyBlue3
    HEX('#87afff'), # 111 - SkyBlue2
    HEX('#87d700'), # 112 - Chartreuse2
    HEX('#87d75f'), # 113 - DarkOliveGreen3
    HEX('#87d787'), # 114 - PaleGreen3
    HEX('#87d7af'), # 115 - DarkSeaGreen3
    HEX('#87d7d7'), # 116 - DarkSlateGray3
    HEX('#87d7ff'), # 117 - SkyBlue1
    HEX('#87ff00'), # 118 - Chartreuse1
    HEX('#87ff5f'), # 119 - LightGreen
    HEX('#87ff87'), # 120 - LightGreen
    HEX('#87ffaf'), # 121 - PaleGreen1
    HEX('#87ffd7'), # 122 - Aquamarine1
    HEX('#87ffff'), # 123 - DarkSlateGray1
    HEX('#af0000'), # 124 - Red3
    HEX('#af005f'), # 125 - DeepPink4
    HEX('#af0087'), # 126 - MediumVioletRed
    HEX('#af00af'), # 127 - Magenta3
    HEX('#af00d7'), # 128 - DarkViolet
    HEX('#af00ff'), # 129 - Purple
    HEX('#af5f00'), # 130 - DarkOrange3
    HEX('#af5f5f'), # 131 - IndianRed
    HEX('#af5f87'), # 132 - HotPink3
    HEX('#af5faf'), # 133 - MediumOrchid3
    HEX('#af5fd7'), # 134 - MediumOrchid
    HEX('#af5fff'), # 135 - MediumPurple2
    HEX('#af8700'), # 136 - DarkGoldenrod
    HEX('#af875f'), # 137 - LightSalmon3
    HEX('#af8787'), # 138 - RosyBrown
    HEX('#af87af'), # 139 - Grey63
    HEX('#af87d7'), # 140 - MediumPurple2
    HEX('#af87ff'), # 141 - MediumPurple1
    HEX('#afaf00'), # 142 - Gold3
    HEX('#afaf5f'), # 143 - DarkKhaki
    HEX('#afaf87'), # 144 - NavajoWhite3
    HEX('#afafaf'), # 145 - Grey69
    HEX('#afafd7'), # 146 - LightSteelBlue3
    HEX('#afafff'), # 147 - LightSteelBlue
    HEX('#afd700'), # 148 - Yellow3
    HEX('#afd75f'), # 149 - DarkOliveGreen3
    HEX('#afd787'), # 150 - DarkSeaGreen3
    HEX('#afd7af'), # 151 - DarkSeaGreen2
    HEX('#afd7d7'), # 152 - LightCyan3
    HEX('#afd7ff'), # 153 - LightSkyBlue1
    HEX('#afff00'), # 154 - GreenYellow
    HEX('#afff5f'), # 155 - DarkOliveGreen2
    HEX('#afff87'), # 156 - PaleGreen1
    HEX('#afffaf'), # 157 - DarkSeaGreen2
    HEX('#afffd7'), # 158 - DarkSeaGreen1
    HEX('#afffff'), # 159 - PaleTurquoise1
    HEX('#d70000'), # 160 - Red3
    HEX('#d7005f'), # 161 - DeepPink3
    HEX('#d70087'), # 162 - DeepPink3
    HEX('#d700af'), # 163 - Magenta3
    HEX('#d700d7'), # 164 - Magenta3
    HEX('#d700ff'), # 165 - Magenta2
    HEX('#d75f00'), # 166 - DarkOrange3
    HEX('#d75f5f'), # 167 - IndianRed
    HEX('#d75f87'), # 168 - HotPink3
    HEX('#d75faf'), # 169 - HotPink2
    HEX('#d75fd7'), # 170 - Orchid
    HEX('#d75fff'), # 171 - MediumOrchid1
    HEX('#d78700'), # 172 - Orange3
    HEX('#d7875f'), # 173 - LightSalmon3
    HEX('#d78787'), # 174 - LightPink3
    HEX('#d787af'), # 175 - Pink3
    HEX('#d787d7'), # 176 - Plum3
    HEX('#d787ff'), # 177 - Violet
    HEX('#d7af00'), # 178 - Gold3
    HEX('#d7af5f'), # 179 - LightGoldenrod3
    HEX('#d7af87'), # 180 - Tan
    HEX('#d7afaf'), # 181 - MistyRose3
    HEX('#d7afd7'), # 182 - Thistle3
    HEX('#d7afff'), # 183 - Plum2
    HEX('#d7d700'), # 184 - Yellow3
    HEX('#d7d75f'), # 185 - Khaki3
    HEX('#d7d787'), # 186 - LightGoldenrod2
    HEX('#d7d7af'), # 187 - LightYellow3
    HEX('#d7d7d7'), # 188 - Grey84
    HEX('#d7d7ff'), # 189 - LightSteelBlue1
    HEX('#d7ff00'), # 190 - Yellow2
    HEX('#d7ff5f'), # 191 - DarkOliveGreen1
    HEX('#d7ff87'), # 192 - DarkOliveGreen1
    HEX('#d7ffaf'), # 193 - DarkSeaGreen1
    HEX('#d7ffd7'), # 194 - Honeydew2
    HEX('#d7ffff'), # 195 - LightCyan1
    HEX('#ff0000'), # 196 - Red1
    HEX('#ff005f'), # 197 - DeepPink2
    HEX('#ff0087'), # 198 - DeepPink1
    HEX('#ff00af'), # 199 - DeepPink1
    HEX('#ff00d7'), # 200 - Magenta2
    HEX('#ff00ff'), # 201 - Magenta1
    HEX('#ff5f00'), # 202 - OrangeRed1
    HEX('#ff5f5f'), # 203 - IndianRed1
    HEX('#ff5f87'), # 204 - IndianRed1
    HEX('#ff5faf'), # 205 - HotPink
    HEX('#ff5fd7'), # 206 - HotPink
    HEX('#ff5fff'), # 207 - MediumOrchid1
    HEX('#ff8700'), # 208 - DarkOrange
    HEX('#ff875f'), # 209 - Salmon1
    HEX('#ff8787'), # 210 - LightCoral
    HEX('#ff87af'), # 211 - PaleVioletRed1
    HEX('#ff87d7'), # 212 - Orchid2
    HEX('#ff87ff'), # 213 - Orchid1
    HEX('#ffaf00'), # 214 - Orange1
    HEX('#ffaf5f'), # 215 - SandyBrown
    HEX('#ffaf87'), # 216 - LightSalmon1
    HEX('#ffafaf'), # 217 - LightPink1
    HEX('#ffafd7'), # 218 - Pink1
    HEX('#ffafff'), # 219 - Plum1
    HEX('#ffd700'), # 220 - Gold1
    HEX('#ffd75f'), # 221 - LightGoldenrod2
    HEX('#ffd787'), # 222 - LightGoldenrod2
    HEX('#ffd7af'), # 223 - NavajoWhite1
    HEX('#ffd7d7'), # 224 - MistyRose1
    HEX('#ffd7ff'), # 225 - Thistle1
    HEX('#ffff00'), # 226 - Yellow1
    HEX('#ffff5f'), # 227 - LightGoldenrod1
    HEX('#ffff87'), # 228 - Khaki1
    HEX('#ffffaf'), # 229 - Wheat1
    HEX('#ffffd7'), # 230 - Cornsilk1
    HEX('#ffffff'), # 231 - Grey100

    # Grayscale colors
    HEX('#080808'), # 232 - Grey3
    HEX('#121212'), # 233 - Grey7
    HEX('#1c1c1c'), # 234 - Grey11
    HEX('#262626'), # 235 - Grey15
    HEX('#303030'), # 236 - Grey19
    HEX('#3a3a3a'), # 237 - Grey23
    HEX('#444444'), # 238 - Grey27
    HEX('#4e4e4e'), # 239 - Grey30
    HEX('#585858'), # 240 - Grey35
    HEX('#626262'), # 241 - Grey39
    HEX('#6c6c6c'), # 242 - Grey42
    HEX('#767676'), # 243 - Grey46
    HEX('#808080'), # 244 - Grey50
    HEX('#8a8a8a'), # 245 - Grey54
    HEX('#949494'), # 246 - Grey58
    HEX('#9e9e9e'), # 247 - Grey62
    HEX('#a8a8a8'), # 248 - Grey66
    HEX('#b2b2b2'), # 249 - Grey70
    HEX('#bcbcbc'), # 250 - Grey74
    HEX('#c6c6c6'), # 251 - Grey78
    HEX('#d0d0d0'), # 252 - Grey82
    HEX('#dadada'), # 253 - Grey85
    HEX('#e4e4e4'), # 254 - Grey89
    HEX('#eeeeee'), # 255 - Grey93
]


class X11SystemColor(ColorNames):
    # Base system colors
    TERM_BLACK = 0
    TERM_RED = 1
    TERM_GREEN = 2
    TERM_YELLOW = 3
    TERM_BLUE = 4
    TERM_MAGENTA = 5
    TERM_CYAN = 6
    TERM_WHITE = 7

    BASE_BLACK = 0
    BASE_RED = 1
    BASE_GREEN = 2
    BASE_YELLOW = 3
    BASE_BLUE = 4
    BASE_MAGENTA = 5
    BASE_CYAN = 6
    BASE_WHITE = 7

    TERM_0 = 0
    TERM_1 = 1
    TERM_2 = 2
    TERM_3 = 3
    TERM_4 = 4
    TERM_5 = 5
    TERM_6 = 6
    TERM_7 = 7

    # Bright version of base system colors
    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15

    BRIGHT_0 = 8
    BRIGHT_1 = 9
    BRIGHT_2 = 10
    BRIGHT_3 = 11
    BRIGHT_4 = 12
    BRIGHT_5 = 13
    BRIGHT_6 = 14
    BRIGHT_7 = 15

    TERM_8 = 8
    TERM_9 = 9
    TERM_10 = 10
    TERM_11 = 11
    TERM_12 = 12
    TERM_13 = 13
    TERM_14 = 14
    TERM_15 = 15

    # System colors
    BLACK = 0
    MAROON = 1
    GREEN = 2
    OLIVE = 3
    NAVY = 4
    PURPLE = 5
    TEAL = 6
    SILVER = 7
    GREY = 8
    RED = 9
    LIME = 10
    YELLOW = 11
    BLUE = 12
    FUCHSIA = 13
    MAGENTA = 13
    AQUA = 14
    CYAN = 14
    WHITE = 15


class X11BaseColor(ColorNames):
    # Base system colors
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


class X11BrightColor(ColorNames):
    # Bright version of base system colors
    BLACK = 8
    RED = 9
    GREEN = 10
    YELLOW = 11
    BLUE = 12
    MAGENTA = 13
    CYAN = 14
    WHITE = 15


class X11ExtendedColor(ColorNames):
    # 216 ANSI colors
    GREY0 = 16
    NAVYBLUE = 17
    DARKBLUE = 18
    BLUE3A = 19
    BLUE3B = 20
    BLUE1 = 21
    DARKGREEN = 22
    DEEPSKYBLUE4A = 23
    DEEPSKYBLUE4B = 24
    DEEPSKYBLUE4C = 25
    DODGERBLUE3 = 26
    DODGERBLUE2 = 27
    GREEN4 = 28
    SPRINGGREEN4 = 29
    TURQUOISE4 = 30
    DEEPSKYBLUE3A = 31
    DEEPSKYBLUE3B = 32
    DODGERBLUE1 = 33
    GREEN3A = 34
    SPRINGGREEN3A = 35
    DARKCYAN = 36
    LIGHTSEAGREEN = 37
    DEEPSKYBLUE2 = 38
    DEEPSKYBLUE1 = 39
    GREEN3B = 40
    SPRINGGREEN3B = 41
    SPRINGGREEN2A = 42
    CYAN3 = 43
    DARKTURQUOISE = 44
    TURQUOISE2 = 45
    GREEN1 = 46
    SPRINGGREEN2B = 47
    SPRINGGREEN1 = 48
    MEDIUMSPRINGGREEN = 49
    CYAN2 = 50
    CYAN1 = 51
    DARKRED1 = 52
    DEEPPINK4A = 53
    PURPLE4A = 54
    PURPLE4B = 55
    PURPLE3 = 56
    BLUEVIOLET = 57
    ORANGE4A = 58
    GREY37 = 59
    MEDIUMPURPLE4 = 60
    SLATEBLUE3A = 61
    SLATEBLUE3B = 62
    ROYALBLUE1 = 63
    CHARTREUSE4 = 64
    DARKSEAGREEN4A = 65
    PALETURQUOISE4 = 66
    STEELBLUE = 67
    STEELBLUE3 = 68
    CORNFLOWERBLUE = 69
    CHARTREUSE3A = 70
    DARKSEAGREEN4B = 71
    CADETBLUE2 = 72
    CADETBLUE1 = 73
    SKYBLUE3 = 74
    STEELBLUE1A = 75
    CHARTREUSE3B = 76
    PALEGREEN3A = 77
    SEAGREEN3 = 78
    AQUAMARINE3 = 79
    MEDIUMTURQUOISE = 80
    STEELBLUE1B = 81
    CHARTREUSE2A = 82
    SEAGREEN2 = 83
    SEAGREEN1A = 84
    SEAGREEN1B = 85
    AQUAMARINE1A = 86
    DARKSLATEGRAY2 = 87
    DARKRED2 = 88
    DEEPPINK4B = 89
    DARKMAGENTA1 = 90
    DARKMAGENTA2 = 91
    DARKVIOLET1A = 92
    PURPLE1A = 93
    ORANGE4B = 94
    LIGHTPINK4 = 95
    PLUM4 = 96
    MEDIUMPURPLE3A = 97
    MEDIUMPURPLE3B = 98
    SLATEBLUE1 = 99
    YELLOW4A = 100
    WHEAT4 = 101
    GREY53 = 102
    LIGHTSLATEGREY = 103
    MEDIUMPURPLE = 104
    LIGHTSLATEBLUE = 105
    YELLOW4B = 106
    DARKOLIVEGREEN3A = 107
    DARKGREENSEA = 108
    LIGHTSKYBLUE3A = 109
    LIGHTSKYBLUE3B = 110
    SKYBLUE2 = 111
    CHARTREUSE2B = 112
    DARKOLIVEGREEN3B = 113
    PALEGREEN3B = 114
    DARKSEAGREEN3A = 115
    DARKSLATEGRAY3 = 116
    SKYBLUE1 = 117
    CHARTREUSE1 = 118
    LIGHTGREEN2 = 119
    LIGHTGREEN3 = 120
    PALEGREEN1A = 121
    AQUAMARINE1B = 122
    DARKSLATEGRAY1 = 123
    RED3A = 124
    DEEPPINK4C = 125
    MEDIUMVIOLETRED = 126
    MAGENTA3A = 127
    DARKVIOLET1B = 128
    PURPLE1B = 129
    DARKORANGE3A = 130
    INDIANRED1A = 131
    HOTPINK3A = 132
    MEDIUMORCHID3 = 133
    MEDIUMORCHID = 134
    MEDIUMPURPLE2A = 135
    DARKGOLDENROD = 136
    LIGHTSALMON3A = 137
    ROSYBROWN = 138
    GREY63 = 139
    MEDIUMPURPLE2B = 140
    MEDIUMPURPLE1 = 141
    GOLD3A = 142
    DARKKHAKI = 143
    NAVAJOWHITE3 = 144
    GREY69 = 145
    LIGHTSTEELBLUE3 = 146
    LIGHTSTEELBLUE = 147
    YELLOW3A = 148
    DARKOLIVEGREEN3 = 149
    DARKSEAGREEN3B = 150
    DARKSEAGREEN2 = 151
    LIGHTCYAN3 = 152
    LIGHTSKYBLUE1 = 153
    GREENYELLOW = 154
    DARKOLIVEGREEN2 = 155
    PALEGREEN1B = 156
    DARKSEAGREEN5B = 157
    DARKSEAGREEN5A = 158
    PALETURQUOISE1 = 159
    RED3B = 160
    DEEPPINK3A = 161
    DEEPPINK3B = 162
    MAGENTA3B = 163
    MAGENTA3C = 164
    MAGENTA2A = 165
    DARKORANGE3B = 166
    INDIANRED1B = 167
    HOTPINK3B = 168
    HOTPINK2 = 169
    ORCHID = 170
    MEDIUMORCHID1A = 171
    ORANGE3 = 172
    LIGHTSALMON3B = 173
    LIGHTPINK3 = 174
    PINK3 = 175
    PLUM3 = 176
    VIOLET = 177
    GOLD3B = 178
    LIGHTGOLDENROD3 = 179
    TAN = 180
    MISTYROSE3 = 181
    THISTLE3 = 182
    PLUM2 = 183
    YELLOW3B = 184
    KHAKI3 = 185
    LIGHTGOLDENROD2A = 186
    LIGHTYELLOW3 = 187
    GREY84 = 188
    LIGHTSTEELBLUE1 = 189
    YELLOW2 = 190
    DARKOLIVEGREEN1A = 191
    DARKOLIVEGREEN1B = 192
    DARKSEAGREEN1 = 193
    HONEYDEW2 = 194
    LIGHTCYAN1 = 195
    RED1 = 196
    DEEPPINK2 = 197
    DEEPPINK1A = 198
    DEEPPINK1B = 199
    MAGENTA2B = 200
    MAGENTA1 = 201
    ORANGERED1 = 202
    INDIANRED1C = 203
    INDIANRED1D = 204
    HOTPINK1A = 205
    HOTPINK1B = 206
    MEDIUMORCHID1B = 207
    DARKORANGE = 208
    SALMON1 = 209
    LIGHTCORAL = 210
    PALEVIOLETRED1 = 211
    ORCHID2 = 212
    ORCHID1 = 213
    ORANGE1 = 214
    SANDYBROWN = 215
    LIGHTSALMON1 = 216
    LIGHTPINK1 = 217
    PINK1 = 218
    PLUM1 = 219
    GOLD1 = 220
    LIGHTGOLDENROD2B = 221
    LIGHTGOLDENROD2C = 222
    NAVAJOWHITE1 = 223
    MISTYROSE1 = 224
    THISTLE1 = 225
    YELLOW1 = 226
    LIGHTGOLDENROD1 = 227
    KHAKI1 = 228
    WHEAT1 = 229
    CORNSILK1 = 230
    GREY100 = 231


class X11GreyscaleColor(ColorNames):
    # Grayscale colors
    GREY0 = 16
    GREY3 = 232
    GREY7 = 233
    GREY11 = 234
    GREY15 = 235
    GREY19 = 236
    GREY23 = 237
    GREY27 = 238
    GREY30 = 239
    GREY35 = 240
    GREY39 = 241
    GREY42 = 242
    GREY46 = 243
    GREY50 = 244
    GREY54 = 245
    GREY58 = 246
    GREY62 = 247
    GREY66 = 248
    GREY70 = 249
    GREY74 = 250
    GREY78 = 251
    GREY82 = 252
    GREY85 = 253
    GREY89 = 254
    GREY93 = 255
    GREY100 = 231


class X11Color(X11SystemColor, X11ExtendedColor, X11GreyscaleColor):
    pass


COLORS = X11_COLORS
Color = X11Color

GREYSCALE_COLORS = (16, *range(232,256), 231)
GREYSCALE_MAP = ColorMap(GREYSCALE_COLORS)


X11_DARK = ColorPalette(
    name='X11 Dark',
    fg=X11_COLORS[Color.WHITE],
    bg=X11_COLORS[Color.BLACK],
    color_names=X11Color,
    colors=X11_COLORS,
)

X11_LIGHT = X11_DARK.invert('X11 Light')


TANGO_COLORS = [
    HEX("#2e3436"),
    HEX("#cc0000"),
    HEX("#4e9a06"),
    HEX("#c4a000"),
    HEX("#3465a4"),
    HEX("#75507b"),
    HEX("#06989a"),
    HEX("#d3d7cf"),
    HEX("#555753"),
    HEX("#ef2929"),
    HEX("#8ae234"),
    HEX("#fce94f"),
    HEX("#729fcf"),
    HEX("#ad7fa8"),
    HEX("#34e2e2"),
    HEX("#eeeeec"),
]

TANGO_DARK = ColorPalette(
    name='Tango Dark',
    fg=HEX("#d3d7cf"),
    bg=HEX("#2e3436"),
    color_names=X11Color,
    colors=[
        *TANGO_COLORS,
        *X11_COLORS[16:],
    ])

TANGO_LIGHT = ColorPalette(
    name='Tango Light',
    fg=HEX("#2e3436"),
    bg=HEX("#eeeeec"),
    color_names=X11Color,
    colors=[
        *TANGO_COLORS,
        *X11_COLORS[16:],
    ])


CGA_TERM = ColorPalette(
    name='CGA',
    fg=HEX('#FFFFFF'),
    bg=HEX('#000000'),
    color_names=X11SystemColor,
    colors=[
        # Order rearanged to match term colors
        HEX('#000000'),
        HEX('#AA0000'),
        HEX('#00AA00'),
        HEX('#AA5500'),
        HEX('#0000AA'),
        HEX('#AA00AA'),
        HEX('#00AAAA'),
        HEX('#AAAAAA'),
        HEX('#555555'),
        HEX('#FF5555'),
        HEX('#55FF55'),
        HEX('#FFFF55'),
        HEX('#5555FF'),
        HEX('#FF55FF'),
        HEX('#55FFFF'),
        HEX('#FFFFFF'),
    ])

