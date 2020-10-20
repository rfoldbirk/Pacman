import pyglet, pgCharacter, maze

window = pyglet.window.Window(232, 256)


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
	global eventIndex, eventClock
	callFuncIfItExists('update', dt)

	
	if eventClock["timer"] <= 0:
		if eventIndex >= len(events): return
		# Execute event
		EX = events[eventIndex]
		setTime = eventClock['default']
		print("Executing:", EX)

		if '/t' in EX:
			setTime = extract(EX, '/t', 1)


		if "open" in EX:
			startPos = extract(EX, '-', 1)
			endPos = extract(EX, '-', 2)

			if type(startPos) == int or type(endPos) == int:
				i = 0
				for E in Entities:
					try:
						if E.name in enemyNames:
							if i >= startPos and i <= endPos:
								E.enemy_setTarget( enemyHomes[E.name][0], enemyHomes[E.name][1] )
								E.goThroughDoor = True

							i += 1
					except:
						pass

		eventClock['timer'] = setTime
		eventIndex += 1

	else:
		eventClock["timer"] -= 1 * dt



def extract(str, pattern, index, convertToInt=True):
	str0 = 0
	str0 = str.split(pattern)[index].split('/')[0]
	try:
		str0 = str0.split('/')[1]
	except:
		pass

	if convertToInt:
		return int(str0)
	else:
		return str0


def callFuncIfItExists(func, *args):
	for E in Entities:
		if hasattr(E, func): getattr(E, func)(*args)


if __name__ == '__main__':

	# Kalder funktionen on_update 144 gange i sekundet
	pyglet.clock.schedule_interval(on_update, 1/144.0)
	pyglet.app.run()