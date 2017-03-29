from sense_hat import SenseHat

sense = SenseHat()

RED = [255,0,0]#Red         Objective Tunnels
BLUE = [0,0,255]#Blue       DeadEnds
GREEN = [0,255,0]#Green		Insulation
YELLOW = [255,255,0]#		Ready Light
EMPTY = [0,0,0]#Empty

def lightmatrix_A7_yellow():
	sense.set_rotation(270)
	sense.set_pixel(0,0,YELLOW)

def lightmatrix_no_color():
	sense.show_letter(' ', text_colour = [0,0,0], back_colour = EMPTY)
	return

def lightmatrix_yellow_ready():
	sense.show_letter(' ', text_colour = [0,0,0], back_colour = YELLOW)
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
	block_identity = block_score.index(max(block_score))
	#The x and y were exchnage explicitly
	if(block_identity == 0):
		sense.set_pixel(y,x,RED)
	if(block_identity == 1):
		sense.set_pixel(y,x,BLUE)
	if(block_identity == 2):
		sense.set_pixel(y,x,GREEN)
	return

