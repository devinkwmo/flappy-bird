import random
import sys

import pygame

pygame.init()

WIN_WIDTH = 288
WIN_HEIGHT = 512

BIRD_IMG = [pygame.image.load('images/bird1.png'),
            pygame.image.load('images/bird2.png'),
            pygame.image.load('images/bird3.png'),
            pygame.image.load('images/bird4.png')]
SCORE_IMG = [pygame.image.load('images/0.png'),
             pygame.image.load('images/1.png'),
             pygame.image.load('images/2.png'),
             pygame.image.load('images/3.png'),
             pygame.image.load('images/4.png'),
             pygame.image.load('images/5.png'),
             pygame.image.load('images/6.png'),
             pygame.image.load('images/7.png'),
             pygame.image.load('images/8.png'),
             pygame.image.load('images/9.png')]
BG_IMG = pygame.image.load('images/bg.png')
BASE_IMG = pygame.image.load('images/base.png')
PIPE_IMG = pygame.image.load('images/pipe.png')
MSG_IMG = pygame.image.load('images/message.png')
GG_IMG = pygame.image.load('images/gameover.png')
SFX = {'flap': pygame.mixer.Sound('audio/wing.wav'), 'point': pygame.mixer.Sound('audio/point.wav'),
       'hit': pygame.mixer.Sound('audio/hit.wav'), 'die': pygame.mixer.Sound('audio/die.wav')}


