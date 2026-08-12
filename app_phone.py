import pygame

phone_state = "sub_menu"  # sub_menu, dialing, add_contact, contacts_list
phone_menu_items = ["Nummer wählen", "Kontakte", "Anrufliste"]
phone_selected_index = 0
dialed_number = ""

# --- NEU: Kontakte-Speicher (erstmal im RAM, kein Save-File) ---
contacts = []  # Liste von {"name": ..., "number": ...}
contacts_selected_index = 0
new_contact_name = ""


def reset():
    global phone_state, phone_selected_index, dialed_number
    phone_state = "sub_menu"
    phone_selected_index = 0
    dialed_number = ""


def handle_event(event):
    global phone_state, phone_selected_index, dialed_number
    global contacts, contacts_selected_index, new_contact_name

    if event.type != pygame.KEYDOWN:
        return

    # --- HAUPT-UNTERMENÜ ---
    if phone_state == "sub_menu":
        if event.key == pygame.K_UP:
            phone_selected_index = (phone_selected_index - 1) % len(phone_menu_items)
        elif event.key == pygame.K_DOWN:
            phone_selected_index = (phone_selected_index + 1) % len(phone_menu_items)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
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
        if event.unicode.isnumeric():
            dialed_number += event.unicode
        elif event.key == pygame.K_BACKSPACE:
            dialed_number = dialed_number[:-1]
        elif event.key == pygame.K_ESCAPE:
            phone_state = "sub_menu"
        elif event.key == pygame.K_TAB:
            # Softkey-Platzhalter: "Kontakt hinzufügen"
            # (auf echter Hardware später an eine feste Taste/Softkey binden)
            if dialed_number:
                phone_state = "add_contact"
                new_contact_name = ""

    # --- NEU: KONTAKT SPEICHERN (Name eintippen) ---
    elif phone_state == "add_contact":
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if new_contact_name.strip():
                contacts.append({"name": new_contact_name.strip(), "number": dialed_number})
            phone_state = "sub_menu"
        elif event.key == pygame.K_BACKSPACE:
            new_contact_name = new_contact_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            phone_state = "dialing"
        elif event.unicode and event.unicode.isprintable():
            if len(new_contact_name) < 20:
                new_contact_name += event.unicode

    # --- NEU: KONTAKTLISTE ANZEIGEN/AUSWÄHLEN ---
    elif phone_state == "contacts_list":
        if event.key == pygame.K_UP and contacts:
            contacts_selected_index = (contacts_selected_index - 1) % len(contacts)
        elif event.key == pygame.K_DOWN and contacts:
            contacts_selected_index = (contacts_selected_index + 1) % len(contacts)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if contacts:
                dialed_number = contacts[contacts_selected_index]["number"]
                phone_state = "dialing"
        elif event.key == pygame.K_ESCAPE:
            phone_state = "sub_menu"


def wrap_number(number, chars_per_line=8):
    """Bricht lange Nummern in mehrere Zeilen um, damit nichts vom
    kleinen Display abgeschnitten wird."""
    if not number:
        return [""]
    return [number[i:i + chars_per_line] for i in range(0, len(number), chars_per_line)]


def draw_screen(screen, font, text_color, bg_color):
    screen.fill(bg_color)
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

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

        info_font = pygame.font.Font(None, 16)
        info_text = info_font.render("[Enter] Auswählen", True, text_color)
        screen.blit(info_text, (6, HEIGHT - 14))

    # --- ANSICHT 2: NUMMER EINTIPPEN (jetzt mit Zeilenumbruch) ---
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

        back_font = pygame.font.Font(None, 16)
        back_text = back_font.render("[ESC] Zurück [Tab] +Kontakt", True, text_color)
        screen.blit(back_text, (4, HEIGHT - 14))

    # --- NEU: ANSICHT 3: KONTAKT SPEICHERN ---
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

        info_font = pygame.font.Font(None, 16)
        info_text = info_font.render("[Enter] Speichern [ESC] Abbr.", True, text_color)
        screen.blit(info_text, (6, HEIGHT - 14))

    # --- NEU: ANSICHT 4: KONTAKTLISTE ---
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

        info_font = pygame.font.Font(None, 16)
        info_text = info_font.render("[Enter] Wählen [ESC] Zurück", True, text_color)
        screen.blit(info_text, (6, HEIGHT - 14))