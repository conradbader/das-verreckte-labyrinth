import pygame
import os
import path

class Fuel_Container(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path):
        super().__init__(group)
        self.animation_images = []
        self.animation_index = 0
        self.animation_len = 0
        self.fill_animation(image_path)
        self.image = self.animation_images[self.animation_index]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos
        self.or_pos = pos
        self.direction = pygame.math.Vector2()
        self.posY_max = 902
        self.posY_min = 1052
        self.range = self.posY_min - self.posY_max
        self.direction.y = 1

    def fill_animation(self, image_path):
        file_list = os.listdir(image_path)
        for file_name in sorted(file_list):
            if file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                image = pygame.image.load(os.path.join(image_path, file_name)).convert_alpha()
                self.animation_images.append(image)
        self.animation_len = len(self.animation_images)

    def animate(self):
        self.animation_index += 0.1
        if self.animation_index >= self.animation_len:
            self.animation_index = 0
        self.image = self.animation_images[int(self.animation_index)]


class Coin_Count(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path, coin_item):
        super().__init__(group)
        self.Coin_Item = coin_item
        self.font = pygame.font.Font(f"{path.schrift}BreatheFireIi.ttf", 25)
        self.surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.img = pygame.image.load(image_path).convert_alpha()
        self.img_rect = self.img.get_rect(topleft=(0, 0))
        self.image = None
        self.colour_count = (255, 255, 255)
        self.update_count()
        self.rect = self.image.get_rect(center=pos)

    def update_count(self):
        self.surface.blit(self.img, self.img_rect)
        text = self.font.render(str(self.Coin_Item.money), True, self.colour_count)
        text_rect = text.get_rect(center=(20, 15))
        self.surface.blit(text, text_rect)
        self.image = self.surface



class Inventory(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path):
        super().__init__(group)
        self.font = pygame.font.Font(None, 40)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.inv_back = self.image
        self.inv_rec = self.inv_back.get_rect(topleft=(0, 0))
        self.pos = pos
        self.items = {}
        self.pos_list = [(49, 59), (106, 59), (167, 59), (225, 59)]
        self.surface = pygame.Surface((269, 102), pygame.SRCALPHA)
        self.colour = (171, 141, 63)

    def update_inventory(self, count, item):
        if item.type not in self.items:
            self.items[item.type] = {
                'count': count,
                'image': item.inventory_image,
                'instance': item,
            }
        else:
            self.items[item.type]['count'] += count
        self.delete_item(count, item)
        self.draw_inventory()

    def delete_item(self, count, item):
        if self.items[item.type]['count'] == 0:
            del self.items[item.type]

    def draw_inventory(self):
        self.surface.blit(self.inv_back, self.inv_rec)
        for i, (item_type, item_data) in enumerate(self.items.items()):
            text = self.font.render(str(item_data['count']), True, self.colour)
            pos = self.pos_list[i]
            self.surface.blit(item_data['image'], item_data['image'].get_rect(center=pos))
            self.surface.blit(text, pos)
        self.image = self.surface

    def check_slot(self, index, egg_open=False):
        try:
            item_type = list(self.items.keys())[index]
            if not egg_open:
                self.items[item_type]['instance'].use_item()
            elif self.items[item_type]['instance'].type == "egg":
                self.items[item_type]['instance'].use_item()

        except IndexError:
            pass


class Key_Inv(pygame.sprite.Sprite):
    def __init__(self, pos, group, path):
        super().__init__(group)
        self.pos = pos
        self.images = {}
        self.fill_images(path)
        self.dic_num = 0
        self.image = self.images[f"{str(self.dic_num)}.png"]
        self.rect = self.image.get_rect(center=pos)

    def fill_images(self, image_path):
        file_list = os.listdir(image_path)
        for file_name in sorted(file_list):
            if file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                image = pygame.image.load(os.path.join(image_path, file_name)).convert_alpha()
                image = pygame.transform.smoothscale(image, (50, 50))
                self.images[file_name] = image

    def update_chain(self):
        self.dic_num += 1
        self.image = self.images[f"{str(self.dic_num)}.png"]

class UI_Group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def draw_ui(self):
        for sprite in self.sprites():
            self.display_surface.blit(sprite.image, sprite.rect)

    def add_sprite(self, sprite):
        self.add(sprite)
        self.draw_ui()

    def remove_sprite(self, sprite):
        self.remove(sprite)
        self.draw_ui()