class Bird:
    # sprite dimensions, for hit-box purposes
    WIDTH = BIRD_IMG[0].get_width()
    HEIGHT = BIRD_IMG[0].get_height()

    X = WIN_WIDTH // 5
    MAX_VEL = 10  # maximum descent
    MIN_VEL = -8  # maximum ascent
    GRAVITY = 1  # acceleration due to gravity
    ROT_VEL = 3  # sprite rotation speed
    ROT_MAX = 20  # sprite rotation threshold (CCW)
    FLAP_ACC = -9  # upward acceleration when flapping

    def __init__(self, y):
        self.y = y

        # used to which sprite to use
        self.flap_counter = 0
        self.img = BIRD_IMG[0]
        self.rot = 0

        # used to determine movement of bird
        self.vel = -9
        self.is_flapping = False

    def draw(self, surface):
        # determine which sprite to use
        self.flap_counter += 1
        if self.flap_counter == 20:
            self.flap_counter = 0
        self.img = BIRD_IMG[self.flap_counter // 5]

        # determine rotation
        rot_display = self.rot if self.rot < self.ROT_MAX else self.ROT_MAX
        player = pygame.transform.rotate(self.img, rot_display)

        # display bird on surface with correct height and rotation
        surface.blit(player, (self.X, self.y))

    def flap(self):
        self.vel = self.FLAP_ACC
        self.is_flapping = True

    def move(self):
        # if not clicked, accelerate downwards
        if not self.is_flapping and self.vel < self.MAX_VEL:
            self.vel += self.GRAVITY

        # if clicked, set sprite rotation to 45 and change is_flapping to False
        if self.is_flapping:
            self.is_flapping = False
            self.rot = 45

        # fall by one velocity unit
        # unless it would result in being below the ground
        self.y += min(self.vel, ground.Y - self.y - bird.HEIGHT)

        # if rotation more than -90 deg, rotate towards ground by one rotational velocity unit
        if self.rot > -90:
            self.rot -= self.ROT_VEL

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Ground:
    """Represents the ground, oversees its movement (infinite scrolling)."""
    VEL = -5
    Y = 410

    def __init__(self):
        self.x1 = 0
        self.x2 = BG_IMG.get_width()

    def move(self):
        self.x1 += self.VEL
        self.x2 += self.VEL

    def draw(self, surface):
        # illusion of scrolling ground
        if self.x1 < -BG_IMG.get_width():
            self.x1 = BG_IMG.get_width()
        if self.x2 < -BG_IMG.get_width():
            self.x2 = BG_IMG.get_width()
        surface.blit(BASE_IMG, (self.x1, self.Y))
        surface.blit(BASE_IMG, (self.x2, self.Y))


class Pipe:
    """Each Pipe object constitutes both an upper and lower pipe."""
    GAP = 100
    PIPE_VEL = -5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.passed = False
        self.top = 0
        self.bot = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOT = PIPE_IMG

        self.set_height()

    def set_height(self):
        # pipes are given random positions
        self.height = random.randrange(0, int(ground.Y * 0.6 - self.GAP)) + int(ground.Y * 0.2)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bot = self.height + self.GAP

    def move(self):
        self.x += self.PIPE_VEL

    def draw(self, surface):
        # draws a pipe pair
        surface.blit(self.PIPE_TOP, (self.x, self.top))
        surface.blit(self.PIPE_BOT, (self.x, self.bot))

    def collide(self, player):
        # if bird and pipe masks overlap, register a collision and return True
        obj_mask = player.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bot_mask = pygame.mask.from_surface(self.PIPE_BOT)

        top_offset = (self.x - player.X, self.top - round(player.y))
        bot_offset = (self.x - player.X, self.bot - round(player.y))

        t_point = obj_mask.overlap(top_mask, top_offset)
        b_point = obj_mask.overlap(bot_mask, bot_offset)

        if t_point or b_point:
            return True

        return False


def redraw():
    """Draws BG, all pipes, ground, and bird (in that order)."""
    WIN.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(WIN)

    ground.draw(WIN)
    bird.draw(WIN)


def show_score(num):
    """Displays score at top-middle of screen. Should be given the highest z-value of all blits."""
    # this code is not written in redraw() since the score is not shown on the welcome screen
    score_digits = [int(x) for x in list(str(num))]
    score_width = 0

    for digit in score_digits:
        score_width += SCORE_IMG[digit].get_width()

    x_offset = int((WIN_WIDTH - score_width) / 2)

    for digit in score_digits:
        WIN.blit(SCORE_IMG[digit], (x_offset, int(WIN_HEIGHT / 10)))
        x_offset += SCORE_IMG[digit].get_width()


def harmonic():
    """Display welcome screen. Includes bird oscillation and moving ground."""
    shm_displacement = 0
    direction = True  # true up, false down
    message_x = int((WIN_WIDTH - MSG_IMG.get_width()) / 2)
    message_y = int(WIN_HEIGHT * 0.12)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                SFX['flap'].play()
                bird.flap()
                return

        # oscillation of bird
        if abs(shm_displacement) == 8:
            direction = not direction

        if direction:
            shm_displacement += 1
            bird.y += 1
        else:
            shm_displacement += -1
            bird.y += -1

        # scrolling ground
        ground.move()
        # draw bg, pipes, ground, bird
        redraw()
        # show welcome message
        WIN.blit(MSG_IMG, (message_x, message_y))

        CLOCK.tick(30)
        pygame.display.update()


def main():
    score = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                SFX['flap'].play()
                bird.flap()

        bird.move()  # bird in free fall
        ground.move()  # scrolling ground

        # check conditions for ground collision
        if bird.y + BIRD_IMG[0].get_height() > ground.Y - 1:
            SFX['hit'].play()
            return {'score': score, 'pipe crash': False}

        # check conditions for pipe collision
        bird_mid = bird.X + BIRD_IMG[0].get_width() / 2
        for pipe in pipes:
            if pipe.collide(bird):
                SFX['hit'].play()
                SFX['die'].play()
                return {'score': score, 'pipe crash': True}

            # moves all pipes if there are multiple on screen
            pipe.move()

            # check conditions for scoring
            pipe_mid = pipe.x + PIPE_IMG.get_width() / 2
            if pipe_mid <= bird_mid < pipe_mid + 4:
                score += 1
                SFX['point'].play()

        # when oldest pipe is 100-105 pixels from left edge, create a new pipe
        if 100 < pipes[0].x < 105:
            pipes.append(Pipe(WIN_WIDTH + 10))

        # when oldest pipe moves off the screen, delete it
        if pipes[0].x < -PIPE_IMG.get_width():
            pipes.pop(0)

        # draw bg, pipes, ground, bird
        redraw()
        # score is shown with the greatest z-level
        show_score(score)

        CLOCK.tick(30)
        pygame.display.update()


def game_over(info):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # click to play again if bird has crashed and fallen to the ground
            if event.type == pygame.MOUSEBUTTONDOWN and bird.y > ground.Y - 50:
                return

        # if a pipe crash occurred
        if info['pipe crash']:
            # custom fall upon death
            if bird.vel < 15:
                bird.vel += 2  # faster gravity upon death
            if bird.rot > -90:
                bird.rot -= 7  # faster rot_vel upon death
            if bird.rot < -90:  # rotation threshold (unchanged)
                bird.rot = -90

            # falling formula
            bird.y += min(bird.vel, ground.Y - bird.y - bird.HEIGHT)

        redraw()
        WIN.blit(GG_IMG, (50, 180))
        show_score(info['score'])
        CLOCK.tick(30)
        pygame.display.update()


if __name__ == '__main__':
    while True:
        WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        CLOCK = pygame.time.Clock()
        pygame.display.set_caption('Flappy Bird')

        bird = Bird(int((WIN_HEIGHT - BIRD_IMG[0].get_height()) / 2))
        ground = Ground()
        pipes = [Pipe(WIN_WIDTH + 300)]  # location of first pipe

        harmonic()  # oscillation and welcome screen
        crash_info = main()  # main returns score and crash condition (ground or pipe)
        game_over(crash_info)  # pipe collisions are treated differently
