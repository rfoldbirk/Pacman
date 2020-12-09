extends AnimatedSprite

onready var pause = true

onready var movementSpeed = 40
onready var defaultMovementSpeed = movementSpeed
onready var currentDirection = Vector2(0, 0)
onready var nextDirection = ''
onready var moveDistance = 4
onready var moveDistanceMax = moveDistance
onready var ghost_correctMoveDistance_debiance = true
onready var timer = 0

onready var ghostIsAligned = false

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

var stuckForFrames = 0

onready var enemyNames = ['Blinky', 'Pinky', 'Inky', 'Clyde']
onready var isGhost = name in enemyNames
onready var trapped = true
onready var mode = 'chase'
onready var lastMode = 'scatter'


# Sørger for at Blinky, begynder at jagte Pacman efter et stykke tid
# Dog kun i starten
onready var switchTimerMax = 5
onready var switchTimerDeb = true
onready var switchTimer = 0


onready var foundPacman = false
onready var use_aStar = true

onready var Game = get_node('/root/Game')


func _ready():
	speed_scale = 3 # Animations hastighed
	
	# x: 112, y: 164 - Her skal Pacman stå
	position.x = 8*12.5#14
	position.y = 8*32.5#20.5

	if isGhost:
		defaultMovementSpeed -= 5
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
				position.x = 8*14
				position.y -= 8
		else:
			position.x = 8*14
			position.y = 8*14.5 # 8*14.5
			
			# currentDirection = directionVectors['right']
			# nextDirection = 'right'

			currentDirection = Vector2()
			nextDirection = ''

			moveDistance = 4
			moveDistanceMax = 8
			
			mode = 'chase'
			trapped = false
	else:
		mode = 'alive'

	setAnimation('up')




func _process(delta):
	if pause: 
		if name == 'Pacman' and mode == 'die':
			if frame == 19:
				get_tree().change_scene("res://Scenes/Menu.tscn")
			setAnimation('die')
			playing = true
		else:
			playing = false
		return

	# Afspiller den korrekte animation
	if mode == 'die':
		# Hvis det er pacman hedder 
		setAnimation(mode)
	else:
		for key in directionVectors:
			if directionVectors[key] == currentDirection:
				if isGhost and mode == 'frightened':
					setAnimation(mode)
				else:
					setAnimation(key)


	# Når pacman / spøgelset er stoppet med at bevæge sig, finder den en ny retning ud fra currentDirection og nextDirection
	if moveDistance <= 0:
		nextPossibleDirections = getDirections()

		if moveDistance < 0:
			movementSpeed = defaultMovementSpeed
			if allowCorrections and moveDistanceMax == 8 and (isGhost or (mode != 'die' and not isGhost)):
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
		
		if ((!isGhost and mode != 'die') or isGhost):
			position += currentDirection * movementSpeed * delta

	if (isGhost or (not isGhost and mode != 'die')):
		playing = lp != position # Hvis den stod stille, bliver animationen ikke afspillet	
	
	if isGhost:
		ghost_process(delta)
	else:
		pacman_process(delta)



var asObj = {
	'main': [],
	'wait': [],
	'new': [],
	'deb': true,
	'occupied': []
}


