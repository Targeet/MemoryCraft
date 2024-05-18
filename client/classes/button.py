import pygame, time, settings
pygame.mixer.init()

CLICK = pygame.mixer.Sound(settings.ASSETS_PATH + "sound/button_click.mp3")

class Button:
    def __init__(self, x, y, w, h, font, text = "Button"):
        self.rect = pygame.Rect(x - w/2, y - h/2, w, h)
        self.font = font
        self.text = text
        
        self.bg_color = (106,106,106)
        self.hover_bg_color = (131,131,200)
        self.border_color = (0,0,0)
        self.txt_color = (255,255,255)
        self.hover_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
        
        self.current_color = self.bg_color
        self.window = pygame.display.get_surface()
        
    def draw(self):
        pygame.draw.rect(self.window, self.current_color, self.rect, 0) #Background
        pygame.draw.rect(self.window, self.border_color, self.rect, 3) #Border
        
        if self.text != "":
            text_surface = self.font.render(self.text, 1, self.txt_color)
            
            center_x = self.rect.x + (self.rect.width/2 - text_surface.get_width()/2)
            center_y = self.rect.y + (self.rect.height/2 - text_surface.get_height()/2)
            
            self.window.blit(text_surface, (center_x, center_y + 5))
            
    def hovered(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_color = self.hover_bg_color
            pygame.mouse.set_cursor(self.hover_cursor)
            return True
        else:
            self.current_color = self.bg_color
            return False
        
    def clicked(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            CLICK.play().set_volume(settings.data["volume"])
            time.sleep(0.1)
            return True
        else: return False