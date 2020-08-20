from pyglet import image


class Entity:
	
	def __init__(self, imagePath, x=0, y=0, width=0, height=0, rotation=0):
		self.x = x
		self.y = y
		self.rotation = rotation
		self.size = { 'width': 0, 'height': 0 }
		self.velocity = { 'x': 0, 'y': 0 }
		self.lastFrame = { 'x': x, 'y': y, 'velocity': self.velocity, 'size': self.size, 'rotation': 0 }
		self.img = image.load(imagePath)
			

	def draw(self):
		self.img.blit(self.x, self.y)

	def update(self, dt):
		self.x += self.velocity['x'] * dt
		self.y += self.velocity['y'] * dt
		
	def onKeyPress(self, symbol, modifiers):
		pass