# import Library
import pygame
import random
import os
from pygame import mixer

# Import module tambahan
from spritesheet import SpriteSheet
from enemy import Enemy

# inisialisasi pygame dan mixer
pygame.init()
mixer.init()

# inisialisasi variable window game
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# inisialisasi window game
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('AstroJump')

# frame rate pada game
clock = pygame.time.Clock()
FPS = 60

# backsound pada game
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0)

# sound effect pada game saat keadaan lompat
jump_fx = pygame.mixer.Sound('assets/jump.mp3')
jump_fx.set_volume(0.4)

# sound effect pada game saat keadaan mati
death_fx = pygame.mixer.Sound('assets/death.mp3')
death_fx.set_volume(0.5)

# variable - variable yang akan digunakan pada game
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

# mengecek kondisi file score
if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

# warna - warna yang akan digunakan dalam game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (25, 17, 127)

# jenis font yang akan digunakan dalam game
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

# image yang digunakan sebagai karakter utama
astro_image = pygame.image.load('assets/astro.png').convert_alpha()

# image yang digunakan sebagai background
bg_image = pygame.image.load('assets/background.jpg').convert_alpha()

# image yang digunakan sebagai pijakan karakter
wall_image = pygame.image.load('assets/wall.png').convert_alpha()

# image yang digunakan sebagai rintangan ufo
ufo_sheet_img = pygame.image.load('assets/ufo.png').convert_alpha()
ufo_sheet = SpriteSheet(ufo_sheet_img)

# image yang digunakan sebagai rintangan pesawat luar angkasa
spacecraft_sheet_img = pygame.image.load('assets/spacecraft.png').convert_alpha()
spacecraft_sheet = SpriteSheet(spacecraft_sheet_img)


# fungsi untuk menampilkan text
def draw_text(text, font, text_col, x, y):
	text = font.render(text, True, text_col)
	screen.blit(text, (x, y))

# fungsi untuk menampilkan score saat game berjalan
def draw_panel():
	draw_text(' Score : ' + str(score), font_small, WHITE, 5, 5)

# fungsi untuk menampilkan background yang berulang
def draw_bg(bg_scroll):
	screen.blit(bg_image, (0, 0 + bg_scroll))
	screen.blit(bg_image, (0, -600 + bg_scroll))

# class untuk karakter utama game
class Player():
	# mendefinisikan karakter utama
	def __init__(self, x, y):
		self.image = pygame.transform.scale(astro_image, (60, 65))
		self.width = 45
		self.height = 60
		# membuat rectangle dari width and height untuk karakter utama
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = (x, y)
		self.velocity_y = 0
		self.flip = False
	
	# proses input serta pengkondisian dalam game
	def move(self):
		# mereset ulang variable ketika game dimulai kembali
		scroll = 0
		dx = 0
		dy = 0

		# input proses in game oleh player
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] or key[pygame.K_a]:
			dx = -10
			self.flip = True
		if key[pygame.K_RIGHT] or key[pygame.K_d]:
			dx = 10
			self.flip = False

		# mensetting gravity
		self.velocity_y += GRAVITY
		# setiap iterasi akan mempengaruhi letak sumbu y karakter
		dy += self.velocity_y

		#setting batas layar kiri
		if self.rect.left + dx < 0:
			dx = 0 - self.rect.left
			
		#setting batas layar kanan
		if self.rect.right + dx > SCREEN_WIDTH:
			dx = SCREEN_WIDTH - self.rect.right

		# melihat kondisi pada in game
		for platform in platform_group:
			# mengecek apakah karakter bertabrakan dengan wall
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# mengecek apakah karakter berhasil naik ke atas wall
				if self.rect.bottom < platform.rect.centery:
					# jika karakter berhasil naik ke atas wall maka dia akan melompat, sebaliknya akan jatuh karena gravitasi
					if self.velocity_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.velocity_y = -20
						# sound effect ketika berhasil naik ke wall
						jump_fx.play()

		# mengecek apakah karakter telah lompat dan melewati batas layar atas
		if self.rect.top <= SCROLL_THRESH:
			# jika player lompat
			if self.velocity_y < 0:
				scroll = -dy

		# memperbarui background karena karakter telat melewati batas atas
		self.rect.x += dx
		self.rect.y += dy + scroll

		# membuat mask berdasarkan image karakter utama
		self.mask = pygame.mask.from_surface(self.image)
		return scroll
	
	# fungsi untuk menampilkan gambar dalam game
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 5, self.rect.y))
		# menampilkan rectagle di sekitar karakter utama
		# pygame.draw.rect(screen, WHITE, self.rect, 2)

# class untuk wall dalam game
class Platform(pygame.sprite.Sprite):
	# mendefinisikan wall
	def __init__(self, x, y, width, moving):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(wall_image, (width, 60))
		self.moving = moving
		self.move_counter = random.randint(0, 50)
		self.direction = random.choice([-1, 1])
		self.speed = random.randint(1, 2)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
	
	# memperbarui posisi wall
	def update(self, scroll):
		# menggerakan wall untuk wall yang bergerak
		if self.moving == True:
			self.move_counter += 1
			self.rect.x += self.direction * self.speed

		# menganti arah bergerak wall atau memantulkan arah gerak wall
		if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
			self.direction *= -1
			self.move_counter = 0

		# memperbarui posisi vertikal wall
		self.rect.y += scroll

		# menghapus wall jika sudah melewati screen
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()

