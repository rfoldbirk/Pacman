import pyglet, pgCharacter, maze, events

window = pyglet.window.Window(232, 296)
pyglet.gl.glClearColor(0,0,0,0)

MAZE = maze.Maze()
PACMAN = pgCharacter.pgCharacter(MAZE)
BLINKY = pgCharacter.pgCharacter(MAZE, PACMAN)

# Event loop
Entities = [] # All entities
Entities.append( MAZE )
Entities.append( PACMAN )
Entities.append( pgCharacter.pgCharacter(MAZE, PACMAN, "blinky") )
Entities.append( pgCharacter.pgCharacter(MAZE, PACMAN, "pinky") )
Entities.append( pgCharacter.pgCharacter(MAZE, PACMAN, "inky") )
Entities.append( pgCharacter.pgCharacter(MAZE, PACMAN, "clyde") )

Entities.append( events.EventSystem(Entities) )



enemyNames = "blinky - pinky - inky - clyde"
enemyHomes = { "blinky": [16, 18], "pinky": [0, 18], "inky": [16, 0], "clyde": [0, 0] }

events = ['open-0-0/t5', 'open-1-1/t5', 'open-2-2/t5', 'open-3-3/t5']
eventIndex = 0
eventClock = { "timer": 0, "default": 10 }


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