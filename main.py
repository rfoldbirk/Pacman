import pyglet, pgCharacter, maze

window = pyglet.window.Window(232, 256)


MAZE = maze.Maze()
PACMAN = pgCharacter.pgCharacter(MAZE)
BLINKY = pgCharacter.pgCharacter(MAZE, PACMAN)

# Event loop
Entities = [] # All entities
Entities.append( MAZE )
Entities.append( PACMAN )
Entities.append( pgCharacter.pgCharacter(MAZE, PACMAN) )


@window.event
def on_key_press(symbol, modifiers):
	callFuncIfItExists('onKeyPress', symbol, modifiers)


@window.event
def on_draw():
	window.clear()
	callFuncIfItExists('draw')


def on_update(dt):
	callFuncIfItExists('update', dt)


def callFuncIfItExists(func, *args):
	for E in Entities:
		if hasattr(E, func): getattr(E, func)(*args)


if __name__ == '__main__':

	# Kalder funktionen on_update 144 gange i sekundet
	pyglet.clock.schedule_interval(on_update, 1/144.0)
	pyglet.app.run()