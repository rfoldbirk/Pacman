import entity, math


class Maze(entity.Entity):
	def __init__(self):

		# 0: fungerer som en dør
		# 1: wall
		# 2: cheese
		# 3: dots, to be eaten
		# 4: ingenting

		self.maxLevel = 10
		self.level = 0

		# 18x19
		self.grid = [
			2, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 2,
			3, 1, 1, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 1, 1, 3,
			3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3,
			3, 1, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 3,
			3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3,
			1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1,
			3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3,
			3, 1, 1, 3, 1, 3, 1, 1, 0, 1, 1, 3, 1, 3, 1, 1, 3,
			3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3,
			3, 1, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 3,
			3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3,
			1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1,
			3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
			3, 1, 1, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 1, 1, 3,
			3, 2, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 2, 3,
			1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1,
			3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3,
			3, 1, 1, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 1, 1, 3,
			3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
		]

		self.width = { 'pixels': 232, 'units': 19 }
		self.height = { 'pixels': 256, 'units': 21 }

		mapSprite = entity.Sprite('./assets/maze.png', type='image')
		super().__init__(sprites = [ mapSprite ])



	def indexToTile(self, index):
		ogindex = index

		y = 0
		while index >= 17:
			y += 1
			index -= 17

		x = index
		
		return x, 18-y



	def tileToPosition(self, x, y):
		position = { "x": 0, "y": 0 }

		# Beregning af den korrekte y position
		for i in range(0, y+1):
			addTo = 12
			if i >= 17:
				addTo = 16

			position["y"] += addTo

		# Beregning af den korrekte x position
		for i in range(0, x+1):
			addTo = 12
			if i == 1 or i == 16:
				addTo = 16

			position["x"] += addTo

		return position



	def getMovementInfo(self, direction, index):
		x, y = self.indexToTile(index)

		moveVertical = 12
		moveHorizontal = 12

		if (direction == "right" and (x == 15 or x == 0)) or (direction == "left" and (x == 16 or x == 1)):
			moveVertical = 16

		if (direction == "up" and (y == 16 or y == 17)) or (direction == "down" and (y == 18 or y == 17)):
			moveHorizontal = 16

		return moveVertical, moveHorizontal	



	def getPossibleDirections(self, x, y, debug=False):
		#? Returnerer blandt andet mulige retninger i formattet: indeks på map, venstre, højre, oppe, nede.
		# TODO: fjern debug, når funktionen har vist sig kampdygtig.

		xTile, yTile, index = self.getXYTileFromPos(x, y, returnIndex=True)
		
		#! INDSÆT HER
		leftTile, rightTile, upTile, downTile = self.getTilesAroundTile(xTile, yTile, index)

		position = self.tileToPosition(xTile, yTile)

		if debug:
			print(" --   DEBUG MODE   --")
			print("X & Y:", x, y)
			print("INDEX:", index, "\t   ", upTile)
			print("TILES:", xTile, yTile, "\t ", leftTile ," ",rightTile)
			print("\t\t   ",downTile)
			print(" -- END DEBUG MODE --")


		# return index, moveToLeft
		return index, leftTile, rightTile, upTile, downTile



	def getXYTileFromPos(self, x, y, returnIndex=False):
		# først runder vi ned eller op afhængigt af hvilken retning vi er på vej i.
		xTile = 0
		if x-16 > 16:
			xTile = round((x-16)/12-1)

		yTile = round((y-20) / 12-1)
		if yTile > 18: yTile = 18

		yPos = 17*(18-yTile)
		index = yPos + xTile

		if returnIndex:
			return xTile, yTile, index
		else:
			return xTile, yTile


	def getTilesAroundTile(self, xTile, yTile, index, convertToTiles=False):
		# Tiles
		leftTile = 1
		leftTile_i = 1
		rightTile = 1
		rightTile_i = 1
		upTile = 1
		upTile_i = 1
		downTile = 1
		downTile_i = 1

		try:
			if xTile != 0:	
				leftTile = self.grid[index-1]
				leftTile_i = index-1
			if xTile != 16:	
				rightTile = self.grid[index+1] # højre side
				rightTile_i = index+1
			if yTile != 18:	
				upTile = self.grid[index-17]
				upTile_i = index-17
			if yTile != 0:	
				downTile = self.grid[index+17]
				downTile_i = index+17
		except:
			print('Something went wrong...')
			exit()

		if not convertToTiles:
			return leftTile, rightTile, upTile, downTile
		else:
			lx, ly = self.indexToTile(leftTile_i)
			rx, ry = self.indexToTile(rightTile_i)
			ux, uy = self.indexToTile(upTile_i)
			dx, dy = self.indexToTile(downTile_i)
			return lx, ly, rx, ry, ux, uy, dx, dy