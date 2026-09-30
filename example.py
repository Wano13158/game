import pygame as pg


YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


WIDTH = 500
HEIGHT = 500


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))


# завантаження картинок


image_ball = pg.image.load("Ball.png").convert_alpha()


image_block1 = pg.image.load("Block1.png").convert_alpha()
image_block2 = pg.image.load("Block2.png").convert_alpha()
image_block3 = pg.image.load("Block3.png").convert_alpha()


image_platform1 = pg.image.load("Platform1.png").convert_alpha()
image_platform2 = pg.image.load("Platform2.png").convert_alpha()
image_platform3 = pg.image.load("Platform3.png").convert_alpha()


image_bg = pg.image.load("background.png").convert()




#####################################
#    елементи з попередніх уроків   #
#####################################




class TextLabel:
    # Текстова позначка
    def __init__(self, x, y, size=32, color=BLACK):
        self.x = x
        self.y = y
        self.color = color
        self.image = None
        self.font = pg.font.Font(None, size)


    def set_text(self, text):
        self.image = self.font.render(text, True, self.color)


    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))




class Button():
    # з попереднього проєкту
    def __init__(self, x, y, text, w):
        self.rect = pg.Rect(x, y, w, 50)
        self.rect_image = pg.Surface((w, 50))
        self.rect_image.fill(BLUE)
        self.rect_image_active = pg.Surface((w, 50))
        self.rect_image_active.fill(GREEN)
        self.font = pg.font.Font(None, 32)
        self.text_image = self.font.render(text, True, RED)
        self.text_rect = self.text_image.get_rect()
        self.text_rect.x = self.rect.x + 20
        self.text_rect.y = y+5
        self.active = False
        self.fn = None


    def update(self):
        x, y = pg.mouse.get_pos()
        collision = self.rect.collidepoint(x, y)
        if collision:
            self.active = True
            click = pg.mouse.get_pressed()[0]
            if click and self.fn:
                self.fn()
        else:
            self.active = False


    def draw(self, surface):
        if self.active:
            surface.blit(self.rect_image, (self.rect.x, self.rect.y))
        else:
            surface.blit(self.rect_image_active, (self.rect.x, self.rect.y))
        surface.blit(self.text_image, (self.text_rect.x, self.text_rect.y))


    def onclick(self, fn):
        self.fn = fn




#####################################
#          ігрові класи             #
#####################################
class Sprite:
    # базовий клас для спадкування класами гри
    def __init__(self, x, y, image):
        self.image = image
        self.rect = pg.Rect(x, y, self.image.get_width(),
                            self.image.get_height())


    def collide(self, sprite):
        return self.rect.colliderect(sprite.rect)


    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))




class Player(Sprite):
    # клас гравця
    def __init__(self, x, y, image_base, image_right, image_left):
        self.image_base = image_base
        self.image_left = image_left
        self.image_right = image_right
        self.dir = "stop"
        super().__init__(x, y, image_base)


    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.rect.left -= 8
            self.image = self.image_left
            self.dir = "left"
        elif keys[pg.K_RIGHT]:
            self.rect.left += 8
            self.image = self.image_right
            self.dir = "right"
        else:
            self.image = self.image_base
            self.dir = "stop"




class Ball(Sprite):
    # клас м'яча
    def __init__(self, x, y, image, velocity):


        self.base_image = image


        super().__init__(x, y, image)


        self.SPEED = velocity


        self.velocityx = velocity
        self.velocityy = -velocity
        self.angle = 0
        self.dir = "stop"


    def update(self):
        self.rect.left += self.velocityx
        self.rect.top += self.velocityy


        if self.dir == "right":
            self.angle += 10
            self.image = pg.transform.rotate(self.base_image, self.angle)
        elif self.dir == "left":
            self.angle -= 10
            self.image = pg.transform.rotate(self.base_image, self.angle)


            # обмеження кута 0 - 360
            if self.angle > 360:
                self.angle -= 360
            if self.angle < 0:
                self.angle += 360


        if self.rect.left < 0:
            self.velocityx = -self.velocityx
        if self.rect.right > WIDTH:
            self.velocityx = -self.velocityx


        if self.rect.top < 0:
            self.velocityy = self.SPEED
        if self.rect.bottom > HEIGHT:
            self.velocityy = -self.SPEED


    def change_velocity(self, player):
        self.velocityy = -self.SPEED
        self.dir = player.dir


        if player.dir == "right":
            self.velocityx += 2


        elif player.dir == "left":
            self.velocityx -= 2


        if self.velocityx < -6:
            self.velocityx = -6
        if self.velocityx > 6:
            self.velocityx = 6




#####################################
#    ігрові об'єкти та цикл         #
#####################################
def menu():
    global running
    start_button = Button(100, 200, "Почати гру", 300)


    def on_start():
        global game_part
        game_part = "game"


    start_button.onclick(on_start)


    while game_part == "menu":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        start_button.update()
        screen.fill(WHITE)
        start_button.draw(screen)
        # оновлення дисплея
        pg.display.flip()
        clock.tick(50)


###########################################
# сама гра
def game():
    global game_part
    ball = Ball(100, HEIGHT//2, image_ball, 4)


    player = Player(WIDTH//2 - 50, HEIGHT - 60, image_platform1,
                    image_platform2, image_platform3)


    score = 0
    label = TextLabel(370, 470, 28)
    label.set_text(f"Score: {score}")


    blocks = []


    for i in range(15):
        row = i//5
        col = i % 5


        blocks.append(Sprite(50 + col*80, 20 + row*40,
                    [image_block1, image_block2, image_block3][row]))


    clock = pg.time.Clock()




    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()


        ball.update()
        player.update()


        if player.collide(ball):
            ball.change_velocity(player)


        screen.blit(image_bg, (0, 0))


        for b in blocks:
            if b.collide(ball):
                ball.velocityy = ball.SPEED
                blocks.remove(b)
                score += 100
                label.set_text(f"Score: {score}")


        for b in blocks:
            b.draw(screen)
       
        # умови виграшу та програшу    
        if not len(blocks):
            game_part = "victory"
            return


        if ball.rect.y > player.rect.y:
            game_part = "gameover"
            return


        ball.draw(screen)
        label.draw(screen)
        player.draw(screen)




        pg.display.flip()


        clock.tick(50)


# меню перемоги
def victory():
    global game_part
    font = pg.font.Font(None, 48)
    img = font.render("Перемога", True, WHITE)
    menu_button = Button(100, 300, "Меню", 300)


    def on_menu():
        global game_part
        game_part = "menu"


    menu_button.onclick(on_menu)


    while game_part == "victory":
        menu_button.update()
        screen.fill(GREEN)
        screen.blit(img, (150, 100))
        menu_button.draw(screen)
        # оновлення дисплея
        pg.display.flip()


        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        clock.tick(50)




#  меню програшу
def gameover():
    global game_part
    font = pg.font.Font(None, 48)
    img = font.render("Програш", True, WHITE)
    menu_button = Button(100, 300, "Меню", 300)


    def on_menu():
        global game_part
        game_part = "menu"


    menu_button.onclick(on_menu)


    while game_part == "gameover":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        menu_button.update()
        screen.fill(RED)
        screen.blit(img, (150, 100))
        menu_button.draw(screen)
        # оновлення дисплея
        pg.display.flip()
        clock.tick(50)




game_part = "menu"
clock = pg.time.Clock()




# цикл з вибором меню
while True:
    if game_part == "menu":
        menu()
    elif game_part == "game":
        game()
    elif game_part == "victory":
        victory()
    elif game_part == "gameover":
        gameover()




pg.quit()






