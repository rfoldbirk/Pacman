import entity, random, math

from constants import Constants
CONSTANTS = Constants()


enemyNames = [ 'blinky', 'pinky', 'inky', 'clyde' ]
enemyHomes = { 'blinky': [16, 20], 'pinky': [0, 20], 'inky': [16, 0], 'clyde': [0, 0] }
enemySpawnTimes = { 'blinky': 0, 'pinky': 10, 'inky': 20, 'clyde': 30 }


class pgCharacter(entity.Entity):
	def __init__(self, copy_of_maze, copy_of_pacman=False, spriteName='pacman', copy_of_blinky=False):
		self.MAZE = copy_of_maze
		self.PACMAN = copy_of_pacman
		self.BLINKY = copy_of_blinky

		self.name = spriteName
		self.isEnemy = self.name in enemyNames

		# Position
		rx, ry = 8+7*12+16, 8+8*12
		if copy_of_pacman:
			ry = 8+10*12

		# Sprites
		sColumns = 3
		if self.isEnemy: 
			sColumns = 2

		spritesArr = []

		spritesArr.append(self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'right', spriteName=spriteName, columns=sColumns))
		spritesArr.append(self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'left', spriteName=spriteName, columns=sColumns))
		spritesArr.append(self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'up', spriteName=spriteName, columns=sColumns))
		spritesArr.append(self.makeDesignedSprite(0, sColumns-1, 'down', spriteName=spriteName, columns=sColumns))
		
		if self.isEnemy:
			# Frightened
			spritesArr.append(self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'rightFrightened', spriteName='frightened2', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'leftFrightened', spriteName='frightened2', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'upFrightened', spriteName='frightened2', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(0, sColumns-1, 'downFrightened', spriteName='frightened2', columns=sColumns))

			# Dead
			spritesArr.append(self.makeDesignedSprite(sColumns*3, sColumns*3+(sColumns-1), 'rightDead', spriteName='dead', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(sColumns*2, sColumns*2+(sColumns-1), 'leftDead', spriteName='dead', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(sColumns, sColumns+(sColumns-1), 'upDead', spriteName='dead', columns=sColumns))
			spritesArr.append(self.makeDesignedSprite(0, sColumns-1, 'downDead', spriteName='dead', columns=sColumns))


		# AI settings
		self.isDead = False
		self.cheeseTimer = 0

		if self.isEnemy: self.timer = 10 * enemyNames.index( self.name ) + 10
		
		self.mode = 'scatter'

		self.setNeedToMove(0) # Holder styr på hvor meget spilleren mangler at bevæge sig for at være færdig.
		
		self.direction = ''
		self.lastDirection = ''
		self.nextDirection = ''

		# Movement settings
		self.goThroughDoor = False
		self.speed = 70
		if self.isEnemy: self.speed -= self.speed/10 # Så spøgelser er lidt langsommere end PACMAN.

		self.originalSpeed = self.speed

		# Debug settings
		self.keepMoving = True #TODO: Fjern når du er færdig med at debugge
		

		# Entity init, meget vigtigt.
		super().__init__(rx, ry, sprites = spritesArr, state='left')

		self.currentSprite.play = False
		if self.isEnemy:
			self._move()





	def update(self, dt):
		if self.mode == 'dead':
			self.speed = self.originalSpeed * 1.5
		else:
			self.speed = self.originalSpeed

		# få positionen på kortet

		if self.direction != '':
			suffix = ''
			if self.isDead: 			suffix = 'Dead'
			if self.mode == 'frightened': 	suffix = 'Frightened'

			
			
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
			# 		self.setMode() # setMode uden et argument skifter automatisk korrekt.


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


		if symbol == 105: # I
			if self.isEnemy:
				self.setMode('dead')

		if symbol == 106: # J
			if self.isEnemy:
				self.setMode('frightened')

		if symbol == 107: # K
			if self.isEnemy:
				self.setMode('scatter') # aka. go to home

		if symbol == 108: # L
			if self.isEnemy:
				self.setMode('chase')


		#! -------------

		if self.isEnemy: return # ignorer alle inputs hvis denne entity er en fjende.

		if symbol == 112: # P
			self.isDead = True

		if symbol == 109: # M
			self.MAZE.getPossibleDirections(self.x+16, self.y+24, True)

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
			self.isDead = False
			self.setNextMove( self.getOppositeDirection(self.lastDirection) )

			if self.mode == 'scatter':
				self.mode = 'chase'
			else:
				self.mode = 'scatter'

		else:
			self.mode = preferedMode
			if self.mode == 'dead':
				self.isDead = True
			else:
				self.isDead = False



	def _enemy_chooseDirection(self):

		target = { 'x': self.PACMAN.x, 'y': self.PACMAN.y }
		

		if self.isDead:
			target = self.MAZE.tileToPosition( 8, 10 )
		elif self.mode == 'scatter':
			target = self.MAZE.tileToPosition(enemyHomes[self.name][0], enemyHomes[self.name][1])
		elif self.mode == 'chase':
			# specielle bevægelses mønstre.
			if self.name == 'pinky':
				target = self.getTargetWithOffset(target, offset=4)
			
			elif self.name == 'inky':
				target = self.getTargetWithOffset(target, offset=2)
				vector = { 
					'x': target['x'] - abs(target['x'] - self.BLINKY.x), 
					'y': target['y'] - abs(target['y'] - self.BLINKY.y)
				}

				target = vector
			elif self.name == 'clyde':
				dist = math.pow(self.PACMAN.x - self.x, 2) + math.pow(self.PACMAN.y - self.y, 2)
				if dist/math.pow(12, 2) < 35:
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
			directionIsUp_orIsDead = (dir == 'up' or self.isDead)
			if (dirs[dir] != 1 or (dirs[dir] == 0 and directionIsUp_orIsDead )) and dir != self.getOppositeDirection(self.lastDirection):
				# Ikke en væg
				pos = self.MAZE.tileToPosition(directions[dir][0], directions[dir][1])

				
				width = abs( pos['x'] - target['x'] )
				height = abs( pos['y'] - target['y'] )

				dist = math.pow(width, 2) + math.pow(height, 2)

				if (cDist == None or dist < cDist) or (directionIsUp_orIsDead and dirs[dir] == 0):
					cDist = dist
					if directionIsUp_orIsDead and dirs[dir] == 0:
						cDist = -1
						if dir == 'up' and self.isDead: self.setMode('chase')
					cDirection = dir


		if self.mode == 'frightened':
			self._move('random', self.getOppositeDirection( self.lastDirection ))
		else:
			self._move(cDirection, self.getOppositeDirection( self.lastDirection ))



	
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
			if (dir > 1 or (dir < int(preferedDirection == 'up' or self.isDead))) and dirsStrs[i] != ignoreDirection:
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
				if len(posDirs) == 0:
					preferedDirection = dirsStrs.index(self.getOppositeDirection(self.lastDirection))
				else:
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
		if self.mode == 'frightened':
			# Spøgelset dør midlertidigt
			self.setMode('dead')
		
		if not self.isDead: # Hvis spøgelset er i live, dør Pacman
			self.PACMAN.isDead = True
			print('Pacman Died :(')
			exit()
	


	#*? Setters	
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
	

	def getTargetWithOffset(self, target, offset):
		tileSize = 12
		if self.PACMAN.lastDirection == 'left':
			target['x'] -= tileSize * offset
		elif self.PACMAN.lastDirection == 'right':
			target['x'] += tileSize * offset
		elif self.PACMAN.lastDirection == 'down':
			target['y'] -= tileSize * offset
		elif self.PACMAN.lastDirection == 'up':
			target['y'] += tileSize * offset

		return target



	
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
	def makeDesignedSprite(self, beginFrame, endFrame, state, spriteName='pacman', rows=4, columns=2, speed=9):
		return entity.Sprite(f'./assets/{spriteName}.png', correspondingState=state, grid={'rows': rows, 'columns': columns}, beginFrame=beginFrame, endFrame=endFrame, animationSpeed=speed, animationBounce=True )


	