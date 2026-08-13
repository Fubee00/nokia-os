import os
import pygame

# Pfad relativ zum Projekt-Root, wo main.py liegt
FONT_PATH = os.path.join("assets", "fonts", "nokiafc22.ttf")

# Cache, damit wir nicht bei jedem Aufruf die Datei neu von der Platte laden
_font_cache = {}
_font_available = None  # None = noch nicht geprüft


def load_font(size):
    """Lädt den Nokia-Bitmap-Font in der gewünschten Größe.
    Fällt automatisch auf Pygames Standardfont zurück, falls die
    .ttf-Datei (noch) fehlt, statt einfach zu crashen."""
    global _font_available

    if size in _font_cache:
        return _font_cache[size]

    if _font_available is None:
        _font_available = os.path.isfile(FONT_PATH)
        if not _font_available:
            print(f"[fonts.py] Achtung: {FONT_PATH} nicht gefunden, "
                  f"nutze Pygame-Standardfont als Fallback.")

    if _font_available:
        font = pygame.font.Font(FONT_PATH, size)
    else:
        font = pygame.font.Font(None, size)

    _font_cache[size] = font
    return font


def render(text, font_size, color):
    """Kurzform: Text rendern OHNE Antialiasing.
    Bei einem Bitmap-Font wie nokiafc22 würde Antialiasing die eigentlich
    schon pixelgenauen Kanten wieder weichzeichnen -> deshalb hier fest
    auf False statt es an jeder Render-Stelle einzeln zu vergessen."""
    font = load_font(font_size)
    return font.render(text, False, color)