extends Line2D


onready var Raycast = get_parent().get_node("Raycast")

func _ready():
	pass


func _process(delta):
	position = Raycast.position
	rotation = Raycast.rotation
	
