import entity, random, math
enemyNames = 'blinky - pinky - inky - clyde'


class Point(entity.Entity):
	def __init__(self, cp_of_entities, cp_of_maze, cp_of_pacman, index):
		self.ENTITIES = cp_of_entities
		self.MAZE = cp_of_maze
		self.PACMAN = cp_of_pacman

		exceptions = [ 145, 144, 143, 179, 178, 177 ]

		xt, yt = self.MAZE.indexToTile(index) # returnerer xTile og yTile
		position = self.MAZE.tileToPosition(xt, yt)
		tileType = self.MAZE.grid[index]


		self.doNotShow = False
		if (not (tileType == 2 or tileType == 3)) or index in exceptions: 
			self.doNotShow = True # Hvis der er en væg, så oprettes der ikke et point eller en ost
		


		point = entity.Sprite('./assets/points.png', grid={'rows': 1, 'columns': 3}, type="Image" )
		cheese = entity.Sprite('./assets/points.png', correspondingState='cheese', type="Image", grid={'rows': 1, 'columns': 3}, beginFrame=1, endFrame=1)
		none = entity.Sprite('./assets/points.png', correspondingState='none', type="Image", grid={'rows': 1, 'columns': 3}, beginFrame=2, endFrame=2)
		spritesArr = [ point, cheese, none ]

		super().__init__(position['x']-3, position['y']-4, sprites = spritesArr, state='main')
		if (tileType == 2): self.setSprite('cheese')



	def update(self, dt):
		# Kollision
		xTile, yTile = self.MAZE.getXYTileFromPos(self.x+16, self.y+24)
		px, py = self.PACMAN.getTilePosition()
		if (px >= xTile >= px) and (py >= yTile >= py) and self.state != 'none':
			if py >= yTile >= py:
				if self.state == 'cheese':
					def _callback(Ghost):
						Ghost.setMode('frightened')

					self.getGhosts(_callback)
					self.PACMAN.score += 1
					


				self.setSprite('none')

		# super.update(dt)




	def getGhosts(self, callback=None, start=0, end=3):
		if type(start) == int or type(end) == int:
			i = 0
			for E in self.ENTITIES:
				if hasattr(E, 'name'):
					if E.name in enemyNames:
						if i >= start and i <= end:
							if callback != None:
								callback(E)

						i += 1