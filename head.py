import entity, random


class Head(entity.Entity):
	def __init__(self):
		rx, ry = random.randint(50, 300), random.randint(50, 300)

		speed = 2.5
		

		right = entity.Sprite('./assets/pacman.png', grid={'rows': 4, 'columns': 3}, beginFrame=9, endFrame=11, animationSpeed=speed, animationBounce=True ) 
		left = entity.Sprite('./assets/pacman.png', grid={'rows': 4, 'columns': 3}, beginFrame=6, endFrame=8, animationSpeed=speed, animationBounce=True ) 
		up = entity.Sprite('./assets/pacman.png', grid={'rows': 4, 'columns': 3}, beginFrame=3, endFrame=5, animationSpeed=speed, animationBounce=True )
		down = entity.Sprite('./assets/pacman.png', grid={'rows': 4, 'columns': 3}, beginFrame=0, endFrame=2, animationSpeed=speed, animationBounce=True )
		
		headPNG = entity.Sprite('./assets/head.png', type='Image', correspondingState='head')
		
		super().__init__(rx, ry, sprites = [ right, left, down, up ])
		
		# self.velocity = { 'x': 30, 'y': 0 }


	def onKeyPress(self, symbol, modifiers):
		if symbol == 65362: # up arrow
			super().setSprite('head')

		if symbol == 65364: # hopefully down arrow
			super().setSprite('down')