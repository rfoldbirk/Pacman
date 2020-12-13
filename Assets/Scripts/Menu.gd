extends Control


onready var game = get_node('/root/Game')
onready var menu = get_node('/root/Game/Menu')
onready var title = get_node('/root/Game/Menu/Title')
onready var btns = get_node('/root/Game/Menu/Buttons')


onready var Menu = {
	'_current': 'Main',
	'_index': 0,
	
	'_vars': {
		'A*': false,
		'SR': false
	},
	
	'Main': [ 'Play', 'Settings', 'Quit' ],
	'Settings': [ 'Use A*: ${A*}', 'Show Route: ${SR}', 'Back' ]
}

func _ready():
	setText()
	

func _process(delta):
	var forceUpdate = false
	var lastIndex = Menu._index
	var lastCurrent = Menu._current
	
	if Input.is_action_just_pressed("ui_down"):
		Menu._index += 1

	if Input.is_action_just_pressed("ui_up"):
		Menu._index -= 1
		
		
	if Input.is_action_just_pressed("ui_accept"):
		var item = Menu[Menu._current][Menu._index]
		
		if Menu._current == 'Main':
			if item == 'Quit':
				get_tree().quit()
			elif item == 'Play' and menu.visible:
				game.spawn(true)
				menu.visible = false
			elif item == 'Settings':
				Menu._current = item

		# Indstillinger
		if Menu._current == 'Settings':
			forceUpdate = true
			if item == 'Use A*: ${A*}':
				Menu._vars['A*'] = not Menu._vars['A*']
					
			elif item == 'Show Route: ${SR}':
				Menu._vars['SR'] = not Menu._vars['SR']
				
			elif item == 'Back':
				Menu._current = 'Main'
		
		
	if lastCurrent != Menu._current:
		Menu._index = 0
	
	if lastIndex != Menu._index or forceUpdate: 
		if Menu._index > Menu[Menu._current].size() -1 or Menu._index < 0:
			Menu._index = lastIndex
			
		setText()
	
	
	

func reset():
	Menu._current = 'Main'
	Menu._index = 0

	setText()

	
func setText():
	btns.text = ''
	
	var currentMenu = Menu[Menu._current]
	var selectedItem = currentMenu[Menu._index]
	
	var z = 0
	for i in currentMenu:
		var item = currentMenu[z]
		if item == selectedItem: item = '[   ' + item + '   ]'
		
		if '${' in item:
			var varName = item.split('${')[1].split('}')[0]
			var varProperty = Menu._vars[varName]
			item = item.replace('${' + varName + '}', String(varProperty))
		
		btns.text += item + '\n\n\n'
		
		z += 1
