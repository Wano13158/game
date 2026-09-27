import pygame
pygame.init()
from random import randint, choice
pygame.font.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Клікер-Бобер")
fon = pygame.image.load('fon.png')
clock = pygame.time.Clock()

class Sprite:
    def __init__(self, x, y, w, h, img):
        loaded_img = pygame.image.load(img)
        self.img = pygame.transform.scale(loaded_img, (w, h))
        self.rect = pygame.Rect(x, y, w, h)
        
    def draw(self, surface):
        surface.blit(self.img, (self.rect.x, self.rect.y))

class Mink(Sprite):
    pass

class Bobr(Sprite):
    def __init__(self, x, y, w, h, img):
        super().__init__(x, y, w, h, img)
        self.visible = False
        self.timer = 0
        self.original_y = y
        self.target_mink = None

    def random_mink(self, minks_list):
        if not self.visible:
            self.target_mink = choice(minks_list)
            self.rect.x = self.target_mink.rect.x + (self.target_mink.rect.width - self.rect.width) // 2
            self.original_y = self.target_mink.rect.y
            self.rect.y = self.original_y
            
            if randint(1, 35) == 1:
                self.visible = True
                self.timer = randint(30, 60)

    def anim_bobr(self):    
        if self.visible:
            if self.rect.y > self.original_y - self.rect.height:
                self.rect.y -= 4
            self.timer -= 1
            if self.timer <= 0:
                self.visible = False
        else:
            if self.rect.y < self.original_y:
                self.rect.y += 4

class Molot(Sprite):
    def __init__(self, x, y, w, h, img, img_down):
        super().__init__(x, y, w, h, img)
        self.img_normal = self.img
        loaded_hit = pygame.image.load(img_down)
        self.img_hit = pygame.transform.scale(loaded_hit, (w, h))
        self.is_hit = False
        self.hit_timer = 0

    def update(self, event, bobrs_list, score_counter):
        if event.type == pygame.MOUSEMOTION:
            self.rect.x = event.pos[0] - self.rect.width // 2
            self.rect.y = event.pos[1] - self.rect.height // 2
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_hit = True
            self.img = self.img_hit
            self.hit_timer = 8
            
            for bobr in bobrs_list:
                if bobr.visible and self.rect.colliderect(bobr.rect):
                    bobr.visible = False
                    bobr.rect.y = bobr.original_y
                    score_counter[0] += 1

    def draw(self, surface):
        if self.is_hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.is_hit = False
                self.img = self.img_normal
        surface.blit(self.img, (self.rect.x, self.rect.y))
       
class Label:
    def __init__(self, x, y, text, font_size=30, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.color = color

    def draw(self, surface, current_text=""):
        text_img = self.font.render(self.text + str(current_text), True, self.color)
        surface.blit(text_img, (self.x, self.y))

minks = []
x, y = 50, 150
for _ in range(3):
    for _ in range(3):
         minks.append(Mink(x, y, 80, 50, "nirka.png"))
         x += 140
    x = 50
    y += 110

bobrs = [Bobr(0, 0, 60, 60, "bobr5.png") for _ in range(3)]
molot = Molot(250, 250, 60, 60, "molot.png", "molot_down.png")

score = [0]
score_label = Label(30, 20, "Очки: ", 36, (50, 200, 50))
game_time = 30 * 40
time_label = Label(320, 20, "Час: ", 36, (200, 50, 50))

pygame.mouse.set_visible(False)
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        molot.update(event, bobrs, score)

    if game_time > 0:
        game_time -= 1
        for bobr in bobrs:
            bobr.random_mink(minks)
            bobr.anim_bobr()

    screen.blit(fon, (0, 0))
    
    for mink in minks:
        mink.draw(screen)
        
    for bobr in bobrs:
        bobr.draw(screen)
    
    molot.draw(screen)

    score_label.draw(screen, score[0])
    time_label.draw(screen, max(0, game_time // 40))

    if game_time <= 0:
        game_over_label = Label(130, 220, "ГРА ЗАВЕРШЕНА!", 45, (255, 0, 0))
        game_over_label.draw(screen, "")

    pygame.display.flip()
    clock.tick(40)

pygame.mouse.set_visible(True)
pygame.quit()