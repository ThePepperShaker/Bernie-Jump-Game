# platform game 

# Art from Kenney.nl
# Bernie and Trump art from 'Super Smash Presidents Game - Open Source Game Project'
# Xeon theme https://opengameart.org/users/bart

import pygame as pg
import random 
from os import path
import time
import pygame.mask


# SETTINGS 

# Game options and settings 

# screen settings
TITLE = 'Bernie Jump'
WIDTH = 480
HEIGHT = 600 
FPS = 60
FONT_NAME = 'helvetica'
HS_FILE = 'img/highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'

# player properties 
PLAYER_ACC = 0.5 
PLAYER_FRICTION = -0.12 
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20 

# game properties 
BOOST_POWER = 60
POW_SPAWN_PCT = 7
MOB_SPAWN = 5000
PLAYER_LAYER = 2 
PLATFORM_LAYER = 1 
POW_LAYER = 1
MOB_LAYER = 2
BULLET_LAYER = 2

# starting platforms 
PLATFORM_LIST = [(0, HEIGHT - 60), 
				 (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50), 
				 (125, HEIGHT - 350), 
				 (350, 200), 
				 (175, 100)]

# define colors 
WHITE = (250, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (135, 206, 250)
BGCOLOR = LIGHTBLUE

# END OF SETTINGS 


# SPRITES 

# Sprite classes for Bernie on the run 
from random import choice, randrange

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
		player_img = pg.image.load(path.join(img_dir, 'bernie.png')).convert()
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.jumping = False
		self.image = pg.transform.scale(player_img, (60, 85))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = (40, HEIGHT - 100)
		self.pos = vec(40, HEIGHT - 100)
		self.vel = vec(0, 0)
		self.acc = vec(0, 0)


	def jump_cut(self):
		if self.jumping:
			if self.vel.y < -5:
				self.vel.y = -5

	def jump(self):
		# jump only if standing on a platform
		self.rect.x += 2
		hits = pg.sprite.spritecollide(self, self.game.platforms, False)
		self.rect.x -= 2
		if hits and not self.jumping:
			# self.game.jump_sound.play()
			self.jumping = True		
			self.vel.y = -PLAYER_JUMP

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
		self.pos += self.vel + 0.5 * self.acc
		# wrap around the sides of the screen 
		if self.pos.x > WIDTH:
			self.pos.x = 0
		if self.pos.x < 0:
			self.pos.x = WIDTH

		self.rect.midbottom = self.pos

	def animate(self):
		now = pg.time.get_ticks()
		player_img = pg.image.load(path.join(img_dir, 'bernie.png')).convert()
		player_jump_img = pg.image.load(path.join(img_dir, 'bernie_jump.png')).convert()
		if self.jumping: 
			self.image = pg.transform.scale(player_jump_img, (60, 85))
			self.image.set_colorkey(BLACK)
		if not self.jumping:
			self.image = pg.transform.scale(player_img, (60, 85))
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
		self.image_straight = pg.image.load(path.join(img_dir, 'trumpstraight.png')).convert()
		self.image_straight.set_colorkey(BLACK)
		self.image_right = pg.image.load(path.join(img_dir, 'trump2.png')).convert()
		self.image_right.set_colorkey(BLACK)
		self.image_left = pg.image.load(path.join(img_dir, 'trump.png')).convert()
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
		self.shoot_delay = 3000
		self.last_shot = pg.time.get_ticks()

	def shoot(self):
		now = pg.time.get_ticks()
		if now - self.last_shot > self.shoot_delay:
			self.last_shot = now 
			bullet = Bullet(self.rect.centerx, self.rect.top)
			all_sprites.add(bullet)
			#shoot_sound.play()

	def update(self):
		self.rect.x += self.vx 
		self.vy += self.dy 
		if self.vy > 3 or self.vy < - 3:
			self.dy *= -1
		center = self.rect.center 
		if self.vx > 0:
			self.image = self.image_right
		elif self.vx < 0: 
			self.image = self.image_left
		else:
			self.image = self.image_straight 
		self.rect = self.image.get_rect()
		self.mask = pg.mask.from_surface(self.image)
		self.rect.center = center
		self.rect.y += self.vy 
		if self.rect.left > WIDTH + 100 or self.rect.right < -100:
			self.kill()
		if self.rect.center == WIDTH /2:
			self.shoot()

class Bullet(pg.sprite.Sprite):
	def __init__(self, x, y):
		self._layer = BULLET_LAYER
		self.groups = game.all_sprites, game.bullets
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load(path.join(img_dir, 'bullet_img.png')).convert()
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = y 
		self.rect.centerx = x
		self.speedy = -10
	def update(self):
		self.rect.y += self.speedy 
		if self.rect.bottom < 0:
			self.kill()


# END OF SPRITES

class Game:
	def __init__(self):
		# initialize game window, etc 
		pg.init()
		pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH, HEIGHT))
		pg.display.set_caption('Bernie Jump')
		self.clock = pg.time.Clock()
		self.running = True
		self.font_name = pg.font.match_font(FONT_NAME)
		self.load_data()

	def load_data(self):
		# load high score 
		self.dir = path.dirname(__file__)
		img_dir = path.join(self.dir, 'img')
		with open(path.join(self.dir, HS_FILE), 'r+') as f:
			try:
				self.highscore = int(f.read())  
			except:
				self.highscore = 0
		# load spritesheet image 
		self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
		# load sounds 
		self.snd_dir = path.join(self.dir, 'sound')
		self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Huge.wav'))
		self.jump_sound.set_volume(0.2)
		# Healthcare is a right...
		self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'healthcare.wav'))
		self.boost_sound.set_volume(0.5)
		# Education related soundbit
		self.educ_sound = pg.mixer.Sound(path.join(self.snd_dir, 'tuitionfree.wav'))
		self.educ_sound.set_volume(0.5)
		# Raising taxes related soundbit
		self.tax_sound = pg.mixer.Sound(path.join(self.snd_dir, 'taxes.wav'))
		self.tax_sound.set_volume(0.5)
		# Enough is enough 
		self.die_sound = pg.mixer.Sound(path.join(self.snd_dir, 'enough.wav'))
		self.die_sound.set_volume(0.05)
		# Trump soundbit
		self.trumpcollide_sound = pg.mixer.Sound(path.join(self.snd_dir, 'CrazyBernie.wav'))
		self.trumpcollide_sound.set_volume(0.5)
 
	def new(self):
		# start a new game
		self.score = 0
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.platforms = pg.sprite.Group()
		self.powerups = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		self.player = Player(self)
		for plat in PLATFORM_LIST:
			Platform(self, *plat)
		self.mob_timer = 0
		self.plat_timer = 30000
		pg.mixer.music.load(path.join(self.snd_dir, 'xeon6.ogg'))
		pg.mixer.music.set_volume(0.2)
		self.run()

	def run(self):
		# game loop 
		pg.mixer.music.play(loops=-1)
		self.playing = True
		while self.playing:
			self.clock.tick(FPS)
			self.events()
			self.update()
			self.draw()
		pg.mixer.music.fadeout(500)

	def update(self):
		# game loop update
		self.all_sprites.update()

		# spawn a mob? 
		now = pg.time.get_ticks()
		if now - self.mob_timer > 5000 + random.choice([-1000, 500, 0, 500, 1000]):
			self.mob_timer = now
			Mob(self)
		
		# hit mobs
		mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
		if mob_hits:
			self.trumpcollide_sound.play()
			self.playing = False

		# check if player hits a platform - only if falling
		if self.player.vel.y > 0:
			hits = pg.sprite.spritecollide(self.player, self.platforms, False)
			if hits:
				lowest = hits[0]
				for hit in hits:
					if hit.rect.bottom > lowest.rect.bottom:
						lowest = hit
				if self.player.pos.x < lowest.rect.right + 10 and self.player.pos.x > lowest.rect.left - 10:
					if self.player.pos.y < lowest.rect.centery:
						self.player.pos.y = lowest.rect.top
						self.player.vel.y = 0
						self.player.jumping = False


		# if player reaches top 1/4th of screen 
		if self.player.rect.top <= HEIGHT / 4:
			self.player.pos.y += max(abs(self.player.vel.y), 2)
			for mob in self.mobs:
				mob.rect.y += max(abs(self.player.vel.y), 2)
			for plat in self.platforms:
				plat.rect.y += max(abs(self.player.vel.y), 2)
				if plat.rect.top >= HEIGHT:
					plat.kill()
					self.score += 10

 		# if player hits a powerup
		pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
		start_time = pg.time.get_ticks()
		end_time = pg.time.get_ticks() + 5000
		for pow in pow_hits:
			if pow.type == 'healthcare':
				self.boost_sound.play()
				self.player.vel.y = -BOOST_POWER
				self.player.jumping = False
			if pow.type == 'education':
				self.educ_sound.play()
				for mob in self.mobs:
					mob.kill()
				self.player.jumping = False
			now = pg.time.get_ticks()
			if pow.type == 'tax':
				self.tax_sound.play()
				self.score += 100
				self.player.jumping = False 
				if now - self.mob_timer > 5000:
					now = self.mob_timer 
					self.draw_text('+ 100', 48, WHITE, WIDTH / 2, HEIGHT / 4) 		
		
		# Bernie dies
		if self.player.rect.bottom > HEIGHT:
			for sprite in self.all_sprites:
				sprite.rect.y -= max(self.player.vel.y, 10)
				if sprite.rect.bottom < 0:
					sprite.kill()
					self.die_sound.play()
		if len(self.platforms) == 0: 
			self.playing = False

		# spawn new platforms to keep same average number of platforms
		while len(self.platforms) < 8:
			width = random.randrange(50, 100)
			p = Platform(self, random.randrange(0, WIDTH - width),
						 random.randrange(-75, -30, 5))



		# calculate the distance between two platforms 

	




		# If the score reaches 5000, allow for more enemies to spawn, and allow them to shoot
		if self.score > 1000:
			now = pg.time.get_ticks()
			if now - self.mob_timer > 4000 + random.choice([-1000, 500, 0, 500, 1000]):
				self.mob_timer = now
				Mob(self)
			# mob hits player with bullet 
			player_hits = pg.sprite.spritecollide(self.player, self.bullets, True, pg.sprite.collide_mask)
			if player_hits:
				self.playing = False



	def events(self):
		# game loop - events
		for event in pg.event.get():
			# check for closing window
			if event.type == pg.QUIT:	
				self.playing = False 
				self.running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_SPACE:
					self.player.jump()
			if event.type == pg.KEYUP:
				if event.key == pg.K_SPACE:
					self.player.jump_cut()


	def draw(self):
		# game loop - draw
		background2 = pg.image.load(path.join(img_dir, 'usflag.jpg')).convert()
		background2_rect = background2.get_rect()
		self.screen.blit(background2, background2_rect)
		# self.screen.fill(BGCOLOR)
		self.all_sprites.draw(self.screen)
		self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
		# after drawing everything, flip the display 
		pg.display.flip()


	def show_start_screen(self):
		# game start screen
		pg.mixer.music.load(path.join(self.snd_dir, 'loading.wav'))
		pg.mixer.music.play(loops=-1)
		background = pg.image.load(path.join(img_dir, 'BernieBG.png')).convert()
		background_rect = background.get_rect()
		self.screen.blit(background, background_rect)
		self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
		self.draw_text('Arrows to move , Space to jump', 22, WHITE, WIDTH / 2, HEIGHT / 2)
		self.draw_text('Press any key to play', 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
		self.draw_text('High Score: ' + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
		pg.display.flip()
		self.wait_for_key()


	def show_go_screen(self):
		if not self.running: 
			return 
		# game over screen
		pg.mixer.music.load(path.join(self.snd_dir, 'loading.wav'))
		pg.mixer.music.play(loops=-1) 
		self.screen.fill(BGCOLOR)
		self.draw_text('GAME OVER', 48, WHITE, WIDTH / 2, HEIGHT / 4)
		self.draw_text('Score: ' + str(self.score), 22, RED, WIDTH / 2, HEIGHT / 2)
		self.draw_text('Press any key to play again', 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
		if self.score > self.highscore:
			self.highscore = self.score 
			self.draw_text("NEW HIGH SCORE", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
			with open(path.join(self.dir, HS_FILE), 'r+') as f:
				f.write(str(self.score))
		else:
			self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
		pg.display.flip()
		self.wait_for_key()

	def wait_for_key(self):
		waiting = True 
		while waiting:
			self.clock.tick(FPS) 
			for event in pg.event.get():
				if event.type == pg.QUIT:
					waiting = False 
					self.running = False 
				if event.type == pg.KEYUP:
					waiting = False 

	def draw_text(self, text, size, color, x, y):
		font = pg.font.Font(self.font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
	g.new()
	g.show_go_screen()

pg.quit()