import pygame
import fonts

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

PLACEHOLDER_ITEMS = {"Ton", "Netzwerk", "WLAN", "Datum & Uhrzeit", "Akku"}

brightness = 70
is_locked = False

exit_to_menu = False

NAVI_UP = pygame.K_UP
NAVI_DOWN = pygame.K_DOWN
NAVI_SELECT = (pygame.K_RETURN, pygame.K_KP_ENTER)
C_KEY = pygame.K_BACKSPACE


def get_brightness():
    return brightness


def get_locked():
    return is_locked


def reset():
    global settings_state, settings_selected_index, exit_to_menu
    settings_state = "menu"
    settings_selected_index = 0
    exit_to_menu = False


def handle_event(event):
    global settings_state, settings_selected_index, brightness, is_locked, exit_to_menu

    if event.type != pygame.KEYDOWN:
        return

    exit_to_menu = False

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
            exit_to_menu = True

    elif settings_state == "brightness":
        if event.key == NAVI_UP:
            brightness = min(100, brightness + 10)
        elif event.key == NAVI_DOWN:
            brightness = max(0, brightness - 10)
        elif event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    elif settings_state == "security":
        if event.key in NAVI_SELECT:
            is_locked = not is_locked
        elif event.key == C_KEY:
            settings_state = "menu"

    elif settings_state == "placeholder":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    elif settings_state == "about":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            settings_state = "menu"

    elif settings_state == "factory_reset_confirm":
        if event.key in NAVI_SELECT:
            settings_state = "menu"
        elif event.key == C_KEY:
            settings_state = "menu"


def draw_softkey_hints(screen, text_color, left_text, right_text):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    if left_text:
        screen.blit(fonts.render(left_text, 16, text_color), (4, HEIGHT - 14))
    if right_text:
        surf = fonts.render(right_text, 16, text_color)
        rect = surf.get_rect(topright=(WIDTH - 4, HEIGHT - 14))
        screen.blit(surf, rect)


def draw_screen(screen, text_color, bg_color):
    """main.py ruft das jetzt als app_settings.draw_screen(screen, BLACK, NOKIA_BG) auf."""
    screen.fill(bg_color)
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    if settings_state == "menu":
        screen.blit(fonts.render("Einstellungen", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        # --- NEU: Das scrollbare Einstellungs-Fenster (max. 6 Einträge gleichzeitig) ---
        MAX_VISIBLE = 6
        start_idx = 0
        if settings_selected_index > 5:
            start_idx = settings_selected_index - 5
        if start_idx > max(0, len(settings_menu_items) - MAX_VISIBLE):
            start_idx = max(0, len(settings_menu_items) - MAX_VISIBLE)

        for i in range(start_idx, min(len(settings_menu_items), start_idx + MAX_VISIBLE)):
            item_y = 22 + ((i - start_idx) * 20)
            item = settings_menu_items[i]
            
            if i == settings_selected_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                surf = fonts.render(item, 20, bg_color)
            else:
                surf = fonts.render(item, 20, text_color)
            screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")

    elif settings_state == "brightness":
        screen.blit(fonts.render("Anzeige", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        label = fonts.render(f"Helligkeit: {brightness}%", 20, text_color)
        screen.blit(label, (6, 40))

        bar_x, bar_y, bar_w, bar_h = 10, 60, WIDTH - 20, 10
        pygame.draw.rect(screen, text_color, (bar_x, bar_y, bar_w, bar_h), 2)
        fill_w = int((bar_w - 4) * (brightness / 100))
        pygame.draw.rect(screen, text_color, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4))

        draw_softkey_hints(screen, text_color, "Navi:+/-", "C:Fertig")

    elif settings_state == "security":
        screen.blit(fonts.render("Sicherheit", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        status = "AN" if is_locked else "AUS"
        screen.blit(fonts.render(f"Tastensperre: {status}", 20, text_color), (6, 40))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:Toggle")

    elif settings_state == "placeholder":
        chosen = settings_menu_items[settings_selected_index]
        screen.blit(fonts.render(chosen, 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        screen.blit(fonts.render("Noch nicht verfügbar", 18, text_color), (6, 40))
        screen.blit(fonts.render("(Hardware fehlt noch)", 18, text_color), (6, 58))

        draw_softkey_hints(screen, text_color, "C:Zurück", "")

    elif settings_state == "about":
        screen.blit(fonts.render("Über das Telefon", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, line in enumerate(["Project 5110", "Radxa Zero 3W", "Firmware: v0.1-dev"]):
            screen.blit(fonts.render(line, 16, text_color), (6, 30 + i * 16))

        draw_softkey_hints(screen, text_color, "C:Zurück", "")

    elif settings_state == "factory_reset_confirm":
        title = fonts.render("Wirklich löschen?", 20, text_color)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        screen.blit(title, title_rect)

        draw_softkey_hints(screen, text_color, "C:Nein", "Navi:Ja")