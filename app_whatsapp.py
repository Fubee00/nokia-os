import pygame

def draw_screen(screen, font, text_color, bg_color):
    screen.fill(bg_color)
    
    # Kopfzeile
    title = font.render("WhatsApp", True, text_color)
    screen.blit(title, (5, 5))
    pygame.draw.line(screen, text_color, (0, 35), (240, 35), 2)
    
    # Ein kleiner Fake-Chat
    chat1 = font.render("Fube: Moin!", True, text_color)
    chat2 = font.render("Daniel: Was geht?", True, text_color)
    
    screen.blit(chat1, (10, 50))
    screen.blit(chat2, (10, 80))