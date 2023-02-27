import pygame


class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed, height_y_contraint):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill(color='white')
        self.rect = self.image.get_rect(center=position)
        self.speed = speed
        self.height_y_contraint = height_y_contraint

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_contraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()
