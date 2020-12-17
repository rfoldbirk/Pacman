extends AnimatedSprite


onready var Game = get_node('/root/Game')
onready var Map = get_node_or_null('/root/Game/Map')
onready var PathMap = get_node('/root/Game/PathMap')

onready var enemyNames = ['Blinky', 'Pinky', 'Inky', 'Clyde']
onready var directionVectors = {
	"right": Vector2(1, 0),
	"up": Vector2(0, -1),
	"down": Vector2(0, 1),
	"left": Vector2(-1, 0),
}

onready var allowCorrections = true
onready var triggedMVD_zeroEvent = false

var killedPacman

var alignmentInfo


var pause

var mode
var lastMode
var use_aStar
var show_route
var trapped
var released


var currentVectorDirection
var nextDirection
var lastDirection

var movementSpeed
var defaultMovementSpeed

var ignoreCollisionsMomentarily

var moveDistance
var moveDistanceMode

var isGhost

var switchToChaseTimer
var hasMadeSwitch

func _ready():
	speed_scale = 3
	setup()


func setup():

	switchToChaseTimer = 5
	hasMadeSwitch = false

	allowCorrections = true
	triggedMVD_zeroEvent = false
	killedPacman = false
	pause = true

	alignmentInfo = {
		'needIt': true,
		'stack': 0,
		'max': 1
	}
	if name in 'Pinky Inky Clyde': alignmentInfo.max = 2
	
	# Specifikt for spøgelser
	isGhost = name in enemyNames
	use_aStar = get_node('/root/Game/Menu').Menu._vars['A*']
	show_route = get_node('/root/Game/Menu').Menu._vars['SR']
	trapped = true
	

	mode = 'scatter'

	currentVectorDirection = Vector2()
	nextDirection = ''
	lastDirection = '' #! not used

	moveDistance = -1
	moveDistanceMode = 'short' # precise, short, long

	movementSpeed = 40
	if isGhost: movementSpeed -= 6
	defaultMovementSpeed = movementSpeed

	ignoreCollisionsMomentarily = false


	# Placering af de forskellige karakterer
	if name == 'Pacman':
		position = getPositionFromTile(Vector2(13.5, 22))

	if name == 'Blinky':
		trapped = false
		mode = 'scatter'
		position = getPositionFromTile(Vector2(13.5, 16))

	if name == 'Pinky':
		position = getPositionFromTile(Vector2(11.5, 19))

	if name == 'Inky':
		position = getPositionFromTile(Vector2(13.5, 19))

	if name == 'Clyde':
		position = getPositionFromTile(Vector2(15.5, 19))

	setAnimation('up')
	lastMode = mode
	released = not trapped


func _process(delta):
	Pacman_controls()
	Ghost_process(delta)

	if pause or get_node('/root/Game/Menu').visible:
		if name == 'Pacman' and mode == 'die':
			if frame == 19 and not get_node('/root/Game/Menu').visible and not killedPacman:
				# skift til menu
				killedPacman = true
				get_node('/root/Game/Menu').visible = true
				get_node('/root/Game/Menu').reset()
			setAnimation('die')
			playing = true
		else:
			playing = false
		return

	

	# Vælger den rigtige animation
	for key in directionVectors:
		if directionVectors[key] == currentVectorDirection:
			if isGhost and mode in 'frightened die':
				setAnimation(mode)
			else:
				setAnimation(key)


	if moveDistance <= 0:
		if not triggedMVD_zeroEvent:
			triggedMVD_zeroEvent = true
			# Først og fremmest skal denne event kun affyres en gang.
			if moveDistance < 0:
				moveDistance = 0 # Derfor sættes denne til nul.
			movementSpeed = defaultMovementSpeed # Nulstiller farten

			# Spøgelserne skal have en chance for at vælge en ny retning
			Ghost_ChooseTile()


			# Derefter retter vi positionen, hvis vi altså får lov...
			if allowCorrections and moveDistanceMode == 'long' and (isGhost or (mode != 'die' and not isGhost)):
				position = getPositionFromTile(getTileFromPosition())


			# Ændre moveDistanceMode fra short til long, hvis altså den ikke allerede er blevet justeret på.
			if alignmentInfo.needIt:
				if nextDirection != '':
					if alignmentInfo.stack == alignmentInfo.max:
						alignmentInfo.needIt = false
						alignmentInfo.stack = 0

						moveDistanceMode = 'long'
					else:
						alignmentInfo.stack += 1

		# Nu skal der vælges ny retning
		var possibleDirections = getDirections()

		if nextDirection in possibleDirections or ignoreCollisionsMomentarily:
			ignoreCollisionsMomentarily = false
			currentVectorDirection = directionVectors[nextDirection]
			setMoveDistance()
		else:
			for dir in directionVectors:
				if currentVectorDirection == directionVectors[dir]:
					# Forsæt bevægelsen
					if dir in possibleDirections:
						setMoveDistance()

		if moveDistance != 0 and nextDirection != '':
			lastDirection = nextDirection
			

	else:
		triggedMVD_zeroEvent = false

		
		#? Forsæt med at gå fremad
		var lastPosition = position

		# Opdatere moveDistance, så vi ved hvor meget den mangler at bevæge sig.
		moveDistance -= abs(currentVectorDirection.length() * movementSpeed * delta)
		
		# Opdatere positionen
		if ((!isGhost and mode != 'die') or isGhost):
			position += currentVectorDirection * movementSpeed * delta

		# Hvis den stod stille, bliver animationen ikke afspillet
		if (isGhost or (not isGhost and mode != 'die')):
			playing = lastPosition != position







