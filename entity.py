from pyglet import image

class Entity:
	def __init__(self,  
			x = 0, y = 0,
			rotation = 0, 
			sprites = [],
			state = 'main'
		):

		self.x, self.y = x, y
		self.rotation = rotation
		self.velocity = { 'x': 0, 'y': 0 }
		
		self.state = state
		self.states = {}

		for sprite in sprites:
			self.states[sprite.correspondingState] = sprite
		
		# vælger det rigtige sprite ud fra state
		self.setSprite(self.state)
		
		# dette bliver vigtigt når man skal regne på kollision.
		self.lastFrame = { 'x': x, 'y': y, 'velocity': self.velocity, 'size': self.size, 'rotation': 0 }

	
	def setSprite(self, state):
		self.currentSprite = self.states[ state ]
		self.currentSprite.resetFrames()
		self.size = self.currentSprite.size


	def draw(self):
		self.currentSprite.draw(self.x, self.y)


	def update(self, dt):
		# Opdatering af position ud fra velocity
		self.x += self.velocity['x'] * dt
		self.y += self.velocity['y'] * dt

		# Velocity degredation
		
		
		# Animation
		self.currentSprite.update(dt)

		
	def onKeyPress(self, symbol, modifiers):
		pass






class Sprite:
	def __init__(self, source, correspondingState='main', type='SpriteSheet', grid={ 'rows': 1, 'columns': 6 }, beginFrame=0, endFrame=0, animationBounce=False, animationSpeed=5):
		self.correspondingState = correspondingState
		self.source = source
		self.type = type
		self.image = image.load(source)

		self.size = { 'width': self.image.width, 'height': self.image.height }
		
		if type == 'SpriteSheet':
			self.grid = grid
			self.spritesheet = image.ImageGrid(self.image, self.grid['rows'], self.grid['columns'])

			self.frameControl = { 'begin': beginFrame, 'end': endFrame }
			if endFrame == -1:
				self.frameControl['end'] = grid['rows'] * grid['columns']

			self.frame = beginFrame
			self.image = self.spritesheet[ self.frame ]

			self.animationBounce = animationBounce
			self.incrementWithValue = 1

			if (beginFrame == endFrame) and beginFrame == 0:
				self.incrementWithValue = 0

			self.timer = {
				'animationSpeed': animationSpeed,
				'count': 0
			}


	def draw(self, x, y):
		self.image.blit(x, y)


	def resetFrames(self):
		if self.type == 'SpriteSheet':
			self.frame = self.frameControl['begin']
			self.image = self.spritesheet[ self.frame ]


	def update(self, dt):
		if self.type == 'SpriteSheet':
			self.timer['count'] += dt * self.timer['animationSpeed']
			if self.timer['count'] >= 1:
				self.timer['count'] = 0
				self.incrementFrame()


	def incrementFrame(self):
		if self.type == 'SpriteSheet':
			self.frame += self.incrementWithValue
			correctFrame = 0

			if self.frame > self.frameControl['end'] or self.frame < self.frameControl['begin']:
				self.incrementWithValue += 0-self.incrementWithValue*2
				correctFrame = self.incrementWithValue * 2

			self.frame += correctFrame

			self.image = self.spritesheet[ self.frame ]






























