from pathlib import Path
from random import choice

import pygame as pg


YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 500
HEIGHT = 500
ROUND_SECONDS = 15
WIN_SCORE = 10
ASSETS = Path(__file__).resolve().parent


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Клікер-Шльопа")


def load_image(name, size=None):
    image = pg.image.load(str(ASSETS / name)).convert_alpha()
    return pg.transform.smoothscale(image, size) if size else image


image_bg = load_image("fon.png", (WIDTH, HEIGHT))
image_hole = load_image("nirka.png", (80, 50))
image_shlepa = load_image("bobr8.png")
image_hammer = load_image("molot.png")
image_hammer_down = load_image("molot_down.png")
image_timer = load_image("timer.png", (58, 58))
image_win = load_image("win.png", (128, 128))
image_lose = load_image("lose.png", (128, 128))


class TextLabel:
    def __init__(self, x, y, size=32, color=BLACK):
        self.x = x
        self.y = y
        self.color = color
        self.image = None
        self.font = pg.font.Font(None, size)

    def set_text(self, text):
        self.image = self.font.render(text, True, self.color)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


class Button:
    def __init__(self, x, y, text, w):
        self.rect = pg.Rect(x, y, w, 50)
        self.rect_image = pg.Surface((w, 50))
        self.rect_image.fill(BLUE)
        self.rect_image_active = pg.Surface((w, 50))
        self.rect_image_active.fill(GREEN)
        self.font = pg.font.Font(None, 32)
        self.text_image = self.font.render(text, True, RED)
        self.text_rect = self.text_image.get_rect(center=self.rect.center)
        self.active = False
        self.fn = None

    def update(self):
        self.active = self.rect.collidepoint(pg.mouse.get_pos())

        if self.active and pg.mouse.get_pressed()[0] and self.fn:
            self.fn()

    def draw(self, surface):
        image = self.rect_image_active if self.active else self.rect_image
        surface.blit(image, self.rect)
        surface.blit(self.text_image, self.text_rect)

    def onclick(self, fn):
        self.fn = fn


class Sprite:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = pg.Rect(x, y, image.get_width(), image.get_height())

    def collide(self, sprite):
        return self.rect.colliderect(sprite.rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Shlepa(Sprite):
    def __init__(self, holes):
        super().__init__(0, 0, image_shlepa)
        self.holes = holes
        self.visible = False
        self.next_move = 0

    def show(self):
        hole = choice(self.holes)
        self.rect.midbottom = hole.rect.midbottom
        self.visible = True
        self.next_move = pg.time.get_ticks() + 700

    def update(self):
        if pg.time.get_ticks() >= self.next_move:
            self.show()

    def hit(self):
        if not self.visible:
            return False
        self.visible = False
        self.next_move = pg.time.get_ticks() + 250
        return True

    def draw(self, surface):
        if self.visible:
            super().draw(surface)


class Hammer(Sprite):
    def __init__(self):
        super().__init__(0, 0, image_hammer)
        self.down_until = 0

    def update(self):
        self.rect.center = pg.mouse.get_pos()

    def hit(self):
        self.down_until = pg.time.get_ticks() + 120

    def draw(self, surface):
        image = image_hammer_down if pg.time.get_ticks() < self.down_until else image_hammer
        surface.blit(image, self.rect)


def menu():
    global game_part
    start_button = Button(100, 300, "Почати гру", 300)

    def on_start():
        global game_part
        game_part = "game"

    start_button.onclick(on_start)

    while game_part == "menu":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

        start_button.update()
        screen.blit(image_bg, (0, 0))
        title = pg.font.Font(None, 48).render("КЛІКЕР-ШЛЬОПА", True, WHITE)
        hint = pg.font.Font(None, 30).render("Спіймай 10 Шльоп за 15 секунд!", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 205)))
        start_button.draw(screen)
        pg.display.flip()
        clock.tick(50)


def game():
    global game_part
    holes = [
        Sprite(x, y, image_hole)
        for x, y in ((50, 190), (205, 190), (350, 190),
                     (50, 280), (205, 280), (350, 280),
                     (50, 370), (205, 370), (350, 370))
    ]
    shlepa = Shlepa(holes)
    hammer = Hammer()
    score = 0
    start_time = pg.time.get_ticks()
    score_label = TextLabel(65, 18, 32, RED)
    time_label = TextLabel(410, 18, 32, RED)
    score_label.set_text(":0")
    pg.mouse.set_visible(False)

    while game_part == "game":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                hammer.hit()
                if hammer.collide(shlepa) and shlepa.hit():
                    score += 1
                    score_label.set_text(f":{score}")

        seconds_left = ROUND_SECONDS - (pg.time.get_ticks() - start_time) // 1000
        if score >= WIN_SCORE:
            game_part = "victory"
            break
        if seconds_left <= 0:
            game_part = "gameover"
            break

        shlepa.update()
        hammer.update()
        time_label.set_text(f":{seconds_left}")

        screen.blit(image_bg, (0, 0))
        shlepa.draw(screen)
        for hole in holes:
            hole.draw(screen)
        screen.blit(image_shlepa, (10, 8))
        screen.blit(image_timer, (350, 3))
        score_label.draw(screen)
        time_label.draw(screen)
        hammer.draw(screen)
        pg.display.flip()
        clock.tick(50)

    pg.mouse.set_visible(True)


def victory():
    global game_part
    font = pg.font.Font(None, 48)
    img = font.render("Перемога", True, WHITE)
    menu_button = Button(100, 350, "Меню", 300)

    def on_menu():
        global game_part
        game_part = "menu"

    menu_button.onclick(on_menu)

    while game_part == "victory":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
        menu_button.update()
        screen.blit(image_bg, (0, 0))
        screen.blit(image_win, image_win.get_rect(center=(250, 160)))
        screen.blit(img, img.get_rect(center=(250, 270)))
        menu_button.draw(screen)
        pg.display.flip()
        clock.tick(50)


def gameover():
    global game_part
    font = pg.font.Font(None, 48)
    img = font.render("Програш", True, WHITE)
    menu_button = Button(100, 350, "Меню", 300)

    def on_menu():
        global game_part
        game_part = "menu"

    menu_button.onclick(on_menu)

    while game_part == "gameover":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
        menu_button.update()
        screen.blit(image_bg, (0, 0))
        screen.blit(image_lose, image_lose.get_rect(center=(250, 160)))
        screen.blit(img, img.get_rect(center=(250, 270)))
        menu_button.draw(screen)
        pg.display.flip()
        clock.tick(50)


game_part = "menu"
clock = pg.time.Clock()


while True:
    if game_part == "menu":
        menu()
    elif game_part == "game":
        game()
    elif game_part == "victory":
        victory()
    elif game_part == "gameover":
        gameover()
