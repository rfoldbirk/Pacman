import entity, random


class Head(entity.Entity):
	def __init__(self):
		rx = random.randint(0, 300)
		ry = random.randint(0, 300)
		super().__init__('./assets/head.png')

		self.velocity = { 'x': 30, 'y': 55 }

	def update(self, dt):
		self.x += 70*dt

		super().update(dt)
		
	def onKeyPress(self, symbol, modifiers):
		print('Head is being activated :)')
		if symbol == 65362: # up arrow
			if self.velocity['y'] < 0: 
				self.velocity['y'] = -self.velocity['x']

		if symbol == 65364: # down arrow
			if self.velocity['y'] > 0: 
				self.velocity['y'] = -self.velocity['x']