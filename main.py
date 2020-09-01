# Bernie Jump

# Art from Kenney.nl
# Bernie and Trump art from 'Super Smash Presidents Game -github.com/'
# Xeon theme https://opengameart.org/users/bart
import pygame as pg
import random 
from settings import *
from sprites import *
from os import path
import time
import pygame.mask

class Game:
	def __init__(self):
		# initialize game window, etc 
		pg.init()
		pg.mixer.init(channels = 1)
		self.channel1 = pg.mixer.Channel(0) # argument must be int
		self.channel2 = pg.mixer.Channel(1)
		self.screen = pg.display.set_mode((WIDTH, HEIGHT))
		pg.display.set_caption('Bernie Jump')
		self.clock = pg.time.Clock()
		self.running = True
		self.font_name = pg.font.match_font(FONT_NAME)
		self.load_data()

	def load_data(self):
		# load high score 
		self.dir = path.dirname('__file__')
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
		self.educ_sound.set_volume(0.25)
		# Raising taxes related soundbit
		self.tax_sound = pg.mixer.Sound(path.join(self.snd_dir, 'taxes.wav'))
		self.tax_sound.set_volume(1.0)
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
		self.player = Player(self)
		for plat in PLATFORM_LIST:
			Platform(self, *plat)
		self.mob_timer = 0
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
			self.channel1.play(self.trumpcollide_sound)
			self.playing = False

		# check if player hits a platform - only if falling
		if self.player.vel.y > 0: 
			hits = pg.sprite.spritecollide(self.player, self.platforms, False)
			if hits:
				lowest = hits[0]
				for hit in hits: 
					if hit.rect.bottom > lowest.rect.bottom: 
						lowest = hit 
				if self.player.pos.x < lowest.rect.right + 10 and \
					self.player.pos.x > lowest.rect.left - 10: 
					if self.player.pos.y < hits[0].rect.bottom:
						self.player.pos.y = hits[0].rect.top
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
				self.channel1.play(self.boost_sound)
				self.player.vel.y = -BOOST_POWER
				self.player.jumping = False
			if pow.type == 'education':
				self.channel1.play(self.educ_sound)
				for mob in self.mobs:
					mob.kill()
				self.player.jumping = False
			now = pg.time.get_ticks()
			if pow.type == 'tax':
				self.channel1.play(self.tax_sound)
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
					self.channel1.play(self.die_sound)
		if len(self.platforms) == 0: 
			self.playing = False

		# spawn new platforms to keep same average number of platforms
		while len(self.platforms) < 6:
			width = random.randrange(50, 100)
			Platform(self, random.randrange(0, WIDTH - width),
						 random.randrange(-75, -30, 15))

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
		self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, 15)
		self.draw_text("Highscore: " + str(self.highscore), 22, WHITE, WIDTH / 2, 40)
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
			# insert option for player to enter name and add name to list of highscores
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