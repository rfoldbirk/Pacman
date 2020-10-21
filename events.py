# Bare nogle kedelige lokale variabler
enemyNames = 'blinky - pinky - inky - clyde'
enemyHomes = { 'blinky': [16, 18], 'pinky': [0, 18], 'inky': [16, 0], 'clyde': [0, 0] }



class EventSystem:
	def __init__(self, copy_of_entities):
		self.Entities = copy_of_entities
		self.events = ['/st1 open 0 0/t5', 'open 1 1/t5', 'open 2 2/t5', 'open 3 3/t5']
		self.eventClock = 0



	def update(self, dt):
		if len(self.events) == 0: return # Returnerer hvis der ikke er noget events

		if self.eventClock <= 0:
			EV = self.events[0]
			
			# Fjern den ekstra tid fra, og prøv igen
			if '/st' in EV:
				startTime = extract(EV, '/st', 1)
				if startTime > 0: # Sætter tiden
					self.eventClock = startTime

					EVarr = EV.split(' ') # Fjerner alt
					EVarr.pop(0)		  # til og med det
					EV = arrToStr(EVarr)  # første mellemrum

					self.events.pop(0)
					self.events.insert(0, EV) 
					return
			else:
				# Udførelse af handling, og så fjerner jeg den
				print('')
				self.executeEvent()
				self.events.pop(0)

		else:
			self.eventClock -= dt # Nedtælling





	def executeEvent(self):
		EV = self.events[0]
		print(EV)

		if '/t' in EV:
			setTime = extract(EV, '/t', 1)
			self.eventClock = setTime


		if 'open' in EV:
			strSpace = EV.split('open')[1]
			startPos = extract(strSpace, ' ', 1)
			endPos = extract(strSpace, ' ', 2)

			if type(startPos) == int or type(endPos) == int:
				i = 0
				for E in self.Entities:
					if hasattr(E, 'name'):
						if E.name in enemyNames:
							if i >= startPos and i <= endPos:
								E.enemy_setTarget( enemyHomes[E.name][0], enemyHomes[E.name][1] )
								E.goThroughDoor = True

							i += 1




def arrToStr(arr, inBetween=' '):
	string = ''
	for elem in arr:
		string += elem + inBetween

	return string



def extract(str, pattern, index, convertToInt=True):
	str0 = 0
	str0 = str.split(pattern)[index].split(' ')[0].split('/')[0]

	if convertToInt:
		return int(str0)
	else:
		return str0