import os
import json
import pygame
import fonts

# --- GPS FÜR DIE JSON-DATEI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "contacts.json")

# --- 1. FUNKTIONEN ZUM SPEICHERN/LADEN ---
def load_contacts():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Hier sortiert die Kiste direkt alles von A bis Z durch
            data.sort(key=lambda x: x["name"].lower())
            return data
    except FileNotFoundError:
        return []

def save_contacts(contacts_list):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts_list, f, ensure_ascii=False, indent=4)


# --- 2. ZUSTÄNDE ---
phone_state = "sub_menu"
phone_menu_items = ["Nummer wählen", "Kontakte", "Anrufliste"]
phone_selected_index = 0
dialed_number = ""

dial_actions = ["Anrufen", "Kontakt speichern", "Löschen"]
dial_actions_index = 0

contact_actions = ["Anrufen", "Bearbeiten", "Löschen"]
contact_actions_index = 0

contacts = load_contacts()
contacts_selected_index = 0
contact_search_query = ""
new_contact_name = ""
new_contact_number = ""
editing_contact_index = None

exit_to_menu = False

NAVI_UP = pygame.K_UP
NAVI_DOWN = pygame.K_DOWN
NAVI_SELECT = (pygame.K_RETURN, pygame.K_KP_ENTER)
C_KEY = pygame.K_BACKSPACE


def reset():
    global phone_state, phone_selected_index, dialed_number, exit_to_menu, contact_search_query
    phone_state = "sub_menu"
    phone_selected_index = 0
    dialed_number = ""
    contact_search_query = ""
    exit_to_menu = False


def handle_event(event):
    global phone_state, phone_selected_index, dialed_number, exit_to_menu
    global dial_actions_index, contact_actions_index
    global contacts, contacts_selected_index, contact_search_query
    global new_contact_name, new_contact_number, editing_contact_index

    if event.type != pygame.KEYDOWN:
        return

    exit_to_menu = False

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
                contact_search_query = ""
        elif event.unicode.isnumeric():
            phone_state = "dialing"
            dialed_number = event.unicode
        elif event.key == C_KEY:
            exit_to_menu = True

    elif phone_state == "dialing":
        if event.unicode.isnumeric() or event.unicode in ("*", "#"):
            dialed_number += event.unicode
        elif event.key == C_KEY:
            if dialed_number:
                dialed_number = dialed_number[:-1]
            else:
                phone_state = "sub_menu"
        elif event.key in NAVI_SELECT:
            if dialed_number:
                phone_state = "dial_actions"
                dial_actions_index = 0

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

    elif phone_state == "calling":
        if event.key == C_KEY or event.key in NAVI_SELECT:
            phone_state = "sub_menu"
            dialed_number = ""

    elif phone_state == "add_contact":
        if event.key in NAVI_SELECT:
            if new_contact_name.strip():
                clean_name = new_contact_name.strip()
                
                existing_idx = None
                for idx, c in enumerate(contacts):
                    if c["number"] == dialed_number:
                        existing_idx = idx
                        break
                
                if existing_idx is not None:
                    contacts[existing_idx]["name"] = clean_name
                else:
                    contacts.append({"name": clean_name, "number": dialed_number})
                
                save_contacts(contacts)
            phone_state = "sub_menu"
        elif event.key == C_KEY:
            if new_contact_name:
                new_contact_name = new_contact_name[:-1]
            else:
                phone_state = "dial_actions"
        elif event.unicode and event.unicode.isprintable():
            if len(new_contact_name) < 20:
                new_contact_name += event.unicode

    elif phone_state == "contacts_list":
        if event.key == NAVI_UP and contacts:
            contacts_selected_index = (contacts_selected_index - 1) % len(contacts)
        elif event.key == NAVI_DOWN and contacts:
            contacts_selected_index = (contacts_selected_index + 1) % len(contacts)
        elif event.key in NAVI_SELECT:
            if contacts:
                phone_state = "contact_detail"
                contact_actions_index = 0
        elif event.key == C_KEY:
            phone_state = "sub_menu"
        elif event.unicode and event.unicode.isprintable():
            char = event.unicode.lower()
            if contacts:
                # Nokia-Style: Suche ab dem nächsten Index nach einem Treffer, springe und cycle durch
                start_search = (contacts_selected_index + 1) % len(contacts)
                found_idx = -1
                for i in range(len(contacts)):
                    idx = (start_search + i) % len(contacts)
                    if contacts[idx]["name"].lower().startswith(char):
                        found_idx = idx
                        break
                if found_idx != -1:
                    contacts_selected_index = found_idx

    elif phone_state == "contact_detail":
        if event.key == NAVI_UP:
            contact_actions_index = (contact_actions_index - 1) % len(contact_actions)
        elif event.key == NAVI_DOWN:
            contact_actions_index = (contact_actions_index + 1) % len(contact_actions)
        elif event.key == C_KEY:
            phone_state = "contacts_list"
        elif event.key in NAVI_SELECT:
            chosen = contact_actions[contact_actions_index]
            if chosen == "Anrufen":
                dialed_number = contacts[contacts_selected_index]["number"]
                phone_state = "calling"
            elif chosen == "Bearbeiten":
                editing_contact_index = contacts_selected_index
                new_contact_name = contacts[contacts_selected_index]["name"]
                new_contact_number = contacts[contacts_selected_index]["number"]
                phone_state = "edit_contact_name"
            elif chosen == "Löschen":
                del contacts[contacts_selected_index]
                save_contacts(contacts)
                if contacts_selected_index >= len(contacts):
                    contacts_selected_index = max(0, len(contacts) - 1)
                phone_state = "contacts_list"

    elif phone_state == "edit_contact_name":
        if event.key in NAVI_SELECT:
            if new_contact_name.strip() and editing_contact_index is not None:
                phone_state = "edit_contact_number"
        elif event.key == C_KEY:
            if new_contact_name:
                new_contact_name = new_contact_name[:-1]
            else:
                phone_state = "contact_detail"
        elif event.unicode and event.unicode.isprintable():
            if len(new_contact_name) < 20:
                new_contact_name += event.unicode

    elif phone_state == "edit_contact_number":
        if event.key in NAVI_SELECT:
            if new_contact_number.strip() and editing_contact_index is not None:
                contacts[editing_contact_index]["name"] = new_contact_name.strip()
                contacts[editing_contact_index]["number"] = new_contact_number.strip()
                save_contacts(contacts)
            phone_state = "contacts_list"
            editing_contact_index = None
        elif event.key == C_KEY:
            if new_contact_number:
                new_contact_number = new_contact_number[:-1]
            else:
                phone_state = "edit_contact_name"
        elif event.unicode.isnumeric() or event.unicode in ("*", "#"):
            if len(new_contact_number) < 20:
                new_contact_number += event.unicode


