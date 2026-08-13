import pygame

# --- ZUSTÄNDE ---
# menu, brightness, security, placeholder, about, factory_reset_confirm
settings_state = "menu"
settings_selected_index = 0

settings_menu_items = [
    "Anzeige",
    "Ton",
    "Netzwerk",
    "WLAN",
    "Datum & Uhrzeit",
    "Sicherheit",
    "Akku",
    "Über das Telefon",
    "Werkseinstellungen",
]

# Items, die technisch noch nicht angebunden sind (warten auf Hardware)
PLACEHOLDER_ITEMS = {"Ton", "Netzwerk", "WLAN", "Datum & Uhrzeit", "Akku"}

# --- ECHTE FUNKTIONEN ---
brightness = 70          # 0-100, später an ST7789-Backlight-PWM koppeln
is_locked = False        # Tastensperre an/aus

NAVI_UP = pygame.K_UP
NAVI_DOWN = pygame.K_DOWN
NAVI_SELECT = (pygame.K_RETURN, pygame.K_KP_ENTER)
C_KEY = pygame.K_BACKSPACE


def get_brightness():
    """Für main.py/Hardware-Layer: aktuellen Helligkeitswert (0-100) abfragen."""
    return brightness


def get_locked():
    return is_locked


def reset():
    global settings_state, settings_selected_index
    settings_state = "menu"
    settings_selected_index = 0


def handle_event(event, global_state):
    global settings_state, settings_selected_index, brightness, is_locked

    if event.type != pygame.KEYDOWN:
        return global_state  # Wenn keine Taste gedrückt wird, Status einfach zurückgeben

    # --- HAUPTMENÜ DER EINSTELLUNGEN ---
    if settings_state == "menu":
        if event.key == NAVI_UP:
            settings_selected_index = (settings_selected_index - 1) % len(settings_menu_items)
        elif event.key == NAVI_DOWN:
            settings_selected_index = (settings_selected_index + 1) % len(settings_menu_items)
        elif event.key in NAVI_SELECT:
            chosen = settings_menu_items[settings_selected_index]
            if chosen == "Anzeige":
                settings_state = "brightness"
            elif chosen == "Sicherheit":
                settings_state = "security"
            elif chosen == "Über das Telefon":
                settings_state = "about"
            elif chosen == "Werkseinstellungen":
                settings_state = "factory_reset_confirm"
            elif chosen in PLACEHOLDER_ITEMS:
                settings_state = "placeholder"
        
        elif event.key == C_KEY:
            # HIER IST DER TRICK: Wenn wir im Hauptmenü der Settings "C" drücken,
            # schicken wir "menu" an die main.py zurück, um die App zu beenden!
            settings_state = "menu"
            return "menu"

    # --- HELLIGKEIT (funktional) ---
    elif settings_state == "brightness":
        if event.key == NAVI_UP:
            brightness = min(100, brightness + 10)
        elif event.key == NAVI_DOWN:
            brightness = max(0, brightness - 10)
        elif event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    # --- SICHERHEIT / TASTENSPERRE (funktional) ---
    elif settings_state == "security":
        if event.key in NAVI_SELECT:
            is_locked = not is_locked
        elif event.key == C_KEY:
            settings_state = "menu"

    # --- PLATZHALTER FÜR NOCH FEHLENDE HARDWARE ---
    elif settings_state == "placeholder":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    # --- ÜBER DAS TELEFON ---
    elif settings_state == "about":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    # --- WERKSEINSTELLUNGEN BESTÄTIGEN ---
    elif settings_state == "factory_reset_confirm":
        if event.key in NAVI_SELECT:
            # Platzhalter für Lösch-Logik
            settings_state = "menu"
        elif event.key == C_KEY:
            settings_state = "menu"

    # Am Ende schicken wir den Status zurück an die main.py
    return global_state


def draw_softkey_hints(screen, font, text_color, left_text, right_text):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    if left_text:
        screen.blit(font.render(left_text, True, text_color), (4, HEIGHT - 14))
    if right_text:
        surf = font.render(right_text, True, text_color)
        rect = surf.get_rect(topright=(WIDTH - 4, HEIGHT - 14))
        screen.blit(surf, rect)


def draw_screen(screen, font, text_color, bg_color):
    screen.fill(bg_color)
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    hint_font = pygame.font.Font(None, 16)

    if settings_state == "menu":
        title = font.render("Einstellungen", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, item in enumerate(settings_menu_items):
            item_y = 26 + (i * 18)
            if i == settings_selected_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 16))
                surf = font.render(item, True, bg_color)
            else:
                surf = font.render(item, True, text_color)
            screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "Navi:OK")

    elif settings_state == "brightness":
        title = font.render("Anzeige", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        label = font.render(f"Helligkeit: {brightness}%", True, text_color)
        screen.blit(label, (6, 40))

        bar_x, bar_y, bar_w, bar_h = 10, 60, WIDTH - 20, 10
        pygame.draw.rect(screen, text_color, (bar_x, bar_y, bar_w, bar_h), 2)
        fill_w = int((bar_w - 4) * (brightness / 100))
        pygame.draw.rect(screen, text_color, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4))

        draw_softkey_hints(screen, hint_font, text_color, "Navi:+/-", "C:Fertig")

    elif settings_state == "security":
        title = font.render("Sicherheit", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        status = "AN" if is_locked else "AUS"
        label = font.render(f"Tastensperre: {status}", True, text_color)
        screen.blit(label, (6, 40))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "Navi:Toggle")

    elif settings_state == "placeholder":
        chosen = settings_menu_items[settings_selected_index]
        title = font.render(chosen, True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        msg_font = pygame.font.Font(None, 18)
        msg = msg_font.render("Noch nicht verfügbar", True, text_color)
        screen.blit(msg, (6, 40))
        msg2 = msg_font.render("(Hardware fehlt noch)", True, text_color)
        screen.blit(msg2, (6, 58))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "")

    elif settings_state == "about":
        title = font.render("Über das Telefon", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        info_font = pygame.font.Font(None, 16)
        lines = ["Project 5110", "Radxa Zero 3W", "Firmware: v0.1-dev"]
        for i, line in enumerate(lines):
            surf = info_font.render(line, True, text_color)
            screen.blit(surf, (6, 30 + i * 16))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "")

    elif settings_state == "factory_reset_confirm":
        title = font.render("Wirklich löschen?", True, text_color)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        screen.blit(title, title_rect)

        draw_softkey_hints(screen, hint_font, text_color, "C:Nein", "Navi:Ja")