func Pacman_controls():
	if isGhost: return

	# Mulighed for at vælge / ønske en ny retning
	for direction in directionVectors:
		if Input.is_action_just_pressed('ui_%s' % direction):
			# Laver et ønske om den næste retning.
			nextDirection = direction

			# Hvis Pacman står stille sætter vi ham bare i gang
			if moveDistance == 0:
				if direction in getDirections():
					triggerMVD_zeroEvent()

			# Hvis den omvendte retning ønskes og den er i bevægelse
			if currentVectorDirection == -directionVectors[nextDirection] and moveDistance > 0:
				setMoveDistance(-2)
				currentVectorDirection = directionVectors[nextDirection]


	# Indsamling af point
	var PointMap = get_node_or_null('/root/Game/PointMap')
	if PointMap:
		var pos = getTileFromPosition()
		var cell = PointMap.get_cellv(pos)

		if cell == 12 or cell == 15:
			movementSpeed = defaultMovementSpeed / 1.4
			PointMap.set_cellv(pos, -2)
			if cell == 15:
				Game.addPoint('powerup')
			else:
				Game.addPoint()



func Ghost_process(_delta):
	if !isGhost: return

	if mode == 'die':
		movementSpeed = defaultMovementSpeed * 4

	# Når den skifter fra en 'mode' til en andnen
	if mode != lastMode:
		if mode in 'chase scatter' and lastMode in 'chase scatter':
			nextDirection = getReverseDirection(lastDirection)
			lastDirection = getReverseDirection(lastDirection)
			currentVectorDirection = directionVectors[nextDirection]
			setMoveDistance(-2) # Sørger for at vende move distance

		lastMode = mode
	
	if not trapped and not hasMadeSwitch:
		switchToChaseTimer -= _delta
		if switchToChaseTimer <= 0:
			hasMadeSwitch = true
			if mode == 'scatter':
				mode = 'chase'
	
	var Pacman = get_node_or_null("/root/Game/Pacman")
	if getTileFromPosition(Pacman.position) == getTileFromPosition():
		# Kollision med Pacman
		if mode == 'frightened':
			# Dead
			mode = 'die'
			Game.addPoint('ghost')
		elif mode != 'die':
			Pacman.mode = 'die'
			Game.pause()

	if Input.is_action_just_pressed('ui_accept'):
		mode = 'chase'

	if Input.is_action_just_pressed('ui_cancel'):
		mode = 'scatter'


var deb = true


