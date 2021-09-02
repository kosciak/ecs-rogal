class TilesSource:

    is_tilesheet = False

    def __init__(self, charset):
        self.path = None
        self.charset = charset

    def has_code_point(self, code_point):
        return code_point in self.charset

    def get_tile(self, code_point, tile_size):
        raise NotImplementedError()

    def tiles_gen(self, tile_size):
        for code_point in self.charset:
            tile = self.get_tile(code_point, tile_size)
            if tile is None:
                continue
            yield code_point, tile