# membuat objek player
astro = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# membuat grup yang berisi wall dalam game
platform_group = pygame.sprite.Group()

# membuat grup yang berisi rintangan dalam game
obstacle_group = pygame.sprite.Group()

# membuat objek platform sebagai pijakan awal
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 60, 100, False)
platform_group.add(platform)

# proses game berjalan
run = True
while run:

	clock.tick(FPS)

	# game dimulai setelah pengecekan game over
	if game_over == False:

		# mendapatkan variable scroll
		scroll = astro.move()

		# menampilkan background
		bg_scroll += scroll
		if bg_scroll >= 600:
			# mereset ulang variable bg_scroll agar background menjadi tidak terbatas
			bg_scroll = 0
		draw_bg(bg_scroll)

		# membuat wall, dengan max wall 10
		if len(platform_group) < MAX_PLATFORMS:
			# membuat variable width otomatis secara random untuk wall
			p_w = random.randint(50, 60)

			# membuat variable posisi sumbu x otomatis secara random untuk wall
			p_x = random.randint(0, SCREEN_WIDTH - p_w)

			# membuat variable posisi sumbu y otomatis secara random berdasarkan sumbu y wall sebelumnya agar karakter dapat terus naik
			p_y = platform.rect.y - random.randint(80, 120)

			# membuat variable tipe otomatis secara random untuk wall
			p_type = random.randint(1, 2)

			# membuat kondisi jika score more than 500, maka wall akan bergerak
			if p_type == 1 and score > 500:
				p_moving = True
			else:
				p_moving = False
			
			# membuat objek platform berdasarkan parameter - parameter yang sudah digenerate secara random
			platform = Platform(p_x, p_y, p_w, p_moving)
			
			# menyimpan objek - objek platform ke grup
			platform_group.add(platform)

		# memperbarui posisi wall
		platform_group.update(scroll)

		# membuat rintangan sesuai kondisi
		if len(obstacle_group) == 0 and score > 1500:
			obs = random.randint(80, 200)
			enemy = Enemy(SCREEN_WIDTH, obs, ufo_sheet, 2)
			obstacle_group.add(enemy)

			if score > 2000:
				obs1 = random.randint(80, 200)
				enemy2 = Enemy(SCREEN_WIDTH, obs1, spacecraft_sheet, 2)
				obstacle_group.add(enemy2)

		# memperbarui rintangan
		obstacle_group.update(scroll, SCREEN_WIDTH)

		# memperbarui score, semakin tinggi karakter naik semakin banyak score
		if scroll > 0:
			score += scroll

		# menampilan garis jika sudah mencapai high score
		pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
		draw_text('High Score!', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

		# menampilkan wall dalam game
		platform_group.draw(screen)

		# menampilkan rintangan dalam game
		obstacle_group.draw(screen)

		# menampilkan karakter utama dalam game
		astro.draw()

		# menampilkan score selama game berlangsung
		draw_panel()

		# mengecek kondisi game over
		if astro.rect.top > SCREEN_HEIGHT:
			game_over = True
			# sound effect ketika jatuh dari wall
			death_fx.play()

		# mengecek jika bertabrakan dengan rintangan
		if pygame.sprite.spritecollide(astro, obstacle_group, False):
			if pygame.sprite.spritecollide(astro, obstacle_group, False, pygame.sprite.collide_mask):
				game_over = True
				# sound effect ketika bertabrakan dengan rintangan
				death_fx.play()
	
	# game berhenti setelah kondisi game over
	else:
		# menampilkan transisi ketika game over
		if fade_counter < SCREEN_WIDTH:
			fade_counter += 5
			for y in range(0, 6, 2):
				pygame.draw.rect(screen, WHITE, (0, y * 150, fade_counter, 150))
				pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - fade_counter, (y + 1) * 150, SCREEN_WIDTH, 150))
		
		# menampilkan hasil game ketika game over
		else:
			# kondisi jika melebihi high score
			if score > high_score:
				draw_text('You Reach New High Score!', font_big, PANEL, 50, 200)
				draw_text('Score : ' + str(score), font_big, PANEL, 135, 250)
				draw_text('Press space to play again', font_big, PANEL, 50, 300)

			# kondisi jika tidak melebihi high score
			elif score < high_score:
				draw_text('Game Over!', font_big, PANEL, 125, 200)
				draw_text('Score : ' + str(score), font_big, PANEL, 140, 250)
				draw_text('Press space to play again', font_big, PANEL, 50, 300)

			# memperbarui jika file sudah ada atau membuat file baru dan write high score
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))

			# jika space ditekan, game akan dimulai kembali
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE]:
				# mereset ulang variable menjadi seperti game dimulai
				game_over = False
				score = 0
				scroll = 0
				fade_counter = 0

				# menempatkan karakter seperti semula
				astro.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

				# mereset rintangan
				obstacle_group.empty()

				# mereset wall
				platform_group.empty()
		
				# membuat objek platform sebagai pijakan awal kembali
				platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
				platform_group.add(platform)


	# kondisi jika game di tutup tanpa menabrak rintangan
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# memperbarui high score jika game di close
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			run = False

	# memperbarui display
	pygame.display.update()

# game berhenti
pygame.quit()