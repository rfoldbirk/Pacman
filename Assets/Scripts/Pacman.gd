extends AnimatedSprite

onready var movementSpeed = 40
onready var currentDirection = Vector2(0, 0)
onready var nextDirection = ''
onready var moveDistance = 4
onready var moveDistanceMax = moveDistance
onready var ghost_correctMoveDistance_debiance = true
onready var timer = 0

onready var keepMoving = true

onready var currentTile = Vector2.ZERO
onready var nextPossibleDirections = []
onready var ignoreCollisionsMomentarily = false
onready var allowCorrections = true

onready var directionVectors = {
	"right": Vector2(1, 0),
	"up": Vector2(0, -1),
	"down": Vector2(0, 1),
	"left": Vector2(-1, 0),
}

onready var enemyNames = ['Blinky', 'Pinky', 'Inky', 'Clyde']
onready var isGhost = name in enemyNames
onready var trapped = true
onready var ghostMode = 'chase'


func _ready():
	speed_scale = 3 # Animations hastighed
	
	# x: 112, y: 164 - Her skal Pacman stå
	position.x = 8*14
	position.y = 8*20.5

	if isGhost:
		nextDirection = 'up'
		currentDirection = directionVectors[nextDirection]

		moveDistance = 1
		moveDistanceMax = moveDistance

		if name != 'Blinky': 
			position.y = 8*18
			position.x = 8*12 + 16* (enemyNames.find(name)-1) # der skal stå: -1
			if name == 'Clyde': 
				position.x -= 1
			if name == 'Inky':
				position.x -= 0.5
				position.y -= 8
		else:
			trapped = false
			moveDistance = 0
			nextDirection = 'right'
			position.y = 8*14.5 # 8*14.5

	setAnimation('up')


func _process(delta):
	# Afspiller den korrekte animation
	for key in directionVectors:
		if directionVectors[key] == currentDirection:
			setAnimation(key)

	# Når pacman / spøgelset er stoppet med at bevæge sig, finder den en ny retning ud fra currentDirection og nextDirection
	if moveDistance <= 0:
		nextPossibleDirections = getDirections()

		if moveDistance < 0:
			if allowCorrections:
				var desiredPosition = getPosition(getTile()) + Vector2(4, 0)
				position = desiredPosition
			
			if isGhost: ghost_chooseTile() # Giver spøgelset en chance for at vælge retning
			if !keepMoving: 
				currentDirection = Vector2.ZERO
				nextDirection = ''
			position += currentDirection * moveDistance
			moveDistance = 0
		

		# Sørger for at den bliver ved med at bevæge sig
		if nextDirection in nextPossibleDirections or ignoreCollisionsMomentarily: # Vælger den nye retning, hvis den altså er gyldig
			ignoreCollisionsMomentarily = false
			currentDirection = directionVectors[nextDirection] # Sætter retningen
			if name == 'Pacman': moveDistanceMax = 8
			moveDistance = moveDistanceMax
		else: # Ellers forsøger den at forsætte i samme retning som sidst.
			for key in directionVectors:
				if directionVectors[key] == currentDirection:
					if key in nextPossibleDirections:
						moveDistance = 8
	
	
	# Opdater position
	var lp = position # Den sidste position
	if moveDistance > 0:
		moveDistance -= abs(currentDirection.length() * movementSpeed * delta)
		
		position += currentDirection * movementSpeed * delta
	playing = lp != position # Hvis den stod stille, bliver animationen ikke afspillet


	if isGhost:
		ghost_process(delta)
	else:
		pacman_process(delta)


