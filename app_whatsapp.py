import pygame
import fonts


def draw_screen(screen, text_color, bg_color):
    """main.py ruft das jetzt als app_whatsapp.draw_screen(screen, BLACK, NOKIA_BG) auf."""
    screen.fill(bg_color)
    WIDTH = screen.get_width()

    # Kopfzeile
    title = fonts.render("WhatsApp", 20, text_color)
    screen.blit(title, (5, 5))
    pygame.draw.line(screen, text_color, (0, 35), (WIDTH, 35), 2)

    # Ein kleiner Fake-Chat
    chat1 = fonts.render("Fube: Moin!", 16, text_color)
    chat2 = fonts.render("Daniel: Was geht?", 16, text_color)

    screen.blit(chat1, (10, 50))
    screen.blit(chat2, (10, 80))