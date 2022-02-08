import pygame, os
from math import sin, cos

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
    def __init__(self, filename, size, lives):
        self.filename = filename
        self.size = size
        self.lives = lives
        self.angle = 0
        self.rotate_direction = None
        self.speed = { 'y': 0, 'x': 0 }

        self.update_sprite(self.filename)
        self.set_pos(Settings.window_width // 2 - self.rect.width // 2, Settings.window_height // 2 - self.rect.height // 2)

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rotate()

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def accelerate(self):
        self.speed['x'] -= sin(self.angle)
        self.speed['y'] -= cos(self.angle)

    def rotate(self):
        if self.rotate_direction == 'left':
            self.angle += Settings.spaceship_rotation_speed
            
        elif self.rotate_direction == 'right':
            self.angle -= Settings.spaceship_rotation_speed

        if self.rotate_direction != None:
            old_center = self.rect.center
            self.update_sprite(self.filename)
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = old_center

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

        self.spaceship = Spaceship("spaceship.png", (58,56), 3)

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

                elif event.key == pygame.K_LEFT:
                    self.spaceship.change_rotate_direction('left')

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.spaceship.change_rotate_direction(None)

            if event.type == pygame.QUIT:
                self.running = False


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
    game = Game()
    game.run()
