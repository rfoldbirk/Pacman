extends AnimatedSprite

onready var speed = 20
onready var dir = Vector2(0, 0)
onready var nextDir = dir
onready var moveDistance = 8
onready var deb = true
onready var timer = 0

onready var threshhold = 0.5

onready var currentTile = Vector2.ZERO
onready var nextPossibleDirections = []

onready var directionVectors = {
	"right": Vector2(1, 0),
	"up": Vector2(0, -1),
	"down": Vector2(0, 1),
	"left": Vector2(-1, 0),
}

func _ready():
	speed_scale = 2 # Animations hastighed
	
	# x: 112, y: 164 - Her skal Pacman stå
	position.x = 8*14
	position.y = 8*20.5


func _process(delta):
	var pos = getTile()
	
	if name == 'Pacman':
		pacman_process(delta)
	
	# Opdater position
	if moveDistance > 0:
		moveDistance -= abs(dir.length() * speed * delta)
		var lp = position # Den sidste position
		position += dir * speed * delta
		playing = lp != position # Hvis den stod stille, bliver animationen ikke afspillet


func pacman_process(delta):
	
	if Input.is_action_just_pressed("ui_accept"):
		print(getDirections())
	
	# Vi har lige rørt begyndelsen på et nyt tile.
	if getTile() != currentTile:
		currentTile = getTile()
		print('ny tile ', getTile())
		moveDistance = 8
		# Så skal der kigges frem!
		# Beregn ny position for raycasteren
		$Raycast.position = getPosition(getTile()) - position
		print(' ------- ', getPosition(getTile()) - position)
		
		var oldPosDirs = nextPossibleDirections
		nextPossibleDirections = getDirections()
			
		# Stopper når der mødes en væg
		var nevermind = false
		for direction in directionVectors:
			if dir == directionVectors[direction]:
				if not (direction in nextPossibleDirections):
					if nextDir == dir:
						moveDistance = 4
						nextDir = Vector2.ZERO
						nextPossibleDirections = oldPosDirs

		print(nextPossibleDirections)
		$Raycast.position = Vector2.ZERO
	else:
		# Tjek hvornår man rammer midten, fordi så skal der vælges en ny retning

		#if nextDir == Vector2.ZERO:
			#dir = nextDir
		pass
	
	
	# Mulighed for at vælge / ønske en ny retning
	for direction in nextPossibleDirections:
		if Input.is_action_pressed('ui_%s' % direction):
			animation = direction
			# Hvis det er den omvendte retning kan man godt
			if -directionVectors[direction] == dir or dir == Vector2.ZERO:
				dir = directionVectors[direction]
			else:
				nextDir = directionVectors[direction]





func getDirections():
	var possibleDirections = []

	for direction in directionVectors:
		var vector = directionVectors[direction]

		$Raycast.set_cast_to(vector * 350) # Sætter retningen på raycasteren
		$Raycast.force_raycast_update() # Raycasteren skal opdateres!
		var collisionPoint = getCollisionTile()
		
		if direction == 'up' or direction == 'left':
			collisionPoint += vector

		# Hvis den ikke kan detektere et punkt, kan man godt gå i den retning
		# Hvis punktet ikke ligger ud for Pacman kan man også gå i den retning
		if !collisionPoint or getTile() + vector != collisionPoint:
			possibleDirections.append(direction)
	
	return possibleDirections



func getTile(pos=position): # Tager objektets egen position som udgangspunkt
	return Vector2( floor(pos.x / 8), floor(pos.y / 8)+2 )


func getPosition(vector):
	return Vector2( 8*(vector.x), 8*(vector.y-1.5) )



func getCollisionTile():
	if $Raycast.is_colliding():
		return getTile($Raycast.get_collision_point())
	else:
		return false
