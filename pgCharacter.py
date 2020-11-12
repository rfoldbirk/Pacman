import entity, random, math

from constants import Constants
CONSTANTS = Constants()


enemyNames = [ 'blinky', 'pinky', 'inky', 'clyde' ]
enemyHomes = { 'blinky': [16, 20], 'pinky': [0, 20], 'inky': [16, 0], 'clyde': [0, 0] }
enemySpawnTimes = { 'blinky': 0, 'pinky': 10, 'inky': 20, 'clyde': 30 }


class pgCharacter(entity.Entity):
	def __init__(self, copy_of_maze, copy_of_pacman=False, spriteName='pacman'):
		self.MAZE = copy_of_maze
		self.PACMAN = copy_of_pacman

		self.name = spriteName
		self.isEnemy = self.name != 'pacman'

		# Position
		rx, ry = 8+7*12+16, 8+8*12
		if copy_of_pacman:
			ry = 8+10*12

		# Sprites
		sColumns = 3
		if self.isEnemy: 
			sColumns = 2

		right = self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'right', spriteName=spriteName, columns=sColumns)
		left = self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'left', spriteName=spriteName, columns=sColumns)
		up = self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'up', spriteName=spriteName, columns=sColumns)
		down = self.makeDesignedSprite(0, sColumns-1, 'down', spriteName=spriteName, columns=sColumns)
		
		if self.isEnemy:
			rightDead = self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'right-dead', spriteName='scared2', columns=sColumns)
			leftDead = self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'left-dead', spriteName='scared2', columns=sColumns)
			upDead = self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'up-dead', spriteName='scared2', columns=sColumns)
			downDead = self.makeDesignedSprite(0, sColumns-1, 'down-dead', spriteName='scared2', columns=sColumns)


		# AI settings
		self.isDead = False
		self.cheeseTimer = 0

		if self.isEnemy: self.timer = 10 * enemyNames.index( self.name ) + 10
		
		self.altTarget = { 'x': -1, 'y': -1 }
		self.mode = 'scatter'

		self.setNeedToMove(0) # Holder styr på hvor meget spilleren mangler at bevæge sig for at være færdig.
		
		self.direction = ''
		self.lastDirection = ''
		self.nextDirection = ''

		# Movement settings
		self.goThroughDoor = False
		self.speed = 70
		if self.isEnemy: self.speed -= self.speed/10 # Så spøgelser er lidt langsommere end PACMAN.

		# Debug settings
		self.keepMoving = False #TODO: Fjern når du er færdig med at debugge
		

		# Entity init, meget vigtigt.
		super().__init__(rx, ry, sprites = [ right, left, down, up ], state='left')

		self.currentSprite.play = False
		if self.isEnemy:
			self._move()


	def update(self, dt):
		# få positionen på kortet

		if self.direction != '':
			suffix = ''
			if self.isDead: suffix = '-dead'
			self.setSprite(self.direction+suffix)
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

				# if self.direction == 'left' or self.direction == 'right':
				# 	self.x -= self.needToMove

				self.lastDirection = self.direction
				self.direction = ''

				

				if self.keepMoving:
					if self.isEnemy:
						#* Fjendtlige bevægelser
						self._enemy_chooseDirection()
					else:
						self._move( preferedDirection=self.lastDirection )
		

		if self.isEnemy:
			# Sørger for at spøgelserne "scatter" når de først bliver går ud af deres fængsel
			
			#! Fjern kommentering
			# if self.needToMove > 0 and self.timer != None:
			# 	self.timer -= dt
			# 	if self.timer <= 0:
			# 		self.timer = None
			# 		self.setMode()


			# Kollision
			xTile, yTile = self.MAZE.getXYTileFromPos(self.x+16, self.y+24)
			px, py = self.PACMAN.getTilePosition()
			if px >= xTile >= px:
				if py >= yTile >= py:
					self._onCollisionWithPacman()

		super().update(dt)






	#*? Interaktion
	def onKeyPress(self, symbol, modifiers):

		#! SKAL FJERNES!
		if symbol == 111: # O
			if self.isEnemy:
				self.setMode('frightened')

		if symbol == 112: # P
			if self.isEnemy:
				self._enemy_chooseDirection()

		if symbol == 105: # I
			if self.name == 'blinky':
				self.setNextMove('up')

		if symbol == 106: # J
			if self.name == 'blinky':
				self.setNextMove('left')

		if symbol == 107: # K
			if self.name == 'blinky':
				self.setNextMove('down')

		if symbol == 108: # L
			if self.name == 'blinky':
				self.setNextMove('right')


		#! -------------

		if self.isEnemy: return # ignorer alle inputs hvis denne entity er en fjende.

		# if symbol == 112: # P
		# 	self.MAZE.getPossibleDirections(self.x+16, self.y+24, True)

		if symbol == 109: # M
			self.keepMoving = not self.keepMoving
			if self.keepMoving and self.isEnemy: self._move('random')

		if symbol == 65362: # up arrow
			self.setNextMove('up')

		if symbol == 65364: # down arrow
			self.setNextMove('down')

		if symbol == 65361: # left arrow
			self.setNextMove('left')

		if symbol == 65363: # right arrow
			self.setNextMove('right')



	
	
	#*? Funktioner der bliver kaldt automatisk.

	def setMode(self, preferedMode='switch'):
		# Modes
		# 1. chase
		# 2. scatter
		# 3. frightened
		# 4. dead

		if preferedMode == 'switch':
			self.setNextMove( self.getOppositeDirection(self.lastDirection) )

			if self.mode == 'scatter':
				self.mode = 'chase'
			else:
				self.mode = 'scatter'

		else:
			self.mode = preferedMode


	def _enemy_chooseDirection(self):
		target = { 'x': self.PACMAN.x, 'y': self.PACMAN.y }

		if self.mode == 'scatter':
			target = self.MAZE.tileToPosition(enemyHomes[self.name][0], enemyHomes[self.name][1])


		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24, False)
		tileX, tileY = self.MAZE.indexToTile(index)

		directions = {
			'up': [tileX, tileY+1],
			'left': [tileX-1, tileY],
			'down': [tileX, tileY-1],
			'right': [tileX+1, tileY]
		}

		dirs = {
			'up': u,
			'left': l,
			'down': d,
			'right': r
		}
		posDirs = CONSTANTS.possibleDirections


		# Vælg en retning
		cDirection = self.getOppositeDirection(self.lastDirection)
		cDist = None

		for dir in posDirs:
			if (dirs[dir] != 1 or (dirs[dir] == 0 and (dir == 'up' or self.isDead))) and dir != self.getOppositeDirection(self.lastDirection):
				# Ikke en væg
				pos = self.MAZE.tileToPosition(directions[dir][0], directions[dir][1])

				
				width = abs( pos['x'] - target['x'] )
				height = abs( pos['y'] - target['y'] )

				dist = math.pow(width, 2) + math.pow(height, 2)

				if (cDist == None or dist < cDist) or (dir == 'up' and dirs[dir] == 0):
					cDist = dist
					if dir == 'up' and dirs[dir] == 0:
						cDist = -1
					cDirection = dir


		if self.mode == 'frightened':
			self._move('random', self.getOppositeDirection( self.lastDirection ))
		else:
			self._move(cDirection, self.getOppositeDirection( self.lastDirection ))




	def n_move(self, preferedDirection='random', ignoreDirection=''):
		if self.needToMove > 0:
			return

		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24, False)
		tileX, tileY = self.MAZE.indexToTile(index)

		_x, _y = self.MAZE.indexToTile( index )
		desiredPosition = self.MAZE.tileToPosition( _x, _y )
		self.x = desiredPosition['x'] -4
		self.y = desiredPosition['y'] -4

		directions = {
			'up': [tileX, tileY+1],
			'left': [tileX-1, tileY],
			'down': [tileX, tileY-1],
			'right': [tileX+1, tileY]
		}

		dirs = {
			'up': u,
			'left': l,
			'down': d,
			'right': r
		}

		posDirs = []

		print(dirs)

		for dir in CONSTANTS.possibleDirections:
			print(dir)
			if dirs[dir] != 1:
				posDirs.append(dir)

		

		if preferedDirection in posDirs:
			self.direction = preferedDirection
			moveVertical, moveHorizontal = self.MAZE.getMovementInfo(self.direction, index)

			if self.direction == 'right' or self.direction == 'left':
				self.setNeedToMove(moveVertical)
			elif self.direction == 'up' or self.direction == 'down':
				self.setNeedToMove(moveHorizontal)
				

	
	def _move(self, preferedDirection='random', ignoreDirection=''):
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

		dirsStrs = CONSTANTS.old_possibleDirections

		
		# Laver et array med de mulige retninger man kan gå i.
		i = 0
		for dir in dirs:
			if (dir > 1 or (dir < int(preferedDirection == 'up'))) and dirsStrs[i] != ignoreDirection:
				posDirs.append(dirsStrs[i])
			i += 1

		
		# Udvægelse af retning // konvertering af string(retning) -> int(retning)
		if self.nextDirection in posDirs:
			preferedDirection = posDirs.index(self.nextDirection)
			self.nextDirection = ''
		elif preferedDirection in posDirs:
			preferedDirection = posDirs.index(preferedDirection)
		else: # Hvis ikke, vælger den bare en tilfældig retning :/
			if self.isEnemy:
				print(posDirs)
				# if len(posDirs) == 0:
				# 	preferedDirection = dirsStrs.index(self.getOppositeDirection(self.lastDirection))
				# else:
				preferedDirection = random.randint(0, len(posDirs)-1)
			elif self.lastDirection in posDirs:
				preferedDirection = dirsStrs.index(self.getOppositeDirection(self.lastDirection))
			else:
				self.currentSprite.play = False
				return

		self.currentSprite.play = True


		# Sætter retningen, så den vender og bevæger sig korrekt.
		try:
			self.direction = posDirs[preferedDirection]
		except:
			self.direction = dirsStrs[preferedDirection]

		moveVertical, moveHorizontal = self.MAZE.getMovementInfo(self.direction, index)

		if self.direction == 'right' or self.direction == 'left':
			self.setNeedToMove(moveVertical)
		elif self.direction == 'up' or self.direction == 'down':
			self.setNeedToMove(moveHorizontal)
	


	def _onCollisionWithPacman(self):
		if self.PACMAN.cheeseTimer > 0:
			self.isDead = True
			self.setSprite('scared2')
	
	#*? Setters
	def setEnemyTarget(self, xTile=-1, yTile=-1):
		self.altTarget = { 'x': xTile, 'y': yTile }
		print(self.name, self.altTarget)

	
	
	def setNeedToMove(self, amount):
		self.NEEDtoMOVE = amount
		self.needToMove = amount



	def setNextMove(self, preferedDirection):
		if self.getOppositeDirection(preferedDirection) == self.direction:
			self.direction = preferedDirection
			self.setNeedToMove( self.NEEDtoMOVE - self.needToMove )

		self.nextDirection = preferedDirection
		self._move(preferedDirection=preferedDirection)


	#*? Getters
	def getTilePosition(self):
		index, l, r, u, d = self.MAZE.getPossibleDirections(self.x+16, self.y+24)
		return self.MAZE.indexToTile( index )
	


	def getAltTarget(self):
		if self.altTarget['x'] == -1 or self.altTarget['y'] == -1: return False
		return self.altTarget


	
	def getOppositeDirection(self, direction):
		if direction == 'right':
			return 'left'
		elif direction == 'left':
			return 'right'
		elif direction == 'up':
			return 'down'
		elif direction == 'down':
			return 'up'


	#*? Specielle funktioner som kun bliver kaldt en gang
	def makeDesignedSprite(self, beginFrame, endFrame, state, spriteName='pacman', rows=4, columns=3, speed=9):
		return entity.Sprite(f'./assets/{spriteName}.png', correspondingState=state, grid={'rows': rows, 'columns': columns}, beginFrame=beginFrame, endFrame=endFrame, animationSpeed=speed, animationBounce=True )


	