import json
import pygame

# --- ZUSTÄNDE ---
# sub_menu, dialing, dial_actions, calling, add_contact, contacts_list
phone_state = "sub_menu"
phone_menu_items = ["Nummer wählen", "Kontakte", "Anrufliste"]
phone_selected_index = 0
dialed_number = ""

# Mini-Aktionsmenü, das aufpoppt wenn man im Wählbildschirm die NaviKey drückt
dial_actions = ["Anrufen", "Kontakt speichern", "Löschen"]
dial_actions_index = 0

contacts = []  # Liste von {"name": ..., "number": ...}
contacts_selected_index = 0
new_contact_name = ""

# --- ECHTE TASTENBELEGUNG DES 5110 (Platzhalter auf der PC-Tastatur zum Testen) ---
# NaviKey hoch/runter    -> Pfeiltasten
# NaviKey reindrücken    -> Enter
# C-Taste (Löschen/Back) -> Backspace
# Zifferntasten 0-9,*,# -> direkt
NAVI_UP = pygame.K_UP
NAVI_DOWN = pygame.K_DOWN
NAVI_SELECT = (pygame.K_RETURN, pygame.K_KP_ENTER)
C_KEY = pygame.K_BACKSPACE


def reset():
    global phone_state, phone_selected_index, dialed_number
    phone_state = "sub_menu"
    phone_selected_index = 0
    dialed_number = ""


def handle_event(event):
    global phone_state, phone_selected_index, dialed_number
    global dial_actions_index, contacts, contacts_selected_index, new_contact_name

    if event.type != pygame.KEYDOWN:
        return

    # --- HAUPT-UNTERMENÜ ---
    if phone_state == "sub_menu":
        if event.key == NAVI_UP:
            phone_selected_index = (phone_selected_index - 1) % len(phone_menu_items)
        elif event.key == NAVI_DOWN:
            phone_selected_index = (phone_selected_index + 1) % len(phone_menu_items)
        elif event.key in NAVI_SELECT:
            chosen = phone_menu_items[phone_selected_index]
            if chosen == "Nummer wählen":
                phone_state = "dialing"
                dialed_number = ""
            elif chosen == "Kontakte":
                phone_state = "contacts_list"
                contacts_selected_index = 0
        elif event.unicode.isnumeric():
            phone_state = "dialing"
            dialed_number = event.unicode

    # --- NUMMER EINTIPPEN ---
    elif phone_state == "dialing":
        if event.unicode.isnumeric() or event.unicode in ("*", "#"):
            dialed_number += event.unicode
        elif event.key == C_KEY:
            if dialed_number:
                dialed_number = dialed_number[:-1]
            else:
                # C bei leerem Feld = zurück, wie am echten Gerät
                phone_state = "sub_menu"
        elif event.key in NAVI_SELECT:
            if dialed_number:
                phone_state = "dial_actions"
                dial_actions_index = 0

    # --- NEU: MINI-AKTIONSMENÜ (statt Tab-Shortcut) ---
    elif phone_state == "dial_actions":
        if event.key == NAVI_UP:
            dial_actions_index = (dial_actions_index - 1) % len(dial_actions)
        elif event.key == NAVI_DOWN:
            dial_actions_index = (dial_actions_index + 1) % len(dial_actions)
        elif event.key == C_KEY:
            phone_state = "dialing"
        elif event.key in NAVI_SELECT:
            chosen = dial_actions[dial_actions_index]
            if chosen == "Anrufen":
                phone_state = "calling"
            elif chosen == "Kontakt speichern":
                phone_state = "add_contact"
                new_contact_name = ""
            elif chosen == "Löschen":
                dialed_number = ""
                phone_state = "dialing"

    # --- NEU: PLATZHALTER FÜR ECHTEN ANRUF ---
    elif phone_state == "calling":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            phone_state = "sub_menu"
            dialed_number = ""

    # --- KONTAKT SPEICHERN (Name eintippen) ---
    elif phone_state == "add_contact":
        if event.key in NAVI_SELECT:
            if new_contact_name.strip():
                contacts.append({"name": new_contact_name.strip(), "number": dialed_number})
            phone_state = "sub_menu"
        elif event.key == C_KEY:
            if new_contact_name:
                new_contact_name = new_contact_name[:-1]
            else:
                phone_state = "dial_actions"
        elif event.unicode and event.unicode.isprintable():
            if len(new_contact_name) < 20:
                new_contact_name += event.unicode

    # --- KONTAKTLISTE ---
    elif phone_state == "contacts_list":
        if event.key == NAVI_UP and contacts:
            contacts_selected_index = (contacts_selected_index - 1) % len(contacts)
        elif event.key == NAVI_DOWN and contacts:
            contacts_selected_index = (contacts_selected_index + 1) % len(contacts)
        elif event.key in NAVI_SELECT:
            if contacts:
                dialed_number = contacts[contacts_selected_index]["number"]
                phone_state = "dialing"
        elif event.key == C_KEY:
            phone_state = "sub_menu"


