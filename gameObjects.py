from Items import *
from door import *
from gameclass import Sound
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group,  mov_speed, image_path, obstical, sound = None):
        super().__init__(group)
        self.pos = pos
        self.animation_images_by_folder = {}
        self.animation_index = 0
        self.animation_lengths = {}
        self.fill_animation(image_path)
        self.direction_an = "down"
        self.in_idle = "Idle"
        self.image = self.animation_images_by_folder.get(self.direction_an + self.in_idle, [])[0]
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = mov_speed
        self.obstical = obstical
        self.camera_group = group
        self.x = 0
        self.y = 0
        self.visible = True
        self.alive = True
        self.moving = False
        self.animation_speed = 0.1
        self.sound = sound


    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.direction_an = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.direction_an = "down"
        else:
            self.direction.y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.direction_an = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.direction_an = "right"
        else:
            self.direction.x = 0
        self.x = self.direction.x
        self.y = self.direction.y
        if self.direction.length() > 1:
            self.direction = self.direction.normalize()

    def update(self):
        self.input()
        if self.direction == (0, 0):
            self.in_idle = "Idle"
            self.sound.play_footsteps(stop=True)
            self.animation_speed = 0.05

        else:
            self.rect.center += self.direction * self.speed
            self.sound.play_footsteps()
            self.in_idle = "Moving"
            self.animation_speed = 0.1

    def reset_pos(self):
        if self.direction.x and self.direction.y:
            self.rect.center -= self.direction * self.speed
            self.direction.y = 0
            self.direction.x = self.x
            self.rect.center += self.direction * self.speed
            if self.camera_group.check_specific_collision(self):
                self.rect.center -= self.direction * self.speed
                self.direction.x = 0
                self.direction.y = self.y
                self.rect.center += self.direction * self.speed
            if self.camera_group.check_specific_collision(self):
                self.rect.center -= self.direction * self.speed
                self.moving = False
                self.in_idle = "Idle"
                self.sound.play_footsteps(stop=True)
                self.animation_speed = 0.05
        else:
            self.moving = False
            self.in_idle = "Idle"
            self.sound.play_footsteps(stop=True)
            self.animation_speed = 0.05
            self.rect.center -= self.direction * self.speed
        self.get_direction()

    def get_direction(self):
        if self.direction.x:
            if self.direction.x > 0:
                self.direction_an = "right"
            else:
                self.direction_an = "left"
        if self.direction.y:
            if self.direction.y > 0:
                self.direction_an = "down"
            else:
                self.direction_an = "up"

    def fill_animation(self, image_path):
        self.animation_images_by_folder = {}
        for root, _, files in os.walk(image_path):
            folder_name = os.path.relpath(root, image_path)
            image_list = []
            for file_name in sorted(files):
                if file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                    image = pygame.image.load(os.path.join(root, file_name)).convert_alpha()
                    image_list.append(image)
            if image_list:
                self.animation_images_by_folder[folder_name] = image_list
                self.animation_lengths[folder_name] = len(image_list)

    def animate(self):
        animation_length = self.animation_lengths.get(self.direction_an + self.in_idle, 0)
        self.animation_index += self.animation_speed
        if self.animation_index >= animation_length:
            self.animation_index = 0
        self.image = self.animation_images_by_folder.get(self.direction_an + self.in_idle, [])[int(self.animation_index)]

class Extra(pygame.sprite.Sprite):
    def __init__(self, pos, image_path, obstical, alpha=False, center=False):
        super().__init__()
        if alpha:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = pygame.image.load(image_path).convert()
        if center:
            self.rect = self.image.get_rect(center=pos)
        else:
            self.rect = self.image.get_rect(topleft=pos)
        self.obstical = obstical
        self.visible = True


class Maze_Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path, obstical, background=None, light_list=None):
        super().__init__(group)
        self.image = pygame.image.load(image_path).convert_alpha()
        if background:
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = self.image.get_rect(center=pos)
        if light_list:
            Light(pos, light_list[0], light_list[1], light_list[2], light_list[3], light_list[4], light_list[5], light_list[6])
        self.obstical = obstical
        self.visible = True


class Camera_Group(pygame.sprite.Group):
    def __init__(self, zoom):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.light_offset = pygame.math.Vector2()
        self.half_win_width = self.display_surface.get_width() // 2
        self.half_win_height = self.display_surface.get_height() // 2

        self.zoom_scale = zoom
        self.zoom_scale_original = self.zoom_scale
        self.internal_surf_size = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_win_width, self.half_win_height))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_win_width
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_win_height
        self.light_player_pos = self.internal_offset + (500, 500)
        self.collide_list = []
        self.render_sprites_list = []
        self.collision_sprites_list = []
        self.light_list = []
        self.light_pos_list = []
        self.hitbox_list = []

        self.collision_surface = pygame.Surface((500, 500))
        self.collision_rec = self.collision_surface.get_rect(center=(500, 500))

        self.render_surface = pygame.Surface((1200, 1200))
        self.render_rec = self.render_surface.get_rect(center=(500, 500))

        self.in_light = False
        self.num_refuel_station = []
        self.sonar_in_use = False
        self.door_list = []

    def get_object_index(self, target):
        for index, sprite in enumerate(self.sprites()):
            if sprite.target == target:
                return index
        return None


    def center_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_win_width
        self.offset.y = target.rect.centery - self.half_win_height
        self.light_offset.x = target.rect.centerx - 1000
        self.light_offset.y = target.rect.centery - 1000


    def view(self, target):
        if self.zoom_scale == self.zoom_scale_original:
            self.zoom_scale = 0.5 * self.zoom_scale_original
            self.render_surface = pygame.Surface((2200, 2200))
            self.render_rec = self.render_surface.get_rect(center=(500, 500))
        else:
            self.zoom_scale = self.zoom_scale_original
            self.render_surface = pygame.Surface((1200, 1200))
            self.render_rec = self.render_surface.get_rect(center=(500, 500))
        self.update_surface(target, True)

    def draw_camera(self, light_player, target, dealer, fuel_station):
        dealer.in_range = False
        self.num_refuel_station.clear()
        self.internal_surf.fill("Black")
        target.update()
        self.update_surface(target)
        self.check_collision(target)
        if self.collide_list:
            target.reset_pos()
        self.center_camera(target)
        for sprite in self.render_sprites_list:
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image, offset_pos)

        self.light_pos_list.clear()

        for sprite in self.light_list:
            self.light_pos_list.append(sprite.rect.topleft - self.light_offset)
            if sprite.rect.scale_by(0.6).colliderect(target):
                self.in_light = True

        for sprite in self.hitbox_list:
            if sprite.rect.colliderect(target):
                sprite.colliding = True
                if not sprite.dealer:
                    light_player.refueling = True
                    self.num_refuel_station.append(sprite)
                else:
                    dealer.in_range = True
                    sprite.dealer.rotate_sprite((500, 500) + self.internal_offset, sprite.rect.center - self.offset + self.internal_offset)
                    if not sprite.dealer.bubble.check_collision(target):
                        sprite.dealer.bubble.change_text()
                        sprite.dealer.bubble.visible = True
                    else:
                        sprite.dealer.bubble.visible = False
            else:
                if sprite.dealer:
                    sprite.dealer.bubble.visible = False
                sprite.colliding = False

        light_surface = light_player.draw_lights(self.light_list, self.light_pos_list, self.in_light)
        self.internal_surf.blit(light_surface, light_player.black_surface.get_rect(center=self.light_player_pos))
        self.in_light = False
        if self.num_refuel_station and not self.sonar_in_use and not light_player.tank_full:
            for station in self.num_refuel_station:
                light_player.draw_fuel_line((500, 500) + self.internal_offset, station.rect.center - self.offset + self.internal_offset, self.internal_surf, fuel_station)
                station.refueling = False
        else:
            light_player.playing_sound = False

        if not self.zoom_scale == self. zoom_scale_original:
            scaled_surf = pygame.transform.smoothscale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
            scaled_rect = scaled_surf.get_rect(center=(self.half_win_width, self.half_win_height))
            self.display_surface.blit(scaled_surf, scaled_rect)
        else:
            self.display_surface.blit(self.internal_surf, self.internal_rect)

    def check_collision(self, target):
        self.collide_list.clear()
        for sprite in self.collision_sprites_list:
            if target.rect.colliderect(sprite.rect):
                if isinstance(sprite, (Fuel_Item, Coin_Item, Sonar_Item, Range_Item, Victory_Item, Key)):        #Hier neues Item hinzufügen
                    sprite.collect_item(1)
                    sprite.kill()
                    self.update_surface(target, True)
                elif isinstance(sprite, Door) and not sprite.is_open and sprite.open_door():
                    sprite.open_door()
                    self.door_list.append(sprite)
                    self.collide_list.append(sprite)
                    self.update_surface(target, True)
                elif isinstance(sprite, Sound_Item):
                    sprite.collect_item(1)
                else:
                    self.collide_list.append(sprite)
        for sprite in self.door_list:
            if sprite.obstical:
                sprite.update()
            else:
                self.door_list.remove(sprite)
                self.update_surface(target, True)


    def check_specific_collision(self, target):
        for sprite in self.collide_list:
            if target.rect.colliderect(sprite.rect):
                return True
        else:
            return False

    def fill_up_surface(self):
        for sprite in self.sprites():
            if self.render_rec.colliderect(sprite.rect):
                if sprite.visible:
                    self.render_sprites_list.append(sprite)
                elif isinstance(sprite, Light):
                    self.light_list.append(sprite)
                elif isinstance(sprite, Hitbox):
                    self.hitbox_list.append(sprite)
            if self.collision_rec.contains(sprite.rect) and sprite.obstical:
                self.collision_sprites_list.append(sprite)

    def clear_lists(self):
        self.light_list.clear()
        self.hitbox_list.clear()
        self.render_sprites_list.clear()
        self.collision_sprites_list.clear()

    def update_surface(self, target, force_update=None):
        if not self.collision_rec.scale_by(0.2).contains(target) or force_update:
            self.collision_rec = self.collision_rec.clamp(target.rect)
            self.render_rec = self.render_rec.clamp(target.rect)
            self.clear_lists()
            self.fill_up_surface()

    def add_sprite(self, sprite, player):
        self.add(sprite)
        self.update_surface(player, True)

    def remove_sprite(self, sprite, player):
        self.remove(sprite)
        self.update_surface(player, True)
