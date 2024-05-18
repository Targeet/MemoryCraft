import pygame, os, settings
pygame.mixer.init()

ASSETS_PATH = settings.ASSETS_PATH

FLIP = pygame.mixer.Sound(ASSETS_PATH + "sound/card_flip.mp3")
BACK = pygame.image.load(ASSETS_PATH + "images/cards/card_back.png")
FRONT = [
    pygame.image.load(ASSETS_PATH + f"images/cards/front/{image}")
    for image in os.listdir(ASSETS_PATH + "images/cards/front")
]

class Card:
    def __init__(self, x, y, w, h, image_id):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.front_image = pygame.transform.scale(FRONT[image_id], (w,h))
        self.back_image = pygame.transform.scale(BACK, (w,h))
        self.rect = pygame.Rect(x - w/2, y - h/2, w, h)
        self.image_id = image_id
        self.id = f"{x}{y}"
        
        self.window = pygame.display.get_surface()
        self.image = self.back_image
        
        #Flip animation
        self.flipped = False
        self.animate_flip = False
        self.first_flip = True
        self.shrink_size = self.w/100*80
        self.flip_frame = 0
        self.flip_frames = 6 #Total frames for the animation
        
        #Hover animation
        self.ishovered = False
        self.animate_hover = False
        self.grow = True
        self.hover_grow = 20
        self.hover_frame = 0
        self.hover_frames = 4
        
    def draw(self):
        self.hovered() #Check for hover
        w, h = self.w, self.h
        
        #Card flip
        if self.animate_flip:
            if self.flip_frame + 1 <= self.flip_frames: self.flip_frame += 1
            elif self.first_flip: #When frames reach max, switch to the second flip and change the card
                self.flip_frame = 0
                self.first_flip = False
                self.flipped = not self.flipped
            elif not self.first_flip: #When second flip is over end the animation and reset variables
                self.flip_frame = 0
                self.first_flip = True
                self.animate_flip = False
                
            #Lerp the width of the rect using 1/frames*frame as weight (0, 100, 1/5*5) = 100
            if self.first_flip: w -= pygame.math.lerp(0, self.shrink_size, (1/self.flip_frames)*self.flip_frame)
            elif not self.first_flip: w -= pygame.math.lerp(self.shrink_size, 0, (1/self.flip_frames)*self.flip_frame)
        
        #Hover 
        if self.animate_hover and self.grow: #Card grows
            w += pygame.math.lerp(0, self.hover_grow, (1/self.hover_frames)*self.hover_frame)
            h += pygame.math.lerp(0, self.hover_grow, (1/self.hover_frames)*self.hover_frame)
            
            if self.hover_frame + 1 <= self.hover_frames: self.hover_frame += 1
            else: 
                self.w += self.hover_grow
                self.h += self.hover_grow
                self.grow = False
                self.hover_frame = 0
        elif self.animate_hover and not self.ishovered: #Card shrinks
            w -= pygame.math.lerp(0, self.hover_grow, (1/self.hover_frames)*self.hover_frame)
            h -= pygame.math.lerp(0, self.hover_grow, (1/self.hover_frames)*self.hover_frame)
            
            if self.hover_frame + 1 <= self.hover_frames: self.hover_frame += 1
            else: 
                self.w -= self.hover_grow
                self.h -= self.hover_grow
                self.hover_frame = 0
                self.animate_hover = False
                self.grow = True
            
        #Change rect sizes and position
        self.rect = pygame.Rect(self.x - w/2, self.y - h/2, w, h) #Create a centered rect with the new width
        shadow_rect = pygame.Rect(self.x - w/2 + 7, self.y - h/2 + 7, w, h)
        shadow_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        #Re-scale image to new rect sizes
        if self.flipped: self.image = pygame.transform.scale(self.front_image, (self.rect.w, self.rect.h))
        else: self.image = pygame.transform.scale(self.back_image, (self.rect.w, self.rect.h))
        
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect())
        self.window.blit(shadow_surface, shadow_rect)
        self.window.blit(self.image, self.rect)
        
    def clicked(self):
        if not self.flipped and not self.animate_flip:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                FLIP.play().set_volume(settings.data["volume"])
                self.animate_flip = True
                return True
        return False
        
    def flip(self):
        self.animate_flip = True
        
    def hovered(self):
        self.ishovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.ishovered: self.animate_hover = True