# Game options and settings 

# screen settings
TITLE = 'Bernie Jump'
WIDTH = 480
HEIGHT = 600 
FPS = 60
FONT_NAME = 'helvetica'
HS_FILE = 'highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'

# player properties 
PLAYER_ACC = 0.5 
PLAYER_FRICTION = -0.12 
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20 

# game properties 
BOOST_POWER = 60
POW_SPAWN_PCT = 2
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