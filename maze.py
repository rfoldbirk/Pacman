import entity


class Maze(entity.Entity):
	def __init__(self):
		mapSprite = entity.Sprite('./assets/maze.png', type='image')
		super().__init__(sprites = [ mapSprite ])
