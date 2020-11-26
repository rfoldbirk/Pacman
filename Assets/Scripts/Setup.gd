extends Node2D

func _ready():
	var enemyNames = ['Blinky', 'Pinky', 'Inky', 'Clyde']
	var Pacman = get_node("Pacman")
	
	for name in enemyNames:
		var newGhost = Pacman.duplicate()
		newGhost.name = name
		
		add_child(newGhost)
