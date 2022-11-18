import pygame
import random

class Enemy(pygame.sprite.Sprite):
	def __init__(self, SCREEN_WIDTH, y, sprite_sheet, scale):
		# Proses Inheritance
		pygame.sprite.Sprite.__init__(self)

		# mendefinisikan variable
		self.animation_list = []
		self.frame_index = 0
		self.update_time = pygame.time.get_ticks()
		self.direction = random.choice([-1, 1])

		# menetapkan arah image menurut arah muncul rintangan
		if self.direction == 1:
			self.flip = True
		else:
			self.flip = False

		# memproses gambar menjadi animasi
		animation_steps = 8
		for animation in range(animation_steps):
			image = sprite_sheet.get_image(animation, 32, 32, scale, (0, 0, 0))
			image = pygame.transform.flip(image, self.flip, False)
			image.set_colorkey((0, 0, 0))
			self.animation_list.append(image)
		
		# membuat rectangle dari gambar
		self.image = self.animation_list[self.frame_index]
		self.rect = self.image.get_rect()

		# menetapkan arah muncul rintangan
		if self.direction == 1:
			self.rect.x = 0
		else:
			self.rect.x = SCREEN_WIDTH
		self.rect.y = y

	def update(self, scroll, SCREEN_WIDTH):
		# memperbarui animasi
		ANIMATION_COOLDOWN = 50
		self.image = self.animation_list[self.frame_index]

		# memperbarui animasi setelah cooldown selesai
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
			
		# mereset animasi seperti awal
		if self.frame_index >= len(self.animation_list):
			self.frame_index = 0

		# menggerakan posisi rintangan
		self.rect.x += self.direction * 2
		self.rect.y += scroll

		# pengecekan apakah rintangan sudah melewati screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()