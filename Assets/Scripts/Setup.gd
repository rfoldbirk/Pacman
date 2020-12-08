extends Node2D


onready var enemyNames = ['Blinky'] #, 'Pinky', 'Inky', 'Clyde']


var points = 0
var freezeTimer = 0
var frightenedTimer = 0
var firstStageFright = true
var switchTimer = 0

onready var Map = get_node('/root/Game/Map')
onready var PointMap = get_node('/root/Game/PointMap')



func _ready():
	spawn(true)


func _process(delta):
	if freezeTimer > 0:
		freezeTimer -= delta
	elif freezeTimer != 0:
		freezeTimer = 0
		pause(true)


	if frightenedTimer > 0:
		frightenedTimer -= delta
	elif frightenedTimer != 0:
		if firstStageFright:
			firstStageFright = false
			frightenedTimer = 3
		else:
			frightenedTimer = 0
			firstStageFright = true
			frightened(false) # Gør spøgelserne normale



func pause(resume=false):
	var names = enemyNames + ['Pacman']

	for Name in names:
		var entity = get_node_or_null('/root/Game/' + Name)
		if entity:
			entity.pause = not resume



func switchBetweenScatterAndChase():
	for Name in enemyNames:
		var ghost = get_node_or_null('/root/Game/' + Name)
		if ghost:
			if ghost.mode == 'chase':
				ghost.mode = 'scatter'
			else:
				ghost.mode = 'chase'

			switchTimer = 25



func frightened(value=true):
	for Name in enemyNames:
		var ghost = get_node_or_null('/root/Game/' + Name)
		if ghost:
			if ghost.mode != 'die':
				if value:
					ghost.mode = 'frightened'
					frightenedTimer = 7
				else:
					ghost.mode = 'chase'

	




func addPoint(type='point'):
	if type == 'powerup':
		points += 5
		frightened()
	elif type == 'point':
		points += 1
	elif type == 'fruit':
		points += 25
	elif type == 'ghost':
		points += 50
		pause()
		freezeTimer = 1

	get_node('/root/Game/Points').text = String(points)



func spawn(resetPoints=false):
	if resetPoints:
		points = 0

	switchTimer = 50
	freezeTimer = 1
	frightenedTimer = 0
	# Reset Pacman og spøgelserne

	for x in range(27):
		for y in range(35):
			var cCell = Map.get_cellv(Vector2(x, y))
			if String(cCell) in '12  15':
				Map.set_cellv(Vector2(x, y), -1)
				PointMap.set_cellv(Vector2(x, y), cCell)

	
	var Pacman = get_node("Pacman")
	Pacman.set_z_index(0)
	
	for Name in enemyNames:
		var newGhost = Pacman.duplicate()
		newGhost.name = Name
		
		add_child(newGhost)

	Pacman.set_z_index(1)
