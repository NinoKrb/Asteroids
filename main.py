from random import randint, uniform
from re import S
import pygame, os
from math import sin, cos, radians

class Settings(object):
    # Essentials
    window_width = 1300
    window_height = 900
    title = 'Asteroids Projekt'
    fps = 60
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(path_file, "assets")
    path_image = os.path.join(path_assets, "images")

    # Spaceship
    spaceship_rotation_speed = 5
    spaceship_max_speed = 8
    spaceship_filenames = { 'normal': 'spaceship.png', 'boost': 'spaceship_boost.png'}

    # Asteroids
    asteroid_images = ['0.png', '1.png', '2.png']
    asteroid_spawn_duration = 500
    asteroid_size = (100,100)
    asteroid_speed = (1.5,3.5)
    asteroid_max_count = 5

    # Projectiles
    max_projectiles = 10
    projectile_filename = 'projectile.png'
    projectile_size = (9,21)
    projectile_min_speed = 3
    projectile_life_duration = 5000

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

class Projectile(pygame.sprite.DirtySprite):
    def __init__(self, filename, angle, speed, size, pos):
        super().__init__()
        self.filename = filename
        self.angle = angle
        self.size = size
        self.speed = self.calculate_speed(speed)
        self.pos = pos
        self.life_timer = Timer(Settings.projectile_life_duration, False)
        self.update_sprite(filename)
        self.set_pos(*self.pos)

        center = self.rect.center
        self.update_sprite(filename)
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.center_sprite(center)

    def calculate_speed(self, speed):
        new_speed = { 'x': 0, 'y': 0 }
        angle = radians(self.angle)

        new_speed['x'] = speed[0] - sin(angle)
        new_speed['y'] = speed[1] - cos(angle)

        if new_speed['x'] > 0 and new_speed['x'] < Settings.projectile_min_speed:
            new_speed['x'] = Settings.projectile_min_speed

        elif new_speed['x'] < 0 and new_speed['x'] > -Settings.projectile_min_speed:
            new_speed['x'] = -Settings.projectile_min_speed

        if new_speed['y'] > 0 and new_speed['y'] < Settings.projectile_min_speed:
            new_speed['y'] = Settings.projectile_min_speed

        elif new_speed['y'] < 0 and new_speed['y'] > -Settings.projectile_min_speed:
            new_speed['y'] = -Settings.projectile_min_speed

        return new_speed

    def center_sprite(self, center):
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.life_timer.is_next_stop_reached():
            self.kill()
        self.move()

    def move(self):
        self.rect.move_ip(self.speed['x'], self.speed['y'])

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

class Asteroid(pygame.sprite.DirtySprite):
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
        self.check_spawn_collission()

    def check_spawn_collission(self):
        hit = pygame.sprite.spritecollide(self, game.spaceship, False, pygame.sprite.collide_circle_ratio(2))
        if len(hit) > 0:
            self.find_position()

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

class Background(pygame.sprite.DirtySprite):
    def __init__(self, filename) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Spaceship(pygame.sprite.DirtySprite):
    def __init__(self, filenames, size, lives):
        super().__init__()
        self.filenames = filenames
        self.size = size
        self.lives = lives
        self.angle = 1
        self.rotate_direction = None
        self.is_accelerating = False
        self.speed = { 'y': 0, 'x': 0 }
        self.projectiles = pygame.sprite.Group()

        self.update_sprite(self.filenames['normal'])
        self.set_pos(Settings.window_width // 2 - self.rect.width // 2, Settings.window_height // 2 - self.rect.height // 2)

    def shoot(self):
        if len(self.projectiles) <= Settings.max_projectiles:
            self.projectiles.add(Projectile(Settings.projectile_filename, self.angle, (self.speed['x'], self.speed['y']), Settings.projectile_size, (self.rect.centerx, self.rect.centery)))

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.projectiles.draw(screen)

    def update(self):
        self.rotate()
        self.move()
        self.check_collisions()
        self.check_pos()
        if self.is_accelerating:
            self.accelerate()
        self.projectiles.update()

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def accelerate(self):
        new_speed = { 'y': 0, 'x': 0 }
        angle = radians(self.angle)
        new_speed['x'] = self.speed['x'] - sin(angle)
        new_speed['y'] = self.speed['y'] - cos(angle)

        if abs(new_speed['x']) < Settings.spaceship_max_speed and abs(new_speed['y']) < Settings.spaceship_max_speed:
            self.speed['x'] = new_speed['x']
            self.speed['y'] = new_speed['y']

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
            self.angle += Settings.spaceship_rotation_speed

        elif self.rotate_direction == 'right':
            self.angle -= Settings.spaceship_rotation_speed

        if self.is_accelerating:
            filename = self.filenames['boost']
        else:
            filename = self.filenames['normal']

        center = self.rect.center
        self.update_sprite(filename)
        self.image = pygame.transform.rotate(self.image, self.angle)
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

        self.spaceship = pygame.sprite.GroupSingle(Spaceship(Settings.spaceship_filenames, (58,56), 3))
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
        self.spaceship.sprite.update()
        [ asteroid.update() for asteroid in self.asteroids]
        if self.asteroid_timer.is_next_stop_reached():
            if len(self.asteroids) < Settings.asteroid_max_count:
                self.asteroids.add(Asteroid(Settings.asteroid_images[randint(0, len(Settings.asteroid_images) - 1)], Settings.asteroid_size, { 'x': uniform(*Settings.asteroid_speed), 'y': uniform(*Settings.asteroid_speed) }))

    def draw(self):
        self.background.draw(self.screen)
        self.spaceship.sprite.draw(self.screen)
        self.asteroids.draw(self.screen)
        pygame.display.flip()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                if event.key == pygame.K_RIGHT:
                    self.spaceship.sprite.change_rotate_direction('right')

                if event.key == pygame.K_LEFT:
                    self.spaceship.sprite.change_rotate_direction('left')

                if event.key == pygame.K_UP:
                    self.spaceship.sprite.is_accelerating = True

                if event.key == pygame.K_RETURN:
                    self.spaceship.sprite.shoot()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.spaceship.sprite.change_rotate_direction(None)
            
                if event.key == pygame.K_UP:
                    self.spaceship.sprite.is_accelerating = False

            if event.type == pygame.QUIT:
                self.running = False


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
    game = Game()
    game.run()
