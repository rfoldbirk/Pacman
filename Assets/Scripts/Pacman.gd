extends AnimatedSprite

onready var speed = 20
onready var dir = Vector2(-1, 0)


func _ready():
	# x: 112, y: 164
	position.x = 8*14
	position.y = 8*20 + 4


func _process(delta):
	var pos = getTile()
	
	# Opdater position
	position += dir * speed * delta
	
	


func getTile():
	return Vector2( floor(position.x / 8), floor(position.y/8) )
