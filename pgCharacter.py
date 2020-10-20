import entity, random, math


class pgCharacter(entity.Entity):
	def __init__(self, copy_of_maze, copy_of_pacman=False, spriteName="pacman"):
		self.MAZE = copy_of_maze
		self.PACMAN = copy_of_pacman

		self.name = spriteName

		# Position
		rx, ry = 8+7*12+16, 8+8*12
		if copy_of_pacman:
			ry = 8+10*12

		# Sprites
		sColumns = 3
		if bool(copy_of_pacman): 
			sColumns = 2

		right = self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'right', spriteName=spriteName, columns=sColumns)
		left = self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'left', spriteName=spriteName, columns=sColumns)
		up = self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'up', spriteName=spriteName, columns=sColumns)
		down = self.makeDesignedSprite(0, sColumns-1, 'down', spriteName=spriteName, columns=sColumns)
		
		

		# AI settings
		self.isEnemy = bool(copy_of_pacman)
		self.isDead = False
		self.altTarget = { "x": -1, "y": -1 }
		self.keepMoving = True #TODO: Fjern når du er færdig med at debugge
		self.direction = ""
		self.setNeedToMove(0) # Holder styr på hvor meget spilleren mangler at bevæge sig for at være færdig.
		self.lastDirection = ""
		self.nextDirection = ""

		self.cheeseTimer = 0

		# Movement settings
		self.goThroughDoor = False
		self.speed = 40
		if bool(copy_of_pacman): self.speed = 35

		# Debug settings
		self.correct = False
		

		# Entity init, meget vigtigt.
		super().__init__(rx, ry, sprites = [ right, left, down, up ], state='left')

		self.currentSprite.play = False
		if self.isEnemy: self._move()


	def update(self, dt):
		# få positionen på kortet

		if self.direction != "":
			self.setSprite(self.direction)
			movement = self.speed * dt

			self.needToMove -= movement
			
			if self.direction == 'left':
				self.x -= movement
			elif self.direction == 'right':
				self.x += movement
			elif self.direction == 'up':
				self.y += movement
			elif self.direction == 'down':
				self.y -= movement

			if self.needToMove <= 0:
				# Nu er det tid at vælge den næste retning.

				self.lastDirection = self.direction
				self.direction = ""

				if self.keepMoving:
					if self.isEnemy:
						#* Fjendtlige bevægelser
						self._enemy_chooseDirection()
					else:
						self._move( preferedDirection=self.lastDirection )
			
		if self.isEnemy:
			# Kollision
			xTile, yTile = self.MAZE.getXYTileFromPos(self.x+16, self.y+24)
			px, py = self.PACMAN.getTilePosition()
			if px >= xTile >= px:
				if py >= yTile >= py:
					if self.PACMAN.cheeseTimer > 0:
						self.isDead = True
						self.setSprite()

		super().update(dt)



	def setNeedToMove(self, amount):
			self.NEEDtoMOVE = amount
			self.needToMove = amount



	def requestMove(self, preferedDirection):
		if self.getOppositeDirection(preferedDirection) == self.direction:
			self.direction = preferedDirection
			self.setNeedToMove( self.NEEDtoMOVE - self.needToMove )

		self.nextDirection = preferedDirection
		self._move(preferedDirection=preferedDirection)



	def _move(self, preferedDirection="random", ignoreDirection=""):

		#* bindestregen betyder at _move ikke bliver kaldt direkte, men derimod det en funktion, 
		#* som bliver kaldt internt når systemet er klar til at bevæge sig videre.

		#* De to parametre bliver henholdsvist brugt af spilleren og fjenden.
		#? preferedDirection: 
		#? 		Bliver brugt til at anmode om en retning, dog bliver denne retning ikke valgt i tilfælde af at
		#?		self.nextDirection er blevet sat.
		#?		Man kan desuden også sætte dene værdi til random, så vælger den selv en retning
		#?
		#? ignoreDirection: 
		#? 		Siger vist lidt sig selv. Hvis man udfylder denne parameter, ignorer metoden en given retning.

		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24)

		if self.needToMove > 0:
			return

		_x, _y = self.MAZE.indexToTile( index )
		desiredPosition = self.MAZE.tileToPosition( _x, _y )
		self.x = desiredPosition['x'] -4
		self.y = desiredPosition['y'] -4

		dirs = [l, r, u, d]
		posDirs = []

		dirsStrs = ["left", "right", "up", "down"]

		
		# Laver et array med de mulige retninger man kan gå i.
		i = 0
		for dir in dirs:
			if (dir > 1 or dir < int(self.goThroughDoor)) and dirsStrs[i] != ignoreDirection:
				posDirs.append(dirsStrs[i])
			i += 1

		
		# Udvægelse af retning // konvertering af string(retning) -> int(retning)
		if self.nextDirection in posDirs:
			preferedDirection = posDirs.index(self.nextDirection)
			self.nextDirection = ""
		elif preferedDirection in posDirs:
			preferedDirection = posDirs.index(preferedDirection)
		else: # Hvis ikke, vælger den bare en tilfældig retning :/
			if self.lastDirection in posDirs:
				preferedDirection = posDirs.index(self.lastDirection)
			elif self.isEnemy:
				if len(posDirs) == 0:
					preferedDirection = dirsStrs.index(self.getOppositeDirection(self.lastDirection))
				else:
					preferedDirection = random.randint(0, len(posDirs)-1)
			else:
				self.currentSprite.play = False
				return

		self.currentSprite.play = True


		# TODO: [ Bedre udvægelse ] Få dette til at fungere
		# directionWishes = [ self.nextDirection, preferedDirection, self.lastDirection, random.randint(0, len(posDirs)-1) ]
		# for _dir in directionWishes:
		# 	_dirNum = _dir
		# 	if type(_dir) == str: 
		# 		_dirNum = posDirs.index(_dir)

		# 	# Afspiller eller stopper animationen
		# 	self.currentSprite.play = not (self.isEnemy and type(_dir) == int)

		# 	if self.isEnemy and type(_dir) == int:
		# 		return
		# 	elif _dir in posDirs:
		# 		preferedDirection = _dirNum
		# 		self.nextDirection = ""
		# TODO: ------------------------------------------------------------------------------------------------------------


		# Sætter spriten, så den vender korrekt.
		try:
			self.direction = posDirs[preferedDirection]
		except:
			self.direction = dirsStrs[preferedDirection]

		moveVertical, moveHorizontal = self.MAZE.getMovementInfo(self.direction, index)

		if self.direction == "right" or self.direction == "left":
			self.setNeedToMove(moveVertical)
		elif self.direction == "up" or self.direction == "down":
			self.setNeedToMove(moveHorizontal)
	


	def onKeyPress(self, symbol, modifiers):

		#! SKAL FJERNES!

		if symbol == 105:
			if modifiers:
				self.y += 12
			else:
				self.y += 16
		if symbol == 106:
			if modifiers:
				self.x -= 12
			else:
				self.x -= 16

		if symbol == 107: # K
			self.correct = True

		if symbol == 108: # L
			index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24)
			_x, _y = self.MAZE.indexToTile( index )
			print(self.MAZE.tileToPosition(_x, _y))


		if self.isEnemy and symbol == 110: # N
			self.goThroughDoor = True
			self.enemy_setTarget(8, 11)

		#! -------------

		if self.isEnemy: return # ignorer alle inputs hvis denne entity er en fjende.

		if symbol == 112: # P
			self.MAZE.getPossibleDirections(self.x+16, self.y+24, True)

		if symbol == 109: # M
			self.keepMoving = not self.keepMoving
			if self.keepMoving and self.isEnemy: self._move("random")

		if symbol == 65362: # up arrow
			self.requestMove("up")

		if symbol == 65364: # down arrow
			self.requestMove("down")

		if symbol == 65361: # left arrow
			self.requestMove("left")

		if symbol == 65363: # right arrow
			self.requestMove("right")



	def enemy_setTarget(self, xTile=-1, yTile=-1):
		self.altTarget = { "x": xTile, "y": yTile }
		print(self.name, self.altTarget)

	
	def useAltTarget(self):
		if self.altTarget["x"] == -1 or self.altTarget["y"] == -1: return False
		return True



	def _enemy_chooseDirection(self):
		#* Fjendtlige bevægelser
		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24, False)

		_dirs = [l, r, u, d]
		_posDirs = ['left', 'right', 'up', 'down']
		amountOfDirections = 0
		posDirs = []
		
		_i = 0
		for _dir in _dirs:
			if (_dir > 1 or _dir < int(self.goThroughDoor)) and _posDirs[_i] != self.getOppositeDirection( self.lastDirection ):
				amountOfDirections += 1
				posDirs.append(_posDirs[_i])

			_i += 1

		if amountOfDirections == 1:
			self._move( ignoreDirection=self.getOppositeDirection( self.lastDirection ) )
		else:
			xTile, yTile, index = self.MAZE.getXYTileFromPos(self.x+16, self.y+24, returnIndex=True)
			lx, ly, rx, ry, ux, uy, dx, dy = self.MAZE.getTilesAroundTile(xTile, yTile, index, convertToTiles=True)
			tilesAround = [lx, ly, rx, ry, ux, uy, dx, dy]

			# Find den korteste rute mod målet
			cDistance = 1000000 #? det skal bare være et højt tal
			cDirection = ""

			px, py = self.PACMAN.getTilePosition()
			if self.useAltTarget():
				px, py = self.altTarget["x"], self.altTarget["y"]

			for pdir in posDirs:
				i = _posDirs.index(pdir)
				gx, gy = tilesAround[i*2], tilesAround[i*2+1]
				
				deltaX = abs(gx - px)
				deltaY = abs(gy - py)

				distance = math.pow(deltaX, 2) + math.pow(deltaY, 2)
				if distance < cDistance: 
					cDistance = distance
					cDirection = pdir

			if xTile == self.altTarget["x"] and yTile == self.altTarget["y"]:
				if (not self.isDead) and self.goThroughDoor:
					self.goThroughDoor = False
					self.enemy_setTarget()

			if xTile == 8 and yTile == 10 and self.isDead:
				self.goThroughDoor = True
				self.isDead = True
			

			self._move( preferedDirection=cDirection, ignoreDirection=self.getOppositeDirection( self.lastDirection ) )
		



	def makeDesignedSprite(self, beginFrame, endFrame, state, spriteName="pacman", rows=4, columns=3, speed=9):
		return entity.Sprite(f'./assets/{spriteName}.png', correspondingState=state, grid={'rows': rows, 'columns': columns}, beginFrame=beginFrame, endFrame=endFrame, animationSpeed=speed, animationBounce=True )



	def getTilePosition(self):
		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24)
		return self.MAZE.indexToTile( index )



	def getOppositeDirection(self, direction):
		if direction == "right":
			return "left"
		elif direction == "left":
			return "right"
		elif direction == "up":
			return "down"
		elif direction == "down":
			return "up"