func Ghost_ChooseTile():
	if !isGhost: return

	var currentPosition = getTileFromPosition()

	if trapped:
		allowCorrections = false
		alignmentInfo.stack = 0
		# op og ned
		if currentPosition.y == 16:
			if deb:
				deb = false
				setMoveDistance(2.5)
			else:
				position = getPositionFromTile(Vector2(13.5, 16))
				nextDirection = 'down'
				ignoreCollisionsMomentarily = true
				setMoveDistance(16)
				moveDistanceMode = 'short'
				trapped = false
				alignmentInfo.needIt = true
				alignmentInfo.stack = 0
				alignmentInfo.max = 2
		
		
		else:
			if nextDirection == '':
				if name == 'Inky':
					nextDirection = 'down'
				else: 
					nextDirection = 'up'
			else:
				if currentPosition.y == 18:
					nextDirection = 'down'
				if currentPosition.y == 20:
					nextDirection = 'up'
					position = getPositionFromTile(Vector2(currentPosition.x - 0.5, 19.5))
			
		return
	else:
		# Tjekker hvorvidt spøgelset er i huset...
		
		if currentPosition.x >= 11 and currentPosition.x <= 16 and currentPosition.y >= 18 and currentPosition.y <= 20:
			if currentPosition.y != 20:
				nextDirection = 'down'
				alignmentInfo.stack = 0
			else:
				alignmentInfo.stack = 0
				# Nu er den i bunden
				# Den kan altså være tre steder...
				if currentPosition.x == 12:
					setMoveDistance(1)
					nextDirection = 'right'
				elif currentPosition.x == 14 and currentPosition.y == 20:
					position = getPositionFromTile(Vector2(13.5, 19.5))
					setMoveDistance(28, true)
					nextDirection = 'up'

					if mode == 'die':
						mode = 'chase'
				elif currentPosition.x == 16:
					setMoveDistance(16)
					nextDirection = 'left'

			return

	var Pacman = get_node_or_null("/root/Game/Pacman")
	var Target = getTileFromPosition(Pacman.position)

	var Homes = { 'Blinky': Vector2(26, -2), 'Pinky': Vector2(0, -2), 'Inky': Vector2(26, 37), 'Clyde': Vector2(0, 37) }

	if mode == 'chase':
		if use_aStar:
			allowCorrections = true
			AStarChooseTile()
			return
		else:
			if name == 'Pinky':
				Target += Pacman.currentVectorDirection * 4
			elif name == 'Inky':
				Target += Pacman.currentVectorDirection * 2
				var Blinky = get_node_or_null('/root/Game/Blinky')
				
				var Bgt = getTileFromPosition(Blinky.position)
				var vectorBetweenPacman_and_Blinky = Bgt - Target
				var vNormal = vectorBetweenPacman_and_Blinky.normalized()
				Target = Target + vNormal * vectorBetweenPacman_and_Blinky.length()

			elif name == 'Clyde':
				var distanceFromClyde_vector2 = getTileFromPosition() - Target
				if distanceFromClyde_vector2.length() <= 8:
					Target = Homes['Clyde']
	
	elif mode == 'scatter':
		Target = Homes[name]
	elif mode == 'frightened':
		# Vælg en tilfældig retning
		var possibleDirections = getDirections()
		if getReverseDirection(lastDirection) in possibleDirections:
			var indexOfOppositeDirection = possibleDirections.find(getReverseDirection(lastDirection))
			possibleDirections.remove(indexOfOppositeDirection)

		var randomNumber = rand_range(0, possibleDirections.size())

		nextDirection = possibleDirections[randomNumber]
		return
	elif mode == 'die':
		Target = Vector2(13.5, 16)
		
		if currentPosition.y == 16:
			if currentPosition.x >= 13 and currentPosition.x <= 14:
				trapped = true
				Ghost_ChooseTile()
				return


	var currentRecord = 0
	var currentDirection = ''


	for direction in getDirections():
		if direction == getReverseDirection(lastDirection):
			continue

		var futurePosition = getTileFromPosition() + directionVectors[direction]
		var distance = abs( (futurePosition - Target).length() )
		if currentDirection == '' or distance < currentRecord:
			currentRecord = distance
			currentDirection = direction

	nextDirection = currentDirection
	# Hvis den er nået hertil må den gerne korrektere positionen :)
	allowCorrections = true

func drawPaths(OPEN, CLOSED):
	for x in range(0, 40):
		for y in range(0, 40):
			PathMap.set_cellv(Vector2(x, y), -1)

	for x in OPEN:
		PathMap.set_cellv(x.position, 1)

	for x in CLOSED:
		PathMap.set_cellv(x.position, 0)