def wrap_number(number, chars_per_line=8):
    if not number:
        return [""]
    return [number[i:i + chars_per_line] for i in range(0, len(number), chars_per_line)]


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
    screen.fill(bg_color)
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    if phone_state == "sub_menu":
        screen.blit(fonts.render("Telefon", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, item in enumerate(phone_menu_items):
            item_y = 26 + (i * 22)
            if i == phone_selected_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                surf = fonts.render(item, 20, bg_color)
            else:
                surf = fonts.render(item, 20, text_color)
            screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")

    elif phone_state == "dialing":
        screen.blit(fonts.render("Nummer wählen", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        lines = wrap_number(dialed_number, chars_per_line=8)
        line_height = 26
        start_y = HEIGHT // 2 - (len(lines) * line_height) // 2
        for i, line in enumerate(lines):
            num_surface = fonts.render(line, 28, text_color)
            num_rect = num_surface.get_rect(center=(WIDTH // 2, start_y + i * line_height))
            screen.blit(num_surface, num_rect)

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")

    elif phone_state == "dial_actions":
        screen.blit(fonts.render(dialed_number, 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        for i, item in enumerate(dial_actions):
            item_y = 26 + (i * 22)
            if i == dial_actions_index:
                pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                surf = fonts.render(item, 20, bg_color)
            else:
                surf = fonts.render(item, 20, text_color)
            screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")

    elif phone_state == "calling":
        title = fonts.render("Rufe an...", 20, text_color)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 16))
        screen.blit(title, title_rect)

        display_text = dialed_number
        for c in contacts:
            if c["number"] == dialed_number:
                display_text = c["name"]
                break

        num_surface = fonts.render(display_text, 24, text_color)
        num_rect = num_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(num_surface, num_rect)

        draw_softkey_hints(screen, text_color, "C:Auflegen", "")

    elif phone_state == "add_contact":
        screen.blit(fonts.render("Kontakt speichern", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        screen.blit(fonts.render(dialed_number, 20, text_color), (6, 26))
        screen.blit(fonts.render(new_contact_name + "_", 24, text_color), (6, 52))

        draw_softkey_hints(screen, text_color, "C:Löschen", "Navi:OK")

    elif phone_state == "contacts_list":
        screen.blit(fonts.render("Kontakte", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

        if not contacts:
            screen.blit(fonts.render("Keine Kontakte", 18, text_color), (6, 30))
        else:
            MAX_VISIBLE = 6
            start_idx = 0
            if contacts_selected_index > 5:
                start_idx = contacts_selected_index - 5
                
            if start_idx > max(0, len(contacts) - MAX_VISIBLE):
                start_idx = max(0, len(contacts) - MAX_VISIBLE)

            for i in range(start_idx, min(len(contacts), start_idx + MAX_VISIBLE)):
                item_y = 22 + ((i - start_idx) * 20)
                
                if i == contacts_selected_index:
                    pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                    surf = fonts.render(contacts[i]["name"], 20, bg_color)
                else:
                    surf = fonts.render(contacts[i]["name"], 20, text_color)
                screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:Aktion")

    elif phone_state == "contact_detail":
        if contacts:
            c = contacts[contacts_selected_index]
            screen.blit(fonts.render("Kontakte", 20, text_color), (4, 4))
            pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)

            screen.blit(fonts.render(c["name"] + ":", 22, text_color), (6, 24))
            screen.blit(fonts.render(c["number"], 18, text_color), (6, 48))
            pygame.draw.line(screen, text_color, (0, 68), (WIDTH, 68), 2)

            for i, item in enumerate(contact_actions):
                item_y = 73 + (i * 20)
                if i == contact_actions_index:
                    pygame.draw.rect(screen, text_color, (2, item_y - 2, WIDTH - 4, 18))
                    surf = fonts.render(item, 20, bg_color)
                else:
                    surf = fonts.render(item, 20, text_color)
                screen.blit(surf, (6, item_y))

        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")

    elif phone_state == "edit_contact_name":
        screen.blit(fonts.render("Name aendern", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)
        screen.blit(fonts.render(new_contact_name + "_", 24, text_color), (6, 40))
        draw_softkey_hints(screen, text_color, "C:Löschen", "Navi:OK")

    elif phone_state == "edit_contact_number":
        screen.blit(fonts.render("Nr. aendern", 20, text_color), (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)
        screen.blit(fonts.render(new_contact_number + "_", 24, text_color), (6, 40))
        draw_softkey_hints(screen, text_color, "C:Zurück", "Navi:OK")