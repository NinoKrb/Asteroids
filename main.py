import pygame, os
from math import sin, cos, radians

class Settings(object):
    window_width = 1000
    window_height = 600
    title = 'Asteroids Projekt'
    fps = 60
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(path_file, "assets")
    path_image = os.path.join(path_assets, "images")

    spaceship_rotation_speed = 5

class Timer(object):
    def __init__(self, duraton, with_start=True):
        self.duraton = duraton
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duraton

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duraton
            return True
        return False

class Background(pygame.sprite.Sprite):
    def __init__(self, filename) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, filenames, size, lives):
        self.filenames = filenames
        self.size = size
        self.lives = lives
        self.angle = 0
        self.rotate_direction = None
        self.is_accelerating = False
        self.speed = { 'y': 0, 'x': 0 }
        self.max_speed = [-4,4]

        self.update_sprite(self.filenames['normal'])
        self.set_pos(Settings.window_width // 2 - self.rect.width // 2, Settings.window_height // 2 - self.rect.height // 2)

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rotate()
        self.move()
        self.check_pos()
        if self.is_accelerating:
            self.accelerate()

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def accelerate(self):
        # if (self.speed['x'] - sin(self.angle)) < self.max_speed[1] and (self.speed['x'] - sin(self.angle)) > self.max_speed[0]:
        #     self.speed['x'] -= sin(self.angle)

        # if (self.speed['y'] - cos(self.angle)) < self.max_speed[1] and (self.speed['y'] - cos(self.angle)) > self.max_speed[0]:
        #     self.speed['y'] -= cos(self.angle)

        self.speed['x'] = 10 * cos(radians(self.angle))
        self.speed['y'] = 10 * sin(radians(self.angle))

    def move(self):
        self.rect.move_ip(self.speed['x'], self.speed['y'])

    def check_pos(self):
        if self.rect.top < -100:
            self.rect.top = Settings.window_height

        elif self.rect.top > Settings.window_height + 100:
            self.rect.bottom = 0

        elif self.rect.left < -100:
            self.rect.left = Settings.window_width

        elif self.rect.left > Settings.window_width + 100:
            self.rect.right = 0

    def rotate(self):
        if self.rotate_direction == 'left':
            self.angle -= Settings.spaceship_rotation_speed

        elif self.rotate_direction == 'right':
            self.angle += Settings.spaceship_rotation_speed

        if self.angle + Settings.spaceship_rotation_speed > 360 and self.angle + Settings.spaceship_rotation_speed < -360:
            self.angle = 0

        if self.rotate_direction != None:
            center = self.rect.center
            if self.is_accelerating:
                self.update_sprite(self.filenames['boost'])
            else:
                self.update_sprite(self.filenames['normal'])
            #self.image = pygame.transform.rotate(self.image, self.angle)
            self.image = pygame.transform.rotate(self.image, -self.angle)
            self.center_sprite(center)

    def center_sprite(self, center):
        self.rect = self.image.get_rect()
        self.rect.center = center

    def change_rotate_direction(self, direction):
        self.rotate_direction = direction

class Game():
    def __init__(self) -> None:
        super().__init__()
        pygame.init()   
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        self.background = Background("background.png")

        self.spaceship = Spaceship({ 'normal': 'spaceship.png', 'boost': 'spaceship_boost.png'}, (58,56), 3)

        self.running = True 

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            self.draw()
            self.update()
            self.watch_for_events()
    
    def update(self):
        self.spaceship.update()

    def draw(self):
        self.background.draw(self.screen)
        self.spaceship.draw(self.screen)
        pygame.display.flip()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                if event.key == pygame.K_RIGHT:
                    self.spaceship.change_rotate_direction('right')

                if event.key == pygame.K_LEFT:
                    self.spaceship.change_rotate_direction('left')

                if event.key == pygame.K_UP:
                    self.spaceship.is_accelerating = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.spaceship.change_rotate_direction(None)
            
                if event.key == pygame.K_UP:
                    self.spaceship.is_accelerating = False

            if event.type == pygame.QUIT:
                self.running = False


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
    game = Game()
    game.run()
