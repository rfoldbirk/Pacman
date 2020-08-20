import entity, random


class Head:
	def __init__(self):
		rx = random.randint(0, 300)
		ry = random.randint(0, 300)
		self.entity = entity.Entity('./assets/head.png', rx, ry)

	def draw(self):
		self.entity.draw()

	def update(self, dt):
		self.entity.update(dt)
		
	def onKeyPress(self, symbol, modifiers):
		print('Head is being activated :)')
		if symbol == 65362: # up arrow
			if self.yVel < 0: 
				self.yVel = -self.xVel

		if symbol == 65364: # down arrow
			if self.yVel > 0: 
				self.yVel = -self.xVel