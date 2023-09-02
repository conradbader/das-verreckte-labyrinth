import pygame
import os
from enum import Enum
from Items import Sound_Item
from DisplaySetup import Light


class Direction(Enum):
    UP = 90
    DOWN = - 90
    LEFT = 180
    RIGHT = 0

class Door(pygame.sprite.Sprite):
    def __init__(self, pos, group, path, direction, key_chain, game, tile_type):
        super().__init__(group)
        self.tile_type = tile_type
        self.music_list = ["level1", "Dungeon", "Moonlight", "Horns"]
        self.music = self.choose_music()
        self.pos = pos
        self.folder_paths = []
        self.fill_folder_paths(path)
        self.group = group
        self.game = game
        self.direction = direction
        self.animation_images = []
        self.animation_index = 0
        self.animation_len = 0
        self.direction = direction.value
        self.fill_animation(self.folder_paths[self.tile_type[-1]])
        self.image = self.animation_images[0]
        self.rect = self.image.get_rect(center=pos)
        self.obstical = True
        self.visible = True
        self.is_open = False
        self.door_type = int(self.tile_type[-1]) + 1
        self.sound = game.sound
        self.key_chain = key_chain
        self.sound_item_1 = None
        self.sound_item_2 = None
        self.place_sound_item()
        self.sound_playing = False
        self.current_time = 0
        self.last_refreshed = 0
        self.refresh_time = 1500

    def fill_folder_paths(self, base_path):
        folder_names = [folder_name for folder_name in os.listdir(base_path) if
                        os.path.isdir(os.path.join(base_path, folder_name))]
        self.folder_paths = {folder_name: os.path.join(base_path, folder_name) for folder_name in folder_names}

    def choose_music(self):
        try:
            music = self.music_list[int(self.tile_type[-1]) - 1]
        except:
            music = self.music_list[1]
        return music

    def place_sound_item(self):
        if self.direction == 90:
            self.sound_item_1 = Sound_Item(self.pos, self.group, self.game, "SaveSpace", False, "top", "up/down")
            self.sound_item_2 = Sound_Item(self.pos, self.group, self.game, self.music, False, "bottom", "up/down")
        elif self.direction == -90:
            self.sound_item_1 = Sound_Item(self.pos, self.group, self.game, self.music, False, "top", "up/down")
            self.sound_item_2 = Sound_Item(self.pos, self.group, self.game, "SaveSpace", False, "bottom", "up/down")
        elif self.direction == 0:
            self.sound_item_1 = Sound_Item(self.pos, self.group, self.game, self.music, False, "left", "left/right")
            self.sound_item_2 = Sound_Item(self.pos, self.group, self.game, "SaveSpace", False, "right", "left/right")
        elif self.direction == 180:
            self.sound_item_1 = Sound_Item(self.pos, self.group, self.game, "SaveSpace", False, "left", "left/right")
            self.sound_item_2 = Sound_Item(self.pos, self.group, self.game, self.music, False, "right", "left/right")

    def fill_animation(self, image_path):
        file_list = os.listdir(image_path)
        for file_name in sorted(file_list):
            if file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                image = pygame.image.load(os.path.join(image_path, file_name)).convert_alpha()
                image = pygame.transform.rotate(image, self.direction)
                self.animation_images.append(image)
            self.animation_len = len(self.animation_images)

    def open_door(self):
        if self.door_type in Key.key_list:
            self.is_open = True
            self.sound.play_sound("DoorOpen")
            return True
        else:
            if self.update_timer():
                self.sound_playing = False
            if not self.sound_playing:
                self.sound_playing = True
                self.sound.play_sound("DoorClosed")
            return False

    def update(self):
        if self.animation_index < self.animation_len - 0.1:
            self.animation_index += 0.1
            self.image = self.animation_images[int(self.animation_index)]
        else:
            self.obstical = False
            self.sound_item_1.collectable = True
            self.sound_item_2.collectable = True

    def update_timer(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time - self.last_refreshed >= self.refresh_time:
            self.last_refreshed = self.current_time
            return True
        else:
            return False

class Key(pygame.sprite.Sprite):

    key_list = []
    def __init__(self, pos, group, path, sound, tone, key_chain, light_player, sonar_item, tile_type):
        super().__init__(group)
        self.tile_type = tile_type
        self.light_player = light_player
        self.sonar_item = sonar_item
        self.group = group
        self.images = {}
        self.fill_images(path)
        self.image = self.images[f"{self.tile_type}.png"]
        self.image = pygame.transform.smoothscale(self.image, (15, 26))
        self.rect = self.image.get_rect(center=pos)
        self.key_type = int(self.tile_type[-1])
        self.sound = sound
        self.tone = tone
        self.key_chain = key_chain
        self.visible = True
        self.obstical = True
        self.light_key = Light(pos, 1000, 1000, 200, self.light_player, 0, self.group, self.sonar_item)
        self.group.add(self.light_key)

    def fill_images(self, image_path):
        file_list = os.listdir(image_path)
        for file_name in sorted(file_list):
            if file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                image = pygame.image.load(os.path.join(image_path, file_name)).convert_alpha()
                image = pygame.transform.smoothscale(image, (40, 40))
                self.images[file_name] = image


    def collect_item(self, count):
        self.sound.play_sound(self.tone)
        self.group.remove(self.light_key)
        Key.key_list.append(self.key_type)
        self.key_chain.update_chain()

    def reset(self):
        Key.key_list.clear()