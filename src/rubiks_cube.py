import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class rubiks_cube:
	# Init
	def __init__(self):
		self.faceslist = ('top', 'bottom', 'front', 'right', 'left', 'back')
		# From now, top is face 0, bottom is face 1 and so on
		# DO NOT CHANGE THE ORDER OF FACESLIST, CODE MAY BREAK

		self.facecolor = {'top' : 'white',
							'front': 'green',
							'bottom': 'blue',
							'right': 'red',
							'left': 'orange',
							'back': 'yellow'}

		self.ordering = {'top':('back', 'right', 'front', 'left'),
					'bottom':('front', 'right', 'left', 'back'),
					'front':('top', 'right', 'bottom', 'left'),
					'right':('top', 'back', 'bottom', 'front'),
					'left':('top', 'front', 'bottom', 'back'),
					'back':('top', 'left', 'bottom', 'right')}

		# Following is the exposure of different faces' cells to other faces
		# With front looking towards you, the lateral faces look as follows
		# 6, 7, 8
		# 3, 4, 5
		# 0, 1, 2
		# if any lateral face is looking towards you, it will seem the same
		#
		# With top looking towards you and front at the bottom, the top face looks like above
		# With bottom looking towards you and back at the bottom the bottom face looks like above
		#
		# Below are cell exposure of adjecent faces in clockwise direction starting from
		# face's top left.
		self.faceneighbors = {'top': [8, 7, 6, 8, 7, 6, 8, 7, 6, 8, 7, 6],
							'bottom': [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
							'front': [0, 1, 2, 6, 3, 0, 8, 7, 6, 2, 5, 8],
							'right': [2, 5, 8, 6, 3, 0, 2, 5, 8, 2, 5, 8],
							'left': [6, 3, 0, 6, 3, 0, 6, 3, 0, 0, 3, 6],
							'back': [8, 7, 6, 6, 3, 0, 2, 1, 0, 2, 5, 8]}

		self.stickersize = 1
		self.inmargin = 0.1

		self.facetemplate = []
		for i in range(6):
			for j in range(6):
				cur_x = (i+1)//2*(self.stickersize)
				cur_y = (j+1)//2*(self.stickersize)
				if i%2 == 0:
					cur_x += self.inmargin
				else:
					cur_x -= self.inmargin
				if j%2 == 0:
					cur_y += self.inmargin
				else:
					cur_y -= self.inmargin
				# print("{} - {} - {} {}".format(i, j, cur_x, cur_y))
				self.facetemplate.append((cur_x, cur_y))
		# print(self.face)

		# Assume that the cube is made up of 36 points (4 points per sticker)
		# 0 is the bottome left point, 35 is the top right point
		# The point looks as follows:
		#
		# 30  31  32  33  34  35
		# 24  25  26  27  28  29
		# ...
		# ...
		# ...
		# 0   1   2   3   4   5
		frontface = []
		rightface = []
		leftface = []
		backface = []
		topface = []
		bottomface = []
		for point in self.facetemplate:
			frontface.append((point[0], point[1], -self.inmargin))
			backface.append((point[0], point[1], - self.stickersize*3 - self.inmargin))
			rightface.append((self.stickersize*3 + self.inmargin, point[0], -point[1]))
			leftface.append((-self.inmargin, point[0], -point[1]))
			topface.append((point[0], self.stickersize*3 + self.inmargin, -point[1]))
			bottomface.append((point[0], -self.inmargin, -point[1]))
		# Alert: self.facepoints is depended on self.faceslist config
		self.facepoints = [topface, bottomface, frontface, rightface, leftface, backface]

		self.surfaceperface = (
								(0, 1, 7, 6),
								# (2, 3, 9, 8),
								# (4, 5, 11, 10),
								# (12, 13, 19, 18),
								# (14, 15, 21, 20),
								# (16, 17, 23, 22),
								# (24, 25, 31, 30),
								# (26, 27, 33, 32),
								# (28, 29, 35, 34)
								)

		# We call all those faces active which look towards the camera
		colorloss = 0.45 
		self.colors = {'active':
							{'red': (1, 0, 0),
							'blue': (0, 0, 1),
							'green': (0, 1, 0),
							'white': (1, 1, 1),
							'orange': (1, 0.647, 0),
							'yellow': (0, 1, 1)},
						'inactive':
							{'red': (1 - colorloss, 0, 0),
							'blue': (0, 0, 1 - colorloss),
							'green': (0, 1 - colorloss, 0),
							'white': (1 - colorloss, 1 - colorloss, 1 - colorloss),
							'orange': (1 - colorloss, 0.647 - colorloss*0.647, 0),
							'yellow': (0, 1 - colorloss, 1 - colorloss)}
						}
		self.cubeconfig = []
		for face in self.faceslist:
			# CubeFace is a 9 element list containing color from bottom left to top right
			# 6 7 8
			# 3 4 5
			# 0 1 2
			cubeface = []
			for x in range(9):
				cubeface.append(self.facecolor[face])
			self.cubeconfig.append(cubeface)
	
	def displaycube(self):
		glBegin(GL_QUADS)
		activityflag = [1, 0, 1, 0, 1, 0]

		# First render the inactive faces
		for x in range(6):
			if activityflag[x] == 0:
				y = 0
				for surface in self.surfaceperface:
					for point in surface:
						glColor3fv(self.colors['inactive'][self.cubeconfig[x][y]])
						glVertex3fv(self.facepoints[x][point])
				y += 1
		# Second, render the active faces
		for x in range(6):
			if activityflag[x] == 1:
				y = 0
				for surface in self.surfaceperface:
					for point in surface:
						glColor3fv(self.colors['active'][self.cubeconfig[x][y]])
						glVertex3fv(self.facepoints[x][point])
				y += 1

		glEnd()

	# Moves that cube can take
	# move_xxy means to rotate face x once in direction of y
	# e.g. move_toc means rotate topface once in clockwise direction
	def move_toc(self):
		self.rotateronface('top', 2)
		self.rotateraroundface('top', 3)
	def move_toa(self):
		rotateronface('top', -2)
		rotateraroundface('top', -3)
		updatedisplay()
	def move_boc(self):
		rotateronface('bottom', 2)
		rotateraroundface('bottom', 3)
		updatedisplay()
	def move_boa(self):
		rotateronface('bottom', -2)
		rotateraroundface('bottom', -3)
		updatedisplay()
	def move_lec(self):
		rotateronface('left', 2)
		rotateraroundface('left', 3)
		updatedisplay()
	def move_lea(self):
		rotateronface('left', -2)
		rotateraroundface('left', -3)
		updatedisplay()
	def move_ric(self):
		rotateronface('right', 2)
		rotateraroundface('right', 3)
		updatedisplay()
	def move_ria(self):
		rotateronface('right', -2)
		rotateraroundface('right', -3)
		updatedisplay()
	def move_bac(self):
		rotateronface('back', 2)
		rotateraroundface('back', 3)
		updatedisplay()
	def move_baa(self):
		rotateronface('back', -2)
		rotateraroundface('back', -3)
		updatedisplay()

	def rotateronface(self, face, offset):
		c = self.cubeconfig[self.faceslist.index(face)]
		rimpoints = [0, 1, 2, 5, 8, 7, 6, 3]
		buf = [c[x] for x in rimpoints]
		rotatedbuf = [buf[(x + offset)%8] for x in range(8)]
		x = 0
		for y in rimpoints:
			c[y] = rotatedbuf[x]
			x += 1
		self.cubeconfig[self.faceslist.index(face)] = c

	def rotateraroundface(self, face, offset):
		fourfaces = self.ordering[face]
		buf = []
		c = self.faceneighbors[face]
		buf = [fourfaces[x//3][c[x]] for x in range(9)]
		rotatedbuf = [buf[(x + offset)%9] for x in range(9)]
		for x in range(9):
			fourfaces[x//3][c[x]] = rotatedbuf[x]


if __name__ == '__main__':
	pygame.init()
	display = (800,600)
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
	gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
	glTranslatef(-1.5, -1.5, -10)
	glRotatef(45, 2, 1, 0)

	rb = rubiks_cube()
	# rb.move_toc();
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		# glRotatef(1, 3, 1, 1) # Rotation matrix
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) # Clearing function
		rb.displaycube()
		pygame.display.flip() #updates display
		pygame.time.wait(10) 

	# Debug code
	print(rb.frontface)