func AStarChooseTile():
	var posDirs_equal2 = getDirections().size() == 2
	var nxtDirIsInPosDirs = nextDirection in getDirections()

	if posDirs_equal2 and nxtDirIsInPosDirs and currentVectorDirection != Vector2():
		return

	var lastDirection = nextDirection
	nextDirection = ''
	currentVectorDirection = Vector2()

	if getDirections().size() == 2 and currentVectorDirection != Vector2(): return

	

	var Pacman = get_node('/root/Game/Pacman')
	var PacmanPos = getTileFromPosition(Pacman.position)

	

	var OPEN = []
	var CLOSED = []
	var currentNode = false

	OPEN.append( newAstarNode( getTileFromPosition() ) )

	var index = 0
	while true:
		index += 1
		#if index > 10: break

		# finder node med den laveste f_cost
		currentNode = false
		var currentNodeIndex = 0

		var _index = 0
		for node in OPEN:
			if not currentNode or node.f_cost < currentNode.f_cost:
				currentNode = node
				currentNodeIndex = _index

			_index += 1

		# fjerner den valgte node fra OPEN og tilføjer den i CLOSED
		OPEN.remove(currentNodeIndex)
		CLOSED.append(currentNode)


		# Så er Pacman fundet og vi kan slappe helt af :)
		if currentNode.position == PacmanPos:
			break


		for direction in getDirections(currentNode.position - getTileFromPosition()):
			if index == 1:
				# hvis retningen er lig den retning spøgelset kom fra
				if direction == getReverseDirection(lastDirection):
					continue


			var newPosition = currentNode.position + directionVectors[direction]

			var neighbourIsClosed = false
			var neighbourIsOpen = false
			var neighbourNode = false

			for closedNode in CLOSED:
				if closedNode.position == newPosition:
					neighbourIsClosed = true
					neighbourNode = closedNode

			for openNode in OPEN:
				if openNode.position == newPosition:
					neighbourIsOpen = true


			if neighbourIsClosed: continue

			var newPath_isShorter = false
			if neighbourNode:
				if currentNode.pathLength + 8 < neighbourNode.pathLength:
					newPath_isShorter = true

			if newPath_isShorter or not neighbourIsOpen:

				# set f_cost of neighbour
				# set parent of neighbour to current
				if neighbourNode:
					var g_cost = abs( (newPosition - currentNode.position).length() ) + currentNode.g_cost
					var h_cost = abs( (PacmanPos - newPosition).length() )
					
					neighbourNode.parent = currentNode
					neighbourNode.f_cost = g_cost + h_cost
					neighbourNode.pathLength = currentNode.pathLength + 8

				if not neighbourIsOpen:
					OPEN.append(newAstarNode(newPosition, currentNode))
			


	# færdig
	
	if show_route:
		drawPaths(OPEN, CLOSED)


	var pathMap = get_node('/root/Game/PathMap')
	var __index = 0
	while true:

		if show_route:
			pathMap.set_cellv(currentNode.position, 2)

		if currentNode.parent.parent.parent:
			currentNode = currentNode.parent
		else:

			currentVectorDirection = currentNode.position - currentNode.parent.position
			for dir in directionVectors:
				if directionVectors[dir] == currentVectorDirection:
					nextDirection = dir
			break

		


func newAstarNode(tile_position, lastNode=false):
	var Pacman = get_node('/root/Game/Pacman')

	if not lastNode: lastNode = {
		'position': tile_position,
		'g_cost': 0,
		'parent': false,
		'pathLength': 0
	}

	# g_cost = længden fra node til start
	var g_cost = abs( (tile_position - lastNode.position).length() ) + lastNode.g_cost
	# h_cost = længden fra node til slut
	var h_cost = abs( (getTileFromPosition(Pacman.position) - tile_position).length() )

	return {
		'position': tile_position,
		'g_cost': g_cost,
		'h_cost': h_cost,
		'f_cost': g_cost + h_cost,
		'parent': lastNode,
		'pathLength': lastNode.pathLength + 8
	}



func triggerMVD_zeroEvent():
	triggedMVD_zeroEvent = false
	moveDistance = -1



func getDirections(offset=Vector2()):
	var validDirections = []

	for direction in directionVectors:
		var cell = Map.get_cellv(getTileFromPosition(position + offset*8) + directionVectors[direction])


		if cell == -1:
			validDirections.append(direction)

	return validDirections


func getDirectionsFromPos(pos=position):
	var validDirections = []

	for direction in directionVectors:
		var cell = Map.get_cellv(getTileFromPosition(pos) + directionVectors[direction])


		if cell == -1:
			validDirections.append(direction)

	return validDirections




func getPositionFromTile(vector):
	return Vector2( 8*(vector.x+.5), 8*(vector.y-1.5) )


func getTileFromPosition(pos=position): # Tager objektets egen position som udgangspunkt
	return Vector2( floor(pos.x / 8), floor(pos.y / 8)+2 )


func getReverseDirection(direction):
	if direction == 'up': return 'down'
	if direction == 'down': return 'up'
	if direction == 'right': return 'left'
	if direction == 'left': return 'right'

	return direction



func setMoveDistance(value=-1, override=false):
	# -1, så vælger den selv
	# -2, vender den moveDistance om afhængig af mode'en

	var oldMVD = moveDistance
	var fVal = value

	if value < 0:
		if moveDistanceMode == 'precise':
			value = 1
		elif moveDistanceMode == 'short':
			value = 4
		else:
			value = 8

	if fVal == -2:
		moveDistance = 0
		value = value - oldMVD

	if moveDistance == 0 or override:
		moveDistance = value


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