func ghost_chooseTile():
	allowCorrections = false
	var lastDirection = nextDirection

	if trapped:
		currentDirection = Vector2.ZERO
		nextDirection = ''
		
		if lastDirection in nextPossibleDirections:
			nextDirection = lastDirection
		else:
			nextDirection = reverseDirection(lastDirection)
			
		
	else:
		var currentPosition = getTile()

		if currentPosition.x >= 11 and currentPosition.x <= 16 and currentPosition.y >= 17 and currentPosition.y <= 21:
			if 'down' in nextPossibleDirections and currentPosition.x != 14:
				# Går lidt ned
				nextDirection = 'down'
			else:
				# Find centrum
				moveDistanceMax = 1
				if currentPosition.x < 14:
					nextDirection = 'right'
				elif currentPosition.x > 14:
					nextDirection = 'left'
					moveDistanceMax = 14
				else:
					nextDirection = 'up'
					ignoreCollisionsMomentarily = true
					if currentPosition.y == 17:
						moveDistanceMax = 10.5
				pass
		else: # Uden for hjemmet
			var indexOfOppositeDirection = nextPossibleDirections.find( reverseDirection(lastDirection) )
			if indexOfOppositeDirection > 0:
				nextPossibleDirections.remove(indexOfOppositeDirection)


			if ghostMode == 'frightened':
				if nextPossibleDirections.size() > 0:
					var randomNum = rand_range(0, nextPossibleDirections.size())
					nextDirection = nextPossibleDirections[randomNum]
				else:
					nextDirection = reverseDirection(lastDirection)


			elif ghostMode == 'chase':
				var PM = get_node_or_null("/root/Game/Pacman")
				var PMC = PM.get('currentDirection')
				var currentRecord = -1
				var winnerDirection = ''


				for direction in nextPossibleDirections:
					if direction == reverseDirection(lastDirection): continue
					
					var PacmanPos = getTile(PM.position)
					var myPos = getTile() + directionVectors[direction]

					if name == 'Pinky':
						PacmanPos += PMC * 4

					if name == 'Inky':
						PacmanPos += PMC * 2
						var Blinky = get_node_or_null('/root/Game/Blinky')
						var Bgt = getTile(Blinky.position)
						
						if Blinky:
							var vectorBetweenPacman_and_Blinky = Bgt - PacmanPos
							vectorBetweenPacman_and_Blinky *= Vector2(-1, -1) # Inversed
							PacmanPos = getTile(get_node('/root/Game/Blinky')).position + vectorBetweenPacman_and_Blinky

					if name == 'Clyde':
						var _distanceVector = myPos - PacmanPos
						if _distanceVector.length() <= 8:
							PacmanPos = Vector2(0, 37)

					var distanceVector = myPos - PacmanPos

					var distance = distanceVector.length()
					
					if distance < currentRecord or currentRecord == -1:
						currentRecord = distance
						winnerDirection = direction

				nextDirection = winnerDirection


			
			allowCorrections = true
			if ghost_correctMoveDistance_debiance:
				ghost_correctMoveDistance_debiance = false
				moveDistanceMax = 4
				nextDirection = 'right'
			else:
				moveDistanceMax = 8


func ghost_process(_delta):
	#nextDirection = ''

	if Input.is_action_just_pressed("ui_cancel"):
		trapped = false
		# nextDirection = 'down'
		# print(getTile())



func pacman_process(_delta):
	# Debug
	if Input.is_action_just_pressed("ui_accept"):
		print(getDirections())
	# -------------------------------------------

	
	# Mulighed for at vælge / ønske en ny retning
	for direction in directionVectors:
		if Input.is_action_just_pressed('ui_%s' % direction):
			# Laver et ønske om den næste retning.
			nextDirection = direction
			if currentDirection == Vector2.ZERO:
				currentDirection = directionVectors[direction]

			# Hvis den omvendte retning ønskes og den er i bevægelse
			if currentDirection == -directionVectors[nextDirection] and moveDistance > 0:
				moveDistance = moveDistanceMax - moveDistance
				currentDirection = directionVectors[nextDirection]





# Returnere et array med mulige retninger
func getDirections(ghost_correctMoveDistance_debianceug=false):
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
	
	if ghost_correctMoveDistance_debianceug: print(possibleDirections)
	return possibleDirections




func setAnimation(anim):
	var animationPlaceholder = '{CharacterName}_{Animation}'
	animationPlaceholder = animationPlaceholder.format({"CharacterName": name})
	var actualAnimation = animationPlaceholder.format({"Animation": anim})
	animation = actualAnimation


func reverseDirection(direction):
	if direction == 'up': return 'down'
	if direction == 'down': return 'up'
	if direction == 'right': return 'left'
	if direction == 'left': return 'right'


func getTile(pos=position): # Tager objektets egen position som udgangspunkt
	return Vector2( floor(pos.x / 8), floor(pos.y / 8)+2 )


func getPosition(vector):
	return Vector2( 8*(vector.x), 8*(vector.y-1.5) )



func getCollisionTile():
	if $Raycast.is_colliding():
		return getTile($Raycast.get_collision_point())
	else:
		return false