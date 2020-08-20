import pyglet
import head

window = pyglet.window.Window()




# Event loop
Entities = [] # All entities
Entities.append( head.Head() )

@window.event
def on_key_press(symbol, modifiers):
	for E in Entities:
		if hasattr(E, 'onKeyPress'): E.onKeyPress(symbol, modifiers)


@window.event
def on_draw():
	window.clear()

	for E in Entities:
		if hasattr(E, 'draw'): E.draw()


def on_update(dt):
	for E in Entities:
		if hasattr(E, 'update'): E.update(dt)



if __name__ == '__main__':
	# Kalder funktionen on_update 120 gange i sekundet
	pyglet.clock.schedule_interval(on_update, 1/120.0)
	pyglet.app.run()