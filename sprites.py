# Sprite classes for Bernie Jump 
# All sprites are my own - should be obvious by how bad they are lol 
# Code adapted from platformer series by KidsCanCode on YouTube
# Additional features I added: 
#  - Increasing difficulty 
#  - New powerups 
#  - my own sprites and game design 
#  - Soundclips for Bernie and Trump 
#  - Changed the functionality of the platforms 

 
from settings import *
import pygame as pg
from os import path
from random import choice, randrange
import time

# pre-assign vector function to vec 
vec = pg.math.Vector2

# load images 
img_dir = path.join(path.dirname(__file__), 'img')

class Spritesheet:
	# utility class for loading and parsing spritesheets
	def __init__(self, filename):
		self.spritesheet = pg.image.load(filename).convert()

	def get_image(self, x, y, width, height):
		# grab an image out of a larger spritesheet
		image = pg.Surface((width, height))
		image.blit(self.spritesheet, (0, 0), (x, y, width, height))
		image = pg.transform.scale(image, (width // 3, height // 3))
		return image

class Player(pg.sprite.Sprite):
	def __init__(self, game):
		self._layer = PLAYER_LAYER
		self.groups = game.all_sprites
		player_img = pg.image.load(path.join(img_dir, 'bernie_static.png')).convert()
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.jumping = False
		self.ducking = False
		self.image = pg.transform.scale(player_img, (100, 100))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = (40, HEIGHT - 100)
		self.pos = vec(40, HEIGHT - 100)
		self.vel = vec(0, 0)
		self.acc = vec(0, 0)

	def jump_cut(self):
		if self.jumping:
			if self.vel.y < -3:
				self.vel.y = -3

	def jump(self):
		# jump only if standing on a platform
		self.rect.y += 2
		hits = pg.sprite.spritecollide(self, self.game.platforms, False)
		self.rect.y -= 2
		if hits and not self.jumping:
			# self.game.jump_sound.play()
			self.jumping = True		
			self.vel.y = -PLAYER_JUMP

	def duck(self):
		self.pos.y -= 2
		hits = pg.sprite.spritecollide(self, self.game.platforms, False)
		if hits and not self.ducking:
			self.ducking = True

	def duck_cut(self):
		self.ducking = False

	def update(self): 
		self.animate()
		# apply gravity to y component of the vector
		self.acc = vec(0, PLAYER_GRAV)
		keys = pg.key.get_pressed()
		if keys[pg.K_LEFT]:
			self.acc.x = -PLAYER_ACC
		if keys[pg.K_RIGHT]:
			self.acc.x = PLAYER_ACC

		# apply friction	
		self.acc.x += self.vel.x * PLAYER_FRICTION
		# equations of motion
		self.vel += self.acc
		if abs(self.vel.x) < 0.1:
			self.vel.x = 0
		self.pos += self.vel + 0.5 * self.acc
		# wrap around the sides of the screen 
		if self.pos.x > WIDTH + self.rect.width / 2:
			self.pos.x = 0 - self.rect.width / 2
		if self.pos.x < 0 - self.rect.width / 2:
			self.pos.x = WIDTH + self.rect.width / 2

		self.rect.midbottom = self.pos

	def animate(self):
		now = pg.time.get_ticks()
		player_img = pg.image.load(path.join(img_dir, 'bernie_sanders1.png')).convert()
		player_jump_right_img = pg.image.load(path.join(img_dir, 'bernie_sanders2.png')).convert()
		player_jump_left_img = pg.image.load(path.join(img_dir, 'bernie_sanders3.png')).convert()
		player_duck_img = pg.image.load(path.join(img_dir, 'bernie_sanders4.png')).convert()
		if self.jumping and self.vel.x >= 0: 
			self.image = pg.transform.scale(player_jump_right_img, (80, 105))
			self.image.set_colorkey(BLACK)
		if self.jumping and self.vel.x < 0: 
			self.image = pg.transform.scale(player_jump_left_img, (80, 105))
			self.image.set_colorkey(BLACK)
		if self.ducking: 
			self.image = pg.transform.scale(player_duck_img, (80, 105))
			self.image.set_colorkey(BLACK)
		if not self.jumping and not self.ducking:
			self.image = pg.transform.scale(player_img, (80, 105))
			self.image.set_colorkey(BLACK)
		self.mask = pg.mask.from_surface(self.image)

class Platform(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self._layer = PLATFORM_LAYER
		self.groups = game.all_sprites, game.platforms
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		images = [self.game.spritesheet.get_image(0, 192, 380, 94), 
				 self.game.spritesheet.get_image(0, 96, 380, 94), 
				 self.game.spritesheet.get_image(382, 408, 200, 100), 
				 self.game.spritesheet.get_image(232, 1288, 200, 100)]
		self.image = choice(images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = x 
		self.rect.y = y
		if randrange(100) < POW_SPAWN_PCT:
			Pow(self.game, self)

	# def dist_between_plats(self):
	#	for plat in self.platforms:
	#		dist = self.rect.centerx - plat.rect.centerx



class Pow(pg.sprite.Sprite):
	def __init__(self, game, plat):
		self._layer = POW_LAYER
		self.groups = game.all_sprites, game.powerups
		pow_img = pg.image.load(path.join(img_dir, 'medkit2.png')).convert()
		educ_img = pg.image.load(path.join(img_dir, 'education.png')).convert()
		tax_img = pg.image.load(path.join(img_dir, 'tax.png')).convert()
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.plat = plat
		self.type = choice(['healthcare', 'education', 'tax'])
		if self.type == 'healthcare':
			self.image = pg.transform.scale(pow_img, (25, 20))
		elif self.type == 'education':
			self.image = pg.transform.scale(educ_img, (30, 30))
		else:
			self.image = pg.transform.scale(tax_img, (25, 25))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.centerx = self. plat.rect.centerx 
		self.rect.bottom = self.plat.rect.top - 5

	def update(self):
		self.rect.bottom = self.plat.rect.top - 5
		if not self.game.platforms.has(self.plat):
			self.kill()

class Mob(pg.sprite.Sprite):
	def __init__(self, game):
		self._layer = MOB_LAYER
		self.groups = game.all_sprites, game.mobs
		pow_img = pg.image.load(path.join(img_dir, 'medkit2.png')).convert()
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image_straight = pg.image.load(path.join(img_dir, 'Trump_right.png')).convert()
		self.image_straight.set_colorkey(BLACK)
		# self.image_straight = pg.transform.scale(self.image_straight, (80, 105))
		self.image_left = pg.image.load(path.join(img_dir, 'Trump_left.png')).convert()
		self.image_left.set_colorkey(BLACK)
		self.image = self.image_straight
		self.rect = self.image.get_rect()
		self.rect.centerx = choice([-100, WIDTH + 100])
		self.vx = randrange(1, 4)
		if self.rect.centerx > WIDTH:
			self.vx *= -1 
		self.rect.y = randrange(HEIGHT / 2)
		self.vy = 0
		self.dy = 0.5 

	def update(self):
		self.rect.x += self.vx 
		self.vy += self.dy 
		if self.vy > 3 or self.vy < - 3:
			self.dy *= -1
		center = self.rect.center 
		if self.vx < 0: 
			self.image = self.image_left
		else:
			self.image = self.image_straight 
		self.rect = self.image.get_rect()
		self.mask = pg.mask.from_surface(self.image)
		self.rect.center = center
		self.rect.y += self.vy 
		if self.rect.left > WIDTH + 100 or self.rect.right < -100:
			self.kill()