func AStarChooseTile():

	var posDirs = getDirectionsAlt()
	var posDirs_equal2 = posDirs.size() == 2
	var nxtDirIsInPosDirs = nextDirection in posDirs

	if posDirs_equal2 and nxtDirIsInPosDirs and currentDirection != Vector2():
		return

	currentDirection = Vector2()

	# hvis der er mere end 1 mulighed, send videre.
	if foundPacman:
		print('Found! - ', foundPacman)
		nextDirection = foundPacman
		currentDirection = directionVectors[nextDirection]
		foundPacman = false
		asObj.deb = true

		if moveDistance == 0:
			moveDistance = 8


		# fjern
		var pathMap = get_node('/root/Game/PathMap')
		for _x in range(0, 28):
			for _y in range(5, 36):
				pathMap.set_cellv(Vector2(_x, _y), -1)
		

		asObj.main = []
		asObj.new = []
		asObj.wait = []
		asObj.occupied = []
	else:
		var lastDirection = nextDirection

		nextDirection = ''

		if asObj.deb:
			asObj.deb = false
			print('Searching')

			var i = 0
			var offset = Vector2()
			


			while not foundPacman:
				i += 1
				if i > 3: break

				asObj.wait = asObj.new
				asObj.new = []

				if (asObj.main + asObj.new + asObj.wait).size() == 0:
					aStar_getShortest(Vector2(), false, lastDirection)
				else:
					var index = 0
					# udforkser først og fremmest de retninger der kommer tættere på...
					for x in asObj.main:
						index += 1
						aStar_getShortest(x.offset, x.firstDirection, x.lastDirection)
						asObj.main.remove(index-1)

					if asObj.main.size() == 0:
						index = 0
						for x in asObj.wait:
							index += 1
							aStar_getShortest(x.offset, x.firstDirection, x.lastDirection)
							asObj.wait.remove(index-1)

			#ghost_chooseTile()

func aStar_getShortest(offset=Vector2(), firstDirection=false, lastDirection=false):
	var ghostPosition = position + offset*8

	var Pacman = get_node_or_null("/root/Game/Pacman")
	var currentDistance = (Pacman.position - ghostPosition).length()

	# Tjekker om vi står oven på Pacman
	if getTile(position + offset*8) == getTile(Pacman.position):
		foundPacman = firstDirection

	var objArray = []

	# hvis dette sker, er det første gang aStar bliver kaldt
	for direction in getDirectionsAlt(offset):
		var newDistance = (Pacman.position - (ghostPosition + directionVectors[direction]*8)).length()

		var newPos = getTile() + offset + directionVectors[direction]
		if reverseDirection(lastDirection) != direction and not (newPos in asObj.occupied):
			asObj.occupied.append(newPos)
			var pathMap = get_node('/root/Game/PathMap')
			pathMap.set_cellv(getTile() + offset, 0)

			var _fd = firstDirection
			if not _fd: _fd = direction

			var obj = {
				'firstDirection': _fd,
				'lastDirection': direction,
				'offset': offset + directionVectors[direction],
				'score': currentDistance - newDistance
			}

			objArray.append(obj)

	if objArray.size() == 0:
		return

	# udregn en gennemsnitlig score
	var genScore = 0
	for x in objArray:
		genScore += x.score

	genScore = genScore / (objArray.size()+2)

	print('total: ', genScore)

	var _index = 0
	for x in objArray:
		if x.score > 0 or x.score > genScore:
			print(x)
			asObj.main.push_back(x)
		else:
			asObj.new.push_back(x)
		_index += 1

			







