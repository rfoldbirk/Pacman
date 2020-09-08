import pyglet, head

window = pyglet.window.Window()


# Event loop
Entities = [] # All entities
Entities.append( head.Head() )



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