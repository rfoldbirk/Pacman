# Bare nogle kedelige lokale variabler
enemyNames = 'blinky - pinky - inky - clyde'
enemyHomes = { 'blinky': [16, 20], 'pinky': [0, 20], 'inky': [16, 0], 'clyde': [0, 0] }

delays = {
	"instant": 0.1,
	"slow": 1000,
	"od": 100, # open delay
	"smd": 0.1  # start moving delay
}


class EventSystem:
	def __init__(self, copy_of_entities):
		self.Entities = copy_of_entities
		self.events = [] #['/stsmd startMoving 0 /r 4', '/stod scatter 0 /r 4']
		self.eventClock = 0
		self.latestEvent = ''



	def update(self, dt):
		
		if len(self.events) == 0: return # Returnerer hvis der ikke er noget events

		if self.eventClock <= 0:
			EV = self.events[0]

			print(EV)

			# Fjern den ekstra tid fra, og prøv igen
			if '/st' in EV:
				self.latestEvent = EV
				startTime = extract(EV, '/st', 1, convertToInt=False)

				try:
					startTime = int(startTime)
				except:
					startTime = delays[startTime]


				if startTime > 0: # Sætter tiden
					self.eventClock = startTime

					EVarr = EV.split(' ') # Fjerner alt
					EVarr.pop(0)		  # til og med det
					EV = arrToStr(EVarr)  # første mellemrum

					print(EV)

					self.events.pop(0)
					self.events.insert(0, EV) 
					return
			else:
				# Udførelse af handling, og så fjerner jeg den
				EV = self.events[0]
				print('no time:', EV)
				self.events.pop(0)
				self.executeEvent(EV)

		else:
			self.eventClock -= 10*dt # Nedtælling





	def executeEvent(self, EV):
		print('Executing Event:', EV)

		value = 0

		if '/t' in EV:
			value = extract(EV, '/t', 1)
			self.eventClock = value

		if 'startMoving' in EV:
			value = extractAfter(EV, 'startMoving')

			def _callback(E):
				E._move()

			self.getGhosts(value, callback=_callback)



		if 'open' in EV:
			value = extractAfter(EV, 'open')

			def _callback(E):
				E.setEnemyTarget( enemyHomes[E.name][0], enemyHomes[E.name][1] )
				E.goThroughDoor = True

			self.getGhosts(value, callback=_callback)


		if 'chase' in EV:
			def _callback(E):
				E.mode = 'chase'

			self.getGhosts(0, 3, _callback)

		
		if 'setMode' in EV:
			mode = extractAfter(EV, 'setMode')

			print('Got mode:', mode)

			def _callback(E):
				E.setMode(mode)

			self.getGhosts(0, 3, callback=_callback)


		if '/r' in EV:
			repeat = extractAfter(EV, '/r')
			if repeat <= 1: return

			newEvent = ''
			for x in self.latestEvent:
				try:
					if '/r' in newEvent:
						break

					if int(x) == value:
						newEvent += str(int(x) + 1)
				except:
					newEvent += x
				

			newEvent += ' ' + str(repeat-1)
			self.events.insert(0, newEvent)




	def getGhosts(self, start, end=None, callback=None):
		if end == None: end = start

		if type(start) == int or type(end) == int:
			i = 0
			for E in self.Entities:
				if hasattr(E, 'name'):
					if E.name in enemyNames:
						if i >= start and i <= end:
							if callback != None:
								callback(E)

						i += 1



def arrToStr(arr, inBetween=' '):
	string = ''
	for elem in arr:
		string += elem + inBetween

	return string


def extractAfter(EV, str, amount=1):
	strSpace = EV.split(str)[1]
	values = []
	for i in range(0, amount):
		values.append(extract(strSpace, ' ', i+1))

	if values == []:
		return False
	elif len(values) == 1:
		return values[0]
	
	return values

def extract(str, pattern, index, convertToInt=True):
	str0 = 0
	str0 = str.split(pattern)[index].split(' ')[0].split('/')[0]

	if convertToInt:
		return int(str0)
	else:
		return str0