import pygame
import sys
from random import choice, randint

from player import Player
from alien import Alien, AlienBoss
from laser import Laser
import block


class Game:
    def __init__(self):
        # player setup
        player_sprite = Player((screen_width / 2, screen_height), 5, screen_width)
        self.player = pygame.sprite.GroupSingle(sprite=player_sprite)

        # health setup
        self.lives = 3
        self.live_surf = pygame.image.load('graphics/player.png').convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)

        # score setup
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)

        # obstacles setup
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_shape = block.obstacle_shape
        self.obstacle_amount = 5
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_obstacles(screen_width / 16, 560, *self.obstacle_x_positions)

        # aliens setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_direction = 1
        self.create_aliens(rows=6, cols=12)

        # alien boss setup
        self.alien_boss = pygame.sprite.GroupSingle()
        self.alien_boss_spawn_time = randint(400, 800)

        # audio setup
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.1)
        music.play(loops=-1)

        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.2)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.2)

    def create_obstacle(self, x_start, y_start, x_offset):
        for row_index, row in enumerate(self.obstacle_shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + x_offset
                    y = y_start + row_index * self.block_size
                    one_block = block.Block(self.block_size, 'gray', x, y)
                    self.blocks.add(one_block)

    def create_obstacles(self, x_start, y_start, *offset):
        for x_offset in offset:
            self.create_obstacle(x_start, y_start, x_offset)

    def create_aliens(self, rows, cols, x_distance=60, y_distance=48, x_offset=50, y_offset=50):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)

                self.aliens.add(alien_sprite)

    def alien_positions_update(self):
        for alien in self.aliens.sprites():
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.aliens_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.aliens_move_down(2)

    def aliens_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens:
                alien.rect.y += distance

    def aliens_shoots(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def alien_boss_spawner(self):
        self.alien_boss_spawn_time -= 1

        if self.alien_boss_spawn_time <= 0:
            self.alien_boss.add(AlienBoss(choice(['left', 'right']), screen_width))
            self.alien_boss_spawn_time = randint(400, 800)

    def collision_checks(self):
        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                # boss collisions
                if pygame.sprite.spritecollide(laser, self.alien_boss, True):
                    self.score += 1000
                    laser.kill()

        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # player collisions
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1

                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', False, (64, 64, 64))
        score_rect = score_surf.get_rect(topleft=(10, -10))
        screen.blit(score_surf, score_rect)

    def display_victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('YOU WON!!!', False, 'white')
            victory_rect = victory_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.alien_positions_update()
        self.alien_lasers.update()
        self.alien_boss_spawner()
        self.alien_boss.update()
        self.collision_checks()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.alien_boss.draw(screen)
        self.display_lives()
        self.display_score()
        self.display_victory_message()


class CRT:
    def __init__(self):
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width, screen_height))

    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height / line_height)

        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, 'black', (0, y_pos), (screen_width, y_pos), 1)

    def draw(self):
        self.tv.set_alpha(50)
        self.create_crt_lines()
        screen.blit(self.tv, (0, 0))


if __name__ == '__main__':
    pygame.init()
    screen_width = 800
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 1200)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.aliens_shoots()

        screen.fill((30, 30, 30))
        game .run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)
