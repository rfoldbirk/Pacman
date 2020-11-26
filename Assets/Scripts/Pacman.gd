extends AnimatedSprite

onready var speed = 20
onready var dir = Vector2(-1, 0)
onready var lastDir = dir
onready var deb = true

func _ready():
	speed_scale = 2 # Animations hastighed
	
	# x: 112, y: 164 - Her skal Pacman stå
	position.x = 8*14
	position.y = 8*20 + 4


func _process(delta):
	# Opdater raycasterens retning
	$Raycast.cast_to = dir * 30
	
	var pos = getTile()
	
	playerThings(delta)
	
	# Opdater position
	var lp = position # Den sidste position
	position += dir * speed * delta
	playing = lp != position # Hvis den stod stille, bliver animationen ikke afspillet
	


func playerThings(delta):
	dir = Vector2(0, 0)
	
	# Der mangler et tjek, så man ikke bare bevæger sig i en retning man ikke kan.
	
	if Input.is_action_pressed("ui_right"):
		dir.x += 1
	if Input.is_action_pressed("ui_left"):
		dir.x -= 1
	if Input.is_action_pressed("ui_up"):
		dir.y -= 1
	if Input.is_action_pressed("ui_down"):
		dir.y += 1


	# Sørger for at man kun kan gå i én retning
	if dir.x != 0:
		dir.y = 0
	elif dir.y != 0:
		dir.x = 0

	# Sørger for at den holder retningen
	if dir == Vector2.ZERO: 
		dir = lastDir
	else:
		lastDir = dir

func getTile(pos=position):
	return Vector2( floor(pos.x / 8), floor(pos.y / 8)+2 )


func getNextTile():
	if $Raycast.is_colliding():
		return getTile($Raycast.get_collision_point())
	else:
		return false
