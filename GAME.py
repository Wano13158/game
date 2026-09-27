"""Whack-a-beaver.

All game art lives next to this file, so the game can be started from any
working directory with ``python GAME.py``.
"""

from pathlib import Path
from random import choice, randint

import pygame


WIDTH, HEIGHT = 500, 500
FPS = 60
ROUND_SECONDS = 15
WIN_SCORE = 10
ASSETS = Path(__file__).resolve().parent


def load_image(name, size=None):
    """Load an image with transparency and optionally scale it."""
    image = pygame.image.load(str(ASSETS / name)).convert_alpha()
    return pygame.transform.smoothscale(image, size) if size else image


class Sprite:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Beaver:
    """A beaver that rises from one unoccupied hole at a time."""

    def __init__(self, frames):
        self.frames = frames
        self.hole = None
        self.rect = frames[0].get_rect()
        self.visible = False
        self.age = 0.0
        self.duration = 0.0
        self.cooldown = randint(250, 700) / 1000

    def reset(self):
        self.hole = None
        self.visible = False
        self.age = 0.0
        self.cooldown = randint(250, 700) / 1000

    def show(self, hole):
        self.hole = hole
        self.visible = True
        self.age = 0.0
        self.duration = randint(1050, 1650) / 1000
        self.rect.midbottom = (hole.rect.centerx, hole.rect.bottom + 3)

    def update(self, dt, holes, occupied):
        if not self.visible:
            self.cooldown -= dt
            available = [hole for hole in holes if hole not in occupied]
            if self.cooldown <= 0 and available:
                self.show(choice(available))
            return

        self.age += dt
        # The four beaver pictures form a small rising animation.
        frame_index = min(len(self.frames) - 1, int(self.age / 0.12))
        old_bottom = self.rect.bottom
        self.image = self.frames[frame_index]
        self.rect = self.image.get_rect(midbottom=(self.hole.rect.centerx, old_bottom))
        if self.age >= self.duration:
            self.reset()

    def hit(self):
        if not self.visible:
            return False
        self.reset()
        return True

    def draw(self, surface):
        if self.visible:
            super_draw = surface.blit
            super_draw(self.image, self.rect)


class Hammer(Sprite):
    def __init__(self, normal, down):
        super().__init__(0, 0, normal)
        self.normal = normal
        self.down = down
        self.hit_until = 0

    def move_to(self, position):
        self.rect.center = position

    def strike(self, now):
        self.hit_until = now + 110

    def draw(self, surface):
        surface.blit(self.down if pygame.time.get_ticks() < self.hit_until else self.normal, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Клікер-Бобер")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.background = load_image("fon.png", (WIDTH, HEIGHT))
        self.hole_image = load_image("nirka.png", (80, 50))
        self.beaver_frames = [load_image(f"bobr{number}.png") for number in range(5, 9)]
        self.timer_icon = load_image("timer.png", (58, 58))
        self.hammer = Hammer(load_image("molot.png"), load_image("molot_down.png"))
        self.play_button = Sprite(186, 330, load_image("btn.png", (128, 128)))
        self.win_image = load_image("win.png", (128, 128))
        self.lose_image = load_image("lose.png", (128, 128))
        self.font = pygame.font.Font(None, 40)
        self.big_font = pygame.font.Font(None, 46)
        self.holes = self.make_holes()
        self.beavers = [Beaver(self.beaver_frames) for _ in range(3)]
        self.running = True
        self.reset_round()

    def make_holes(self):
        # These positions line up with the three perspective lanes in fon.png.
        positions = ((50, 190), (205, 190), (350, 190),
                     (50, 280), (205, 280), (350, 280),
                     (50, 370), (205, 370), (350, 370))
        return [Sprite(x, y, self.hole_image) for x, y in positions]

    def reset_round(self):
        self.score = 0
        self.time_left = float(ROUND_SECONDS)
        self.finished = False
        pygame.mouse.set_visible(False)
        for beaver in self.beavers:
            beaver.reset()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            self.hammer.move_to(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.finished:
                if self.play_button.rect.collidepoint(event.pos):
                    self.reset_round()
                return
            self.hammer.move_to(event.pos)
            self.hammer.strike(pygame.time.get_ticks())
            for beaver in self.beavers:
                if beaver.visible and self.hammer.rect.colliderect(beaver.rect) and beaver.hit():
                    self.score += 1
                    break

    def update(self, dt):
        if self.finished:
            return
        self.time_left = max(0.0, self.time_left - dt)
        occupied = {beaver.hole for beaver in self.beavers if beaver.visible}
        for beaver in self.beavers:
            beaver.update(dt, self.holes, occupied)
            occupied = {item.hole for item in self.beavers if item.visible}
        if self.time_left == 0:
            self.finished = True
            pygame.mouse.set_visible(True)

    def text(self, value, x, y, color, font=None):
        image = (font or self.font).render(value, True, color)
        self.screen.blit(image, (x, y))

    def draw_hud(self):
        # Icons replace verbose labels and retain the compact layout of the reference.
        self.screen.blit(self.beaver_frames[-1], (10, 8))
        self.text(f":{self.score}", 66, 18, (235, 20, 20))
        self.screen.blit(self.timer_icon, (350, 3))
        self.text(f":{max(0, int(self.time_left + 0.999))}", 410, 18, (235, 20, 20))

    def draw_result(self):
        panel = pygame.Surface((360, 285), pygame.SRCALPHA)
        panel.fill((20, 45, 80, 220))
        self.screen.blit(panel, (70, 105))
        won = self.score >= WIN_SCORE
        result = self.win_image if won else self.lose_image
        self.screen.blit(result, result.get_rect(center=(250, 180)))
        title = self.big_font.render("ПЕРЕМОГА!" if won else "СПРОБУЙ ЩЕ!", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(250, 263)))
        self.text(f"Рахунок: {self.score}", 172, 288, (255, 255, 255), self.font)
        self.play_button.draw(self.screen)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for hole in self.holes:
            hole.draw(self.screen)
        for beaver in self.beavers:
            beaver.draw(self.screen)
        self.draw_hud()
        if self.finished:
            self.draw_result()
        else:
            self.hammer.draw(self.screen)
        pygame.display.flip()

    def run(self):
        pygame.mouse.set_visible(False)
        self.hammer.move_to(pygame.mouse.get_pos())
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
