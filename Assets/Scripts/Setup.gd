extends Node2D


onready var enemyNames = ['Blinky', 'Pinky', 'Inky', 'Clyde']


var points = 0
var freezeTimer = 0
var frightenedTimer = 0

func _ready():
	spawn(true)


func _process(delta):
	if freezeTimer > 0:
		freezeTimer -= delta
	elif freezeTimer != 0:
		freezeTimer = 0
		pause(true)



func pause(resume=false):
	var names = enemyNames + ['Pacman']

	for Name in names:
		var entity = get_node_or_null('/root/Game/' + Name)
		if entity:
			entity.pause = not resume



func frightened(value=true):
	for Name in enemyNames:
		var ghost = get_node_or_null('/root/Game/' + Name)
		if ghost:
			ghost.mode == 'frightened':

	frightenedTimer = 7




func addPoint(type='point'):
	if type == 'powerup':
		points += 5
	elif type == 'point':
		points += 1
	elif type == 'fruit':
		points += 25
	elif type == 'ghost':
		points += 50
		pause()
		freezeTimer = 2

	get_node('/root/Game/Points').text = String(points)



func spawn(resetPoints=false):
	if resetPoints:
		points = 0

	freezeTimer = 3
	frightenedTimer = 0
	# Reset Pacman og spøgelserne

	
	var Pacman = get_node("Pacman")
	
	for Name in enemyNames:
		var newGhost = Pacman.duplicate()
		newGhost.name = Name
		
		add_child(newGhost)