func ghost_chooseTile():
	allowCorrections = false
	var lastDirection = nextDirection

	if trapped:
		# Hvis den er fanget, bevæger spøgelset sig op og ned
		currentDirection = Vector2.ZERO
		nextDirection = ''
		
		if lastDirection in nextPossibleDirections:
			nextDirection = lastDirection
		else:
			nextDirection = reverseDirection(lastDirection)
			
		
	else:
		# Ellers skal den komme ud, via en bestemt gang
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

					if mode == 'die':
						mode = 'chase'
						ghost_correctMoveDistance_debiance = true
						ghostIsAligned = false
					if currentPosition.y == 17:
						moveDistanceMax = 11 # Meget vigtigt med .5, da de ellers ikke kommer helt op
		else: 
			# Uden for hjemmet
			var indexOfOppositeDirection = nextPossibleDirections.find( reverseDirection(lastDirection) )
			if indexOfOppositeDirection >= 0:
				nextPossibleDirections.remove(indexOfOppositeDirection)


			if mode == 'frightened':
				if nextPossibleDirections.size() > 0:
					var randomNum = rand_range(0, nextPossibleDirections.size())
					nextDirection = nextPossibleDirections[randomNum]
				else:
					nextDirection = reverseDirection(lastDirection)


			else:
				var PM = get_node_or_null("/root/Game/Pacman")
				var PM_currentDirection = PM.get('currentDirection')
				var currentRecord = -1
				var winnerDirection = ''

				if mode == 'chase' and use_aStar:
					AStarChooseTile()
					return

				for direction in nextPossibleDirections:
					if direction == reverseDirection(lastDirection): continue
					
					var TargetTile = getTile(PM.position)
					var myPos = getTile() + directionVectors[direction]

					if name == 'Blinky':
						if mode == 'scatter':
							TargetTile = Vector2(26, -2)


					if name == 'Pinky':
						TargetTile += PM_currentDirection * 4
						if mode == 'scatter':
							TargetTile = Vector2(0, -2)


					if name == 'Inky':
						TargetTile += PM_currentDirection * 2
						var Blinky = get_node_or_null('/root/Game/Blinky')
						
						if Blinky:
							var Bgt = getTile(Blinky.position)
							var vectorBetweenPacman_and_Blinky = Bgt - TargetTile
							var vNormal = vectorBetweenPacman_and_Blinky.normalized()
							TargetTile = TargetTile + vNormal * vectorBetweenPacman_and_Blinky.length()

						if mode == 'scatter':
							TargetTile = Vector2(26, 37)


					if name == 'Clyde':
						var _distanceVector = myPos - TargetTile
						if _distanceVector.length() <= 8 or mode == 'scatter':
							TargetTile = Vector2(0, 37)


					if mode == 'die':
						TargetTile = Vector2(13, 16)


					var distanceVector = myPos - TargetTile

					var distance = distanceVector.length()
					
					if distance < currentRecord or currentRecord == -1:
						currentRecord = distance
						winnerDirection = direction

				nextDirection = winnerDirection

			
			allowCorrections = true
			if ghost_correctMoveDistance_debiance:
				ghost_correctMoveDistance_debiance = false
				moveDistanceMax = 4
				if switchTimerDeb and name == 'Blinky':
					switchTimer = switchTimerMax
					switchTimerDeb = false
			else:
				moveDistanceMax = 8


			if mode == 'die':
				if currentPosition.x >= 13 and currentPosition.x <= 14:
					if currentPosition.y >= 16 and currentPosition.y <= 19:
						allowCorrections = false
						if !ghostIsAligned:
							moveDistanceMax = 30
							moveDistance = 4

							nextDirection = 'down'
							ignoreCollisionsMomentarily = true
							
							ghostIsAligned = true



func ghost_process(_delta):
	if mode == 'die':
		movementSpeed = defaultMovementSpeed * 4


	# Når den skifter fra en mode til en andnen
	if mode != lastMode:
		lastMode = mode
		if not (mode in 'die frightened') and not (lastMode in 'die frightened'):
			var rDir = reverseDirection(nextDirection)
			var currentPosition = getTile()

			# Tjekker først og fremmest at den omvendte retning er gyldig,
			# hvorefter den tjekker om spøgelset er inden i deres base
			if rDir != '' and not (currentPosition.x >= 11 and currentPosition.x <= 16 and currentPosition.y >= 17 and currentPosition.y <= 21):
				nextDirection = rDir
				if currentDirection == -directionVectors[nextDirection] and moveDistance > 0:
					moveDistance = moveDistanceMax - moveDistance
					currentDirection = directionVectors[nextDirection]


	# Sørger for at den skifter fra scatter til chase, men er kun gyldigt for Blinky
	if switchTimer > 0:
		pass
		#TODO: switchTimer -= _delta
	elif switchTimer != 0:
		switchTimer = 0
		if mode == 'scatter':
			mode = 'chase'
		elif not mode in 'frightened die':
			mode = 'scatter'


	var Pacman = get_node_or_null("/root/Game/Pacman")
	if Pacman:
		if getTile(Pacman.position) == getTile():
			# Kollision med Pacman
			if mode == 'frightened':
				# Dead
				mode = 'die'
				Game.addPoint('ghost')
			elif mode != 'die':
				Pacman.mode = 'die'
				Game.pause()

	if Input.is_action_just_pressed("ui_cancel"):
		asObj.deb = true
		ghost_chooseTile()