def wrap_number(number, chars_per_line=8):
    if not number:
        return [""]
    return [number[i:i + chars_per_line] for i in range(0, len(number), chars_per_line)]


def draw_softkey_hints(screen, font, text_color, left_text, right_text):
    """Kurze Hinweise unten links/rechts statt einer langen Zeile,
    damit nichts über den 128px-Screen rausläuft."""
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    if left_text:
        surf = font.render(left_text, True, text_color)
        screen.blit(surf, (4, HEIGHT - 14))
    if right_text:
        surf = font.render(right_text, True, text_color)
        rect = surf.get_rect(topright=(WIDTH - 4, HEIGHT - 14))
        screen.blit(surf, rect)


def draw_screen(screen, font, text_color, bg_color):
    screen.fill(bg_color)
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    hint_font = pygame.font.Font(None, 16)

    # --- ANSICHT 1: TELEFON-UNTERMENÜ ---
    if phone_state == "sub_menu":
        title = font.render("Telefon", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, item in enumerate(phone_menu_items):
            item_y = 26 + (i * 22)
            if i == phone_selected_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                item_surface = font.render(item, True, bg_color)
            else:
                item_surface = font.render(item, True, text_color)
            screen.blit(item_surface, (6, item_y))

        draw_softkey_hints(screen, hint_font, text_color, "Navi:OK", "")

    # --- ANSICHT 2: NUMMER EINTIPPEN ---
    elif phone_state == "dialing":
        title = font.render("Nummer wählen", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        number_font = pygame.font.Font(None, 28)
        lines = wrap_number(dialed_number, chars_per_line=8)
        line_height = 26
        start_y = HEIGHT // 2 - (len(lines) * line_height) // 2

        for i, line in enumerate(lines):
            num_surface = number_font.render(line, True, text_color)
            num_rect = num_surface.get_rect(center=(WIDTH // 2, start_y + i * line_height))
            screen.blit(num_surface, num_rect)

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "Navi:OK")

    # --- NEU: MINI-AKTIONSMENÜ ---
    elif phone_state == "dial_actions":
        title = font.render(dialed_number, True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, item in enumerate(dial_actions):
            item_y = 26 + (i * 22)
            if i == dial_actions_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                item_surface = font.render(item, True, bg_color)
            else:
                item_surface = font.render(item, True, text_color)
            screen.blit(item_surface, (6, item_y))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "Navi:OK")

    # --- NEU: ANRUF-PLATZHALTER ---
    elif phone_state == "calling":
        title = font.render("Rufe an...", True, text_color)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 16))
        screen.blit(title, title_rect)

        num_font = pygame.font.Font(None, 24)
        num_surface = num_font.render(dialed_number, True, text_color)
        num_rect = num_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(num_surface, num_rect)

        draw_softkey_hints(screen, hint_font, text_color, "C:Auflegen", "")

    # --- KONTAKT SPEICHERN ---
    elif phone_state == "add_contact":
        title = font.render("Kontakt speichern", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        num_font = pygame.font.Font(None, 20)
        num_surface = num_font.render(dialed_number, True, text_color)
        screen.blit(num_surface, (6, 26))

        name_font = pygame.font.Font(None, 24)
        name_surface = name_font.render(new_contact_name + "_", True, text_color)
        screen.blit(name_surface, (6, 52))

        draw_softkey_hints(screen, hint_font, text_color, "C:Löschen", "Navi:OK")

    # --- KONTAKTLISTE ---
    elif phone_state == "contacts_list":
        title = font.render("Kontakte", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        if not contacts:
            empty_font = pygame.font.Font(None, 18)
            empty_text = empty_font.render("Keine Kontakte", True, text_color)
            screen.blit(empty_text, (6, 30))
        else:
            for i, c in enumerate(contacts):
                item_y = 26 + (i * 20)
                if i == contacts_selected_index:
                    pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                    item_surface = font.render(c["name"], True, bg_color)
                else:
                    item_surface = font.render(c["name"], True, text_color)
                screen.blit(item_surface, (6, item_y))

        draw_softkey_hints(screen, hint_font, text_color, "C:Zurück", "Navi:OK")