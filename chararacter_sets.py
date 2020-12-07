import enum

class CP437_CharacterSet(enum.IntEnum):
    SMILIE = 1
    SMILIE_INV = 2
    HEART = 3
    DIAMOND = 4
    CLUB = 5
    SPADE = 6
    BULLET = 7
    BULLET_INV = 8
    RADIO_UNSET = 9
    RADIO_SET = 10
    MALE = 11
    FEMALE = 12
    NOTE = 13
    NOTE_DOUBLE = 14
    LIGHT = 15
    ARROW2_E = 16
    ARROW2_W = 17
    DARROW_V = 18
    EXCLAM_DOUBLE = 19
    PILCROW = 20
    SECTION = 21
    # TODO: 22 - 23
    ARROW_N = 24
    ARROW_S = 25
    ARROW_E = 26
    ARROW_W = 27
    # TODO: 28
    DARROW_H = 29
    ARROW2_N = 30
    ARROW2_S = 31
    # TODO: 32 - 154
    POUND = 156
    # TODO: 157
    MULTIPLICATION = 158
    FUNCTION = 159
    # TODO: 160 - 168
    RESERVED = 169
    # TODO: 170
    HALF = 171
    ONE_QUARTER = 172
    # TODO: 173 - 175
    BLOCK1 = 176
    BLOCK2 = 177
    BLOCK3 = 178
    VLINE = 179
    TEEW = 180
    # TODO: 181 - 183
    COPYRIGHT = 184
    DTEEW = 185
    DVLINE = 186
    DNE = 187
    DSE = 188
    CENT = 189
    YEN = 190
    NE = 191
    SW = 192
    TEEN = 193
    TEES = 194
    TEEE = 195
    HLINE = 196
    CROSS = 197
    # TODO: 198 - 199
    DSW = 200
    DNW = 201
    DTEEN = 202
    DTEES = 203
    DTEEE = 204
    DHLINE = 205
    DCROSS = 206
    CURRENCY = 207
    # TODO: 208 - 216
    SE = 217
    NW = 218
    # TODO: 219 - 223
    CHECKBOX_UNSET = 224
    CHECKBOX_SET = 225
    SUBP_NW = 226
    SUBP_NE = 227
    SUBP_N = 228
    SUBP_SE = 229
    SUBP_DIAG = 230
    SUBP_E = 231
    SUBP_SW = 232
    # TODO: 233 - 242
    THREE_QUARTERS = 243
    # TODO: 244 - 245
    DIVISION = 246
    # TODO: 247
    GRADE = 248
    UMLAUT = 249
    # TODO: 250
    POW1 = 251
    POW3 = 252
    POW2 = 253
    BULLET_SQUARE = 254


Character = CP437_CharacterSet


class Symbol(enum.IntEnum):
    # Single line walls:
    HLINE=196 #  (HorzLine)
    VLINE=179 #  (VertLine)
    NE=191 #  (NE)
    NW=218 #  (NW)
    SE=217 #  (SE)
    SW=192 #  (SW)

    # Double lines walls:
    DHLINE=205 #  (DoubleHorzLine)
    DVLINE=186 #  (DoubleVertLine)
    DNE=187 #  (DoubleNE)
    DNW=201 #  (DoubleNW)
    DSE=188 #  (DoubleSE)
    DSW=200 #  (DoubleSW)

    # Single line vertical/horizontal junctions (T junctions):
    TEEW=180 #  (TeeWest)
    TEEE=195 #  (TeeEast)
    TEEN=193 #  (TeeNorth)
    TEES=194 #  (TeeSouth)

    # Double line vertical/horizontal junctions (T junctions):
    DTEEW=185 #  (DoubleTeeWest)
    DTEEE=204 #  (DoubleTeeEast)
    DTEEN=202 #  (DoubleTeeNorth)
    DTEES=203 #  (DoubleTeeSouth)

    # Block characters:
    BLOCK1=176 #  (Block1)
    BLOCK2=177 #  (Block2)
    BLOCK3=178 #  (Block3)

    # Cross-junction between two single line walls:
    CROSS=197 #  (Cross)

    # Arrows:
    ARROW_N=24 #  (ArrowNorth)
    ARROW_S=25 #  (ArrowSouth)
    ARROW_E=26 #  (ArrowEast)
    ARROW_W=27 #  (ArrowWest)

    # Arrows without tail:
    ARROW2_N=30 #  (ArrowNorthNoTail)
    ARROW2_S=31 #  (ArrowSouthNoTail)
    ARROW2_E=16 #  (ArrowEastNoTail)
    ARROW2_W=17 #  (ArrowWestNoTail)

    # Double arrows:
    DARROW_H=29 #  (DoubleArrowHorz)
    ARROW_V=18 #  (DoubleArrowVert)

    # GUI stuff:
    CHECKBOX_UNSET=224
    CHECKBOX_SET=225
    RADIO_UNSET=9
    RADIO_SET=10

    # Sub-pixel resolution kit:
    SUBP_NW=226 #  (SubpixelNorthWest)
    SUBP_NE=227 #  (SubpixelNorthEast)
    SUBP_N=228 #  (SubpixelNorth)
    SUBP_SE=229 #  (SubpixelSouthEast)
    SUBP_DIAG=230 #  (SubpixelDiagonal)
    SUBP_E=231 #  (SubpixelEast)
    SUBP_SW=232 #  (SubpixelSouthWest)

    # Miscellaneous characters:
    SMILY = 1 #  (Smilie)
    SMILY_INV = 2 #  (SmilieInv)
    HEART = 3 #  (Heart)
    DIAMOND = 4 #  (Diamond)
    CLUB = 5 #  (Club)
    SPADE = 6 #  (Spade)
    BULLET = 7 #  (Bullet)
    BULLET_INV = 8 #  (BulletInv)
    MALE = 11 #  (Male)
    FEMALE = 12 #  (Female)
    NOTE = 13 #  (Note)
    NOTE_DOUBLE = 14 #  (NoteDouble)
    LIGHT = 15 #  (Light)
    EXCLAM_DOUBLE = 19 #  (ExclamationDouble)
    PILCROW = 20 #  (Pilcrow)
    SECTION = 21 #  (Section)
    POUND = 156 #  (Pound)
    MULTIPLICATION = 158 #  (Multiplication)
    FUNCTION = 159 #  (Function)
    RESERVED = 169 #  (Reserved)
    HALF = 171 #  (Half)
    ONE_QUARTER = 172 #  (OneQuarter)
    COPYRIGHT = 184 #  (Copyright)
    CENT = 189 #  (Cent)
    YEN = 190 #  (Yen)
    CURRENCY = 207 #  (Currency)
    THREE_QUARTERS = 243 #  (ThreeQuarters)
    DIVISION = 246 #  (Division)
    GRADE = 248 #  (Grade)
    UMLAUT = 249 #  (Umlaut)
    POW1 = 251 #  (Pow1)
    POW3 = 252 #  (Pow2)
    POW2 = 253 #  (Pow3)
    BULLET_SQUARE = 254 #  (BulletSquare)

