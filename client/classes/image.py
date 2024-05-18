import pygame

class Image:
    def __init__(self, x, y, image, w = 0, h = 0):
        self.image = image
        if w != 0 or h != 0: self.image = pygame.transform.scale(image, (w,h))
        self.rect = self.image.get_rect(center = (x,y))
        
        self.window = pygame.display.get_surface()
        
    def draw(self):
        self.window.blit(self.image, self.rect)