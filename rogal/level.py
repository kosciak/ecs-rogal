from .geometry import Rectangular, Position, Size


class Level(Rectangular):

    position = Position.ZERO

    def __init__(self, level_id, depth, terrain):
        self.id = level_id

        self.depth = depth
        self.terrain = terrain

    @property
    def size(self):
        return Size(*self.terrain.shape)

    def serialize(self):
        terrain = []
        for row in self.terrain.T:
            terrain.append(','.join([f'{terrain_id:02x}' for terrain_id in row]))
        data = {
            str(self.id): dict(
                depth=self.depth,
                #name=self.name,
                terrain=terrain,
            )}
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id} depth={self.depth} size={self.size}>'

