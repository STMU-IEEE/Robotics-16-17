from sense_hat import SenseHat

sense = SenseHat()

R = [255,0,0]#Red         Objective Tunnels
M = [255,0,255]#Magenta
B = [0,0,255]#Blue       DeadEnds
C = [0,255,255]#Cyan
G = [0,255,0]#Green		Insulation
Y = [255,255,0]#		Ready Light
E = [0,0,0]#Empty

def lightmatrix_debug(x):
	if x%5 == 0:
		color = R
	elif x%5 == 1:
		color = M
	elif x%5 == 2:
		color = B
	elif x%5 == 3:
		color = C
	elif x%5 == 4:
		color = G
	sense.clear(color)


def lightmatrix_A7_yellow():
	sense.set_rotation(270)
	sense.set_pixel(0,0,Y)

def lightmatrix_yellow():
	# sense.set_rotation(270)
	sense.clear(Y)

def lightmatrix_no_color():
	sense.clear()
	return

def lightmatrix_yellow_ready():
	sense.show_letter(' ', text_colour = [0,0,0], back_colour = Y)
	return

def lightmatrix_update(x,y,block_score):
	total = 0
	print(block_score)
	for z in range(3):
		total += block_score[z]

	tunnel_intensity = round(block_score[0] / total * 255)
	dead_intensity = round(block_score[1] / total * 255)
	insulation_intensity = round(block_score[2] / total * 255)
	#The x and y were exhange explicitly
	sense.set_pixel(y,x, [tunnel_intensity, insulation_intensity, dead_intensity])
	return

def lightmatrix_update_simple(x,y,block_score):
	block_identity = block_score
	#The x and y were exchnage explicitly
	if(block_identity == 0):
		sense.set_pixel(y,x,R)
	if(block_identity == 1):
		sense.set_pixel(y,x,B)
	if(block_identity == 2):
		sense.set_pixel(y,x,G)
	return
