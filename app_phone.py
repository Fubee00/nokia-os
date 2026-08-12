import pygame

phone_state = "sub_menu"
phone_menu_items = ["Nummer wählen", "Kontakte", "Anrufliste"]
phone_selected_index = 0
dialed_number = ""

def reset():
    global phone_state, phone_selected_index, dialed_number
    phone_state = "sub_menu"
    phone_selected_index = 0
    dialed_number = ""

def handle_event(event):
    global phone_state, phone_selected_index, dialed_number
    
    if event.type == pygame.KEYDOWN:
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
            
            # --- NEU: DIREKT EINTIPPEN IM UNTERMENÜ ---
            elif event.unicode.isnumeric():
                phone_state = "dialing"  # Sofort in den Wählmodus springen
                dialed_number = event.unicode  # Die gedrückte Zahl direkt als Start nehmen

        elif phone_state == "dialing":
            if event.unicode.isnumeric():
                dialed_number += event.unicode
            elif event.key == pygame.K_BACKSPACE:
                dialed_number = dialed_number[:-1]
            elif event.key == pygame.K_ESCAPE:
                phone_state = "sub_menu"

def draw_screen(screen, font, text_color, bg_color):
    screen.fill(bg_color)
    
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    # --- ANSICHT 1: DAS TELEFON-UNTERMENÜ ---
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

    # --- ANSICHT 2: NUMMER EINTIPPEN ---
    elif phone_state == "dialing":
        title = font.render("Nummer wählen", True, text_color)
        screen.blit(title, (4, 4))
        pygame.draw.line(screen, text_color, (0, 18), (WIDTH, 18), 2)
        
        number_font = pygame.font.Font(None, 32)
        num_surface = number_font.render(dialed_number, True, text_color)
        num_rect = num_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(num_surface, num_rect)

        back_font = pygame.font.Font(None, 16)
        back_text = back_font.render("[ESC] Zurück", True, text_color)
        screen.blit(back_text, (4, HEIGHT - 14))