import pygame, string

class TextBox:
    def __init__(self, x, y, w, h, font, text = ""):
        self.rect = pygame.Rect(x - w/2, y - h/2, w, h)
        self.font = font
        
        self.bg_color = (0,0,0)
        self.inactive_border_color = (148,148,148)
        self.active_border_color = (255,255,255)
        self.txt_color = (255,255,255)
        self.txt_shadow_color = (60,60,60)
        self.hover_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_IBEAM)
        self.allowed_char = list(string.ascii_letters) + list(string.digits) + list(string.whitespace) + list(string.punctuation)
        self.max_length = 16
        
        self.text = text
        self.active = False
        self.border_color = self.inactive_border_color
        self.window = pygame.display.get_surface()
    
    def draw(self):
        self.border_color = self.active_border_color if self.active else self.inactive_border_color
        
        pygame.draw.rect(self.window, self.bg_color, self.rect, 0)
        pygame.draw.rect(self.window, self.border_color, self.rect, 3)
        
        if self.text != "":
            
            text_shadow = self.font.render(self.text, 1, self.txt_shadow_color)
            text_surface = self.font.render(self.text, 1, self.txt_color)
            
            center_y = self.rect.y + (self.rect.height/2 - text_surface.get_height()/2)
            
            self.window.blit(text_shadow, (self.rect.x + 12, center_y + 6))
            self.window.blit(text_surface, (self.rect.x + 10, center_y + 3))
        
    def hovered(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(self.hover_cursor)
            return True
        return False
    
    def clicked(self):
        self.active = self.rect.collidepoint(pygame.mouse.get_pos())
                
    def keydown(self, event): 
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode in self.allowed_char:
                self.text += event.unicode