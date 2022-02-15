from random import randint, uniform
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
    spaceship_speed = 5

    asteroid_images = ['0.png', '1.png', '2.png']
    asteroid_spawn_duration = 500
    asteroid_size = (100,100)
    asteroid_speed = (0.5,3.5)

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

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, filename, size, speed):
        super().__init__()
        self.filename = filename
        self.size = size
        self.speed = speed
        self.update_sprite(self.filename)
        self.find_position()

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def find_position(self):
        self.pos = (randint(0, Settings.window_width - Settings.asteroid_size[0]),randint(0, Settings.window_height - Settings.asteroid_size[1]))
        self.set_pos(*self.pos)

    def update(self):
        self.check_pos()
        self.move()

    def move(self):
        self.rect.move_ip(self.speed['x'], self.speed['y'])

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def check_pos(self):
        if self.rect.top < -self.rect.height:
            self.rect.top = Settings.window_height

        elif self.rect.top > Settings.window_height + self.rect.height:
            self.rect.bottom = 0

        elif self.rect.left < -self.rect.width:
            self.rect.left = Settings.window_width

        elif self.rect.left > Settings.window_width + self.rect.width:
            self.rect.right = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

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
        super().__init__()
        self.filenames = filenames
        self.size = size
        self.lives = lives
        self.angle = 1
        self.rotate_direction = None
        self.is_accelerating = False
        self.speed = { 'y': 0, 'x': 0 }
        self.max_speed = 5

        self.update_sprite(self.filenames['normal'])
        self.set_pos(Settings.window_width // 2 - self.rect.width // 2, Settings.window_height // 2 - self.rect.height // 2)

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rotate()
        self.move()
        self.check_collisions()
        self.check_pos()
        if self.is_accelerating:
            self.accelerate()

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def accelerate(self):
        if Settings.spaceship_speed * cos(radians(self.angle)) < self.max_speed:
            self.speed['x'] = Settings.spaceship_speed * cos(radians(self.angle))

        if Settings.spaceship_speed * sin(radians(self.angle)) < self.max_speed:
            self.speed['y'] = Settings.spaceship_speed * sin(radians(self.angle))

    def move(self):
        self.rect.move_ip(self.speed['x'], self.speed['y'])

    def check_pos(self):
        if self.rect.top < -self.rect.height:
            self.rect.top = Settings.window_height

        elif self.rect.top > Settings.window_height + self.rect.height:
            self.rect.bottom = 0

        elif self.rect.left < -self.rect.width:
            self.rect.left = Settings.window_width

        elif self.rect.left > Settings.window_width + self.rect.width:
            self.rect.right = 0

    def rotate(self):
        if self.rotate_direction == 'left':
            self.angle -= Settings.spaceship_rotation_speed

        elif self.rotate_direction == 'right':
            self.angle += Settings.spaceship_rotation_speed

        if self.angle + Settings.spaceship_rotation_speed > 360 and self.angle + Settings.spaceship_rotation_speed < -360:
            self.angle = 0

        if self.is_accelerating:
            filename = self.filenames['boost']
        else:
            filename = self.filenames['normal']

        center = self.rect.center
        self.update_sprite(filename)
        self.image = pygame.transform.rotate(self.image, -self.angle)
        self.center_sprite(center)

    def center_sprite(self, center):
        self.rect = self.image.get_rect()
        self.rect.center = center

    def change_rotate_direction(self, direction):
        self.rotate_direction = direction

    def check_collisions(self):
        asteroid_hit_list = pygame.sprite.spritecollide(self, game.asteroids, False, pygame.sprite.collide_mask)
        if len(asteroid_hit_list) > 0:
            game.running = False

class Game():
    def __init__(self) -> None:
        super().__init__()
        pygame.init()   
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        self.background = Background('background.png')

        self.spaceship = Spaceship({ 'normal': 'spaceship.png', 'boost': 'spaceship_boost.png'}, (58,56), 3)
        self.asteroid_timer = Timer(Settings.asteroid_spawn_duration)
        self.asteroids = pygame.sprite.Group()

        self.running = True 

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            self.draw()
            self.update()
            self.watch_for_events()
    
    def update(self):
        self.spaceship.update()
        [ asteroid.update() for asteroid in self.asteroids]
        if self.asteroid_timer.is_next_stop_reached():
            self.asteroids.add(Asteroid(Settings.asteroid_images[randint(0, len(Settings.asteroid_images) - 1)], Settings.asteroid_size, { 'x': uniform(*Settings.asteroid_speed), 'y': uniform(*Settings.asteroid_speed) }))

    def draw(self):
        self.background.draw(self.screen)
        self.spaceship.draw(self.screen)
        self.asteroids.draw(self.screen)
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