func pacman_process(_delta):
	# Mulighed for at vælge / ønske en ny retning
	for direction in directionVectors:
		if Input.is_action_just_pressed('ui_%s' % direction):
			# Laver et ønske om den næste retning.
			nextDirection = direction
			if currentDirection == Vector2.ZERO:
				if direction in getDirections():
					currentDirection = directionVectors[direction]

			# Hvis den omvendte retning ønskes og den er i bevægelse
			if currentDirection == -directionVectors[nextDirection] and moveDistance > 0:
				moveDistance = moveDistanceMax - moveDistance
				currentDirection = directionVectors[nextDirection]


	# Indsamling af point
	var PointMap = get_node_or_null('/root/Game/PointMap')
	if PointMap:
		var pos = getTile()
		var cell = PointMap.get_cellv(pos)
		if cell == 12 or cell == 15:
			movementSpeed = defaultMovementSpeed / 1.3
			PointMap.set_cellv(pos, -2)
			if cell == 15:
				Game.addPoint('powerup')
			else:
				Game.addPoint()



# Returnere et array med mulige retninger
func getDirections(debug=false, offset=Vector2()):
	var possibleDirections = []
	var oldRCPos = $Raycast.position
	$Raycast.position += offset * 8

	for direction in directionVectors:
		var vector = directionVectors[direction]

		$Raycast.set_cast_to(vector * 350) # Sætter retningen på raycasteren
		$Raycast.force_raycast_update() # Raycasteren skal opdateres!
		$Raycast.force_update_transform()
		var collisionPoint = getCollisionTile()
		
		if direction == 'up' or direction == 'left':
			collisionPoint += vector

		# Hvis den ikke kan detektere et punkt, kan man godt gå i den retning
		# Hvis punktet ikke ligger ud for Pacman kan man også gå i den retning
		if !collisionPoint or getTile() + vector != collisionPoint:
			possibleDirections.append(direction)
	
	$Raycast.position = oldRCPos

	if debug: print(possibleDirections)
	return possibleDirections



func getDirectionsAlt(offset=Vector2()):
	var validDirections = []

	var Map = get_node_or_null('/root/Game/Map')


	for direction in directionVectors:
		var cell = Map.get_cellv(getTile(position + offset*8) + directionVectors[direction])

		if cell == -1:
			validDirections.append(direction)

	return validDirections




func setAnimation(anim):
	var customPrefix = name

	if isGhost and anim == 'die':
		anim = nextDirection
		customPrefix = 'Dead'


	var animationPlaceholder = '{CharacterName}_{Animation}'
	animationPlaceholder = animationPlaceholder.format({"CharacterName": customPrefix})
	var actualAnimation = animationPlaceholder.format({"Animation": anim})

	# Undtagelser
	if isGhost:
		if anim == 'frightened':
			if not Game.firstStageFright:
				anim = 'frightened_ending'
			animation = anim
			return
	
	
	animation = actualAnimation

	


func reverseDirection(direction):
	if direction == 'up': return 'down'
	if direction == 'down': return 'up'
	if direction == 'right': return 'left'
	if direction == 'left': return 'right'

	return direction


func getTile(pos=position): # Tager objektets egen position som udgangspunkt
	return Vector2( floor(pos.x / 8), floor(pos.y / 8)+2 )


func getPosition(vector):
	return Vector2( 8*(vector.x), 8*(vector.y-1.5) )



func getCollisionTile():
	if $Raycast.is_colliding():
		return getTile($Raycast.get_collision_point())
	else:
		return false
