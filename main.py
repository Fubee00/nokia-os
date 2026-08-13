import pygame
import sys
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

font = pygame.font.Font(None, 20)      # Für kleine Texte
big_font = pygame.font.Font(None, 24)  # Für den App-Namen

menu_items = ["Telefon", "WhatsApp", "Spotify", "Optionen"]
selected_index = 0
current_state = "menu"

# --- STATUSLEISTE FUNKTION (Korrekt mit batt_y verknüpft) ---
def draw_status_bar(screen, color, battery_level=3):
    WIDTH = screen.get_width()
    
    # Empfangsbalken links (5 Striche)
    for i in range(5):
        height = 3 + i
        pygame.draw.rect(screen, color, (4 + (i * 3), 14 - height, 2, height))

    # Batterie-Koordinaten
    batt_y = 5
    batt_x = WIDTH - 24
    
    # Batterie-Symbol rechts (jetzt mit korrekter Y-Position!)
    pygame.draw.rect(screen, color, (batt_x, batt_y, 16, 8), 1)
    pygame.draw.rect(screen, color, (batt_x + 16, batt_y + 2, 2, 4))
    
    # Batterie-Füllung (je nach Stufe)
    for i in range(battery_level):
        pygame.draw.rect(screen, color, (batt_x + 2 + (i * 4), batt_y + 2, 3, 4))

# --- HIER LADEN WIR DIE ICONS ---
try:
    icon_phone = pygame.image.load("phone_icon.png").convert_alpha()
except pygame.error:
    icon_phone = None
    print("Achtung Fube: phone_icon.png nicht gefunden! Prüf den Dateinamen.")

try:
    icon_whatsapp = pygame.image.load("Messeage_icon.png").convert_alpha()
except pygame.error:
    icon_whatsapp = None
    print("Achtung Fube: whatsapp.png nicht gefunden! Prüf den Dateinamen.")

try:
    icon_music = pygame.image.load("music_icon.png").convert_alpha()
except pygame.error:
    icon_music = None
    print("Achtung Fube: music_icon.png nicht gefunden!")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state == "menu":
                    running = False
                else:
                    current_state = "menu"
            
            # --- STEUERUNG IM HAUPTMENÜ ---
            elif current_state == "menu":
                if event.key == pygame.K_UP:
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
                        current_state = "settings"
                
                # --- DIREKT AUS DEM HAUPTMENÜ NUMMER WÄHLEN ---
                elif event.unicode.isnumeric():
                    selected_index = 0 
                    app_phone.reset()
                    app_phone.phone_state = "dialing"
                    app_phone.dialed_number = event.unicode
                    current_state = "phone"

            # --- STEUERUNG IN DEN APPS ---
            elif current_state == "phone":
                app_phone.handle_event(event)

            elif current_state == "settings":
                current_state = app_settings.handle_event(event, current_state)

    # --- BILDER ZEICHNEN ---
    if current_state == "menu":
        screen.fill(NOKIA_BG)
        
        # Statusleiste oben zeichnen (Empfang & Batterie)
        draw_status_bar(screen, BLACK)
        
        # Kopfzeile (Menü-Titel in der Mitte der Statusleiste)
        title_text = font.render("Menu", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, 8))
        screen.blit(title_text, title_rect)
        
        # Trennstrich unter der Statusleiste
        pygame.draw.line(screen, BLACK, (0, 18), (WIDTH, 18), 2)

        # Aktuelle App auslesen
        current_app = menu_items[selected_index]

        # Das passende Icon in die Mitte klatschen
        if current_app == "Telefon" and icon_phone:
            icon_rect = icon_phone.get_rect(center=(WIDTH//2, HEIGHT//2 - 10))
            screen.blit(icon_phone, icon_rect)
        elif current_app == "WhatsApp" and icon_whatsapp:
            icon_rect = icon_whatsapp.get_rect(center=(WIDTH//2, HEIGHT//2 - 10))
            screen.blit(icon_whatsapp, icon_rect)
        elif current_app == "Spotify" and icon_music: # <--- HIER DEIN NEUER ZWEIG
            icon_rect = icon_music.get_rect(center=(WIDTH//2, HEIGHT//2 - 10))
            screen.blit(icon_music, icon_rect)
        

        # App-Name unter das Icon klatschen
        app_text = big_font.render(current_app, True, BLACK)
        text_rect = app_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 45))
        screen.blit(app_text, text_rect)

        # Kleine Pfeile zum Scrollen
        up_arrow = font.render("^", True, BLACK)
        down_arrow = font.render("v", True, BLACK)
        screen.blit(up_arrow, (WIDTH//2 - 4, 25))
        screen.blit(down_arrow, (WIDTH//2 - 4, HEIGHT - 15))

    elif current_state == "phone":
        app_phone.draw_screen(screen, font, BLACK, NOKIA_BG)
        
    elif current_state == "whatsapp":
        app_whatsapp.draw_screen(screen, font, BLACK, NOKIA_BG)

    elif current_state == "settings":
        app_settings.draw_screen(screen, font, BLACK, NOKIA_BG)
      

    pygame.display.flip()

pygame.quit()
sys.exit()