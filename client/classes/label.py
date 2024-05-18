import pygame

class Label:
    def __init__(self, x, y, font, text = "Label", text_shadow = False, color = (255,255,255), w = 50, h = 50, align = "center"):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.font = font
        self.text = text
        self.text_shadow = text_shadow
        self.align = align
        
        self.color = color
        self.shadow_color = (80,80,80)
        
        self.window = pygame.display.get_surface()
    
    def draw(self):
        if self.text != "":
            text_surface = self.font.render(self.text, 1, self.color)
            x, y = 0, 0
            
            #Align text
            match self.align: 
                case "right":
                    x, y = self.x - self.w/2, self.y - self.h/2
                case "center":
                    x, y = self.x - text_surface.get_width()/2, self.y - self.h/2
            
            if self.text_shadow:
                shadow_surface = self.font.render(self.text, 1, self.shadow_color)
                self.window.blit(shadow_surface, (x + 7, y + 7))
            self.window.blit(text_surface, (x, y))
            
            
            