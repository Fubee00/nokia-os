import pygame
import sys
import fonts
import app_phone
import app_whatsapp
import app_settings

pygame.init()

NOKIA_BG = (155, 220, 50)
BLACK = (0, 0, 0)

# Exakte Auflösung für dein 1.8-Zoll TFT
WIDTH = 128
HEIGHT = 160
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nokia OS")

menu_items = ["Telefon", "WhatsApp", "Spotify", "Optionen"]
selected_index = 0
current_state = "menu"

# --- STATUSLEISTE FUNKTION ---
def draw_status_bar(screen, color, battery_level=3):
    WIDTH = screen.get_width()

    for i in range(5):
        height = 3 + i
        pygame.draw.rect(screen, color, (4 + (i * 3), 14 - height, 2, height))

    batt_y = 5
    batt_x = WIDTH - 24
    pygame.draw.rect(screen, color, (batt_x, batt_y, 16, 8), 1)
    pygame.draw.rect(screen, color, (batt_x + 16, batt_y + 2, 2, 4))

    for i in range(battery_level):
        pygame.draw.rect(screen, color, (batt_x + 2 + (i * 4), batt_y + 2, 3, 4))

# --- ICONS LADEN ---
try:
    icon_phone = pygame.image.load("phone_icon.png").convert_alpha()
except pygame.error:
    icon_phone = None
    print("Achtung Fube: phone_icon.png nicht gefunden! Prüf den Dateinamen.")

try:
    icon_whatsapp = pygame.image.load("Messeage_icon.png").convert_alpha()
except pygame.error:
    icon_whatsapp = None
    print("Achtung Fube: Messeage_icon.png nicht gefunden! Prüf den Dateinamen.")

try:
    icon_music = pygame.image.load("music_icon.png").convert_alpha()
except pygame.error:
    icon_music = None
    print("Achtung Fube: music_icon.png nicht gefunden!")

# --- NEU: Zahnrad-Icon für die Optionen geladen ---
try:
    icon_settings = pygame.image.load("settings_icon.png").convert_alpha()
except pygame.error:
    icon_settings = None
    print("Achtung Fube: settings_icon.png nicht gefunden! Pack das Zahnrad in den Ordner.")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if current_state == "menu":
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if menu_items[selected_index] == "Telefon":
                        app_phone.reset()
                        current_state = "phone"
                    elif menu_items[selected_index] == "WhatsApp":
                        current_state = "whatsapp"
                    elif menu_items[selected_index] == "Optionen":
                        app_settings.reset()
                        current_state = "settings"
                elif event.unicode.isnumeric():
                    app_phone.reset()
                    app_phone.phone_state = "dialing"
                    app_phone.dialed_number = event.unicode
                    current_state = "phone"

            elif current_state == "phone":
                if event.key == pygame.K_ESCAPE:
                    current_state = "menu"
                else:
                    app_phone.handle_event(event)
                    if app_phone.exit_to_menu:
                        current_state = "menu"

            elif current_state == "settings":
                if event.key == pygame.K_ESCAPE:
                    current_state = "menu"
                else:
                    app_settings.handle_event(event)
                    if app_settings.exit_to_menu:
                        current_state = "menu"

            elif current_state == "whatsapp":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    current_state = "menu"

    # --- ZEICHNEN ---
    if current_state == "menu":
        screen.fill(NOKIA_BG)
        draw_status_bar(screen, BLACK)

        title_text = fonts.render("Menu", 20, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 8))
        screen.blit(title_text, title_rect)

        pygame.draw.line(screen, BLACK, (0, 18), (WIDTH, 18), 2)

        current_app = menu_items[selected_index]

        if current_app == "Telefon" and icon_phone:
            icon_rect = icon_phone.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            screen.blit(icon_phone, icon_rect)
        elif current_app == "WhatsApp" and icon_whatsapp:
            icon_rect = icon_whatsapp.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            screen.blit(icon_whatsapp, icon_rect)
        elif current_app == "Spotify" and icon_music:
            icon_rect = icon_music.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            screen.blit(icon_music, icon_rect)
        # --- NEU: Zahnrad-Icon anzeigen, wenn "Optionen" ausgewählt ist ---
        elif current_app == "Optionen" and icon_settings:
            icon_rect = icon_settings.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            screen.blit(icon_settings, icon_rect)

        app_text = fonts.render(current_app, 24, BLACK)
        text_rect = app_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45))
        screen.blit(app_text, text_rect)

        up_arrow = fonts.render("^", 20, BLACK)
        down_arrow = fonts.render("v", 20, BLACK)
        screen.blit(up_arrow, (WIDTH // 2 - 4, 25))
        screen.blit(down_arrow, (WIDTH // 2 - 4, HEIGHT - 15))

    elif current_state == "phone":
        app_phone.draw_screen(screen, BLACK, NOKIA_BG)

    elif current_state == "whatsapp":
        app_whatsapp.draw_screen(screen, BLACK, NOKIA_BG)

    elif current_state == "settings":
        app_settings.draw_screen(screen, BLACK, NOKIA_BG)

    pygame.display.flip()

pygame.quit()
sys.exit()