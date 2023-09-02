import pygame
from gameclass import Sound
from UI import *
from Items import Hitbox
import math
from DisplaySetup import Light
import path


class Dealer_Shop(pygame.sprite.Sprite):
    def __init__(self, pos, background_path, button_path, button_pressed_path, sound ,inventory, coin_item, coin_count, sonar_item, range_item, advanced_view, power_up_bar, better_tank, egg_item, fuel_station):
        super().__init__()
        self.sound = sound
        self.power_up_bar = power_up_bar
        self.type_list = [sonar_item, range_item, fuel_station, advanced_view, better_tank, egg_item]
        self.inventory = inventory
        self.coin_item = coin_item
        self.coin_count = coin_count
        self.open_dealer = False
        self.button_info = [
            {
                'pos': (12, 252),
                'text': 'Buy Item',
                'item_index': 0,
                'price': 3,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "item",
                'count': 1
            },
            {
                'pos': (216, 252),
                'text': 'Buy Item',
                'item_index': 1,
                'price': 1,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "item",
                'count': 1
            },
            {
                'pos': (420, 252),
                'text': 'Buy Item',
                'item_index': 2,
                'price': 10,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "item",
                'count': 1
            },
            {
                'pos': (12, 540),
                'text': 'Buy Item',
                'item_index': 3,
                'price': 10,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "power_up"
            },
            {
                'pos': (216, 540),
                'text': 'Buy Item',
                'item_index': 4,
                'price': 15,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "power_up"
            },
            {
                'pos': (430, 540),
                'text': 'Buy Item',
                'item_index': 5,
                'price': 1,
                'image': pygame.image.load(button_path).convert_alpha(),
                'pressed_image': pygame.image.load(button_pressed_path).convert_alpha(),
                'type': "item",
                'count': 1
            }
        ]
        self.pos_mouse = [0, 0]
        self.button_rec_list = []
        self.text_list = [
            ["TYP: Arcane Eye", "FUNC: reveal map", "DURATION: 3 sec", "PRICE: 3 Gems"],
            ["TYP: Zoom Item", "FUNC: zoom out", "DURATION: 3 sec", "PRICE: 1 Gem"],
            ["TYP: Fuel Station", "FUNC: place Fuel", "DURATION: infinite", "PRICE: 10 Gems"],
            ["TYP: View PowerUp", "FUNC: control View", "DURATION: infinite", "PRICE: 10 Gems"],
            ["TYP: Tank PowerUp", "FUNC: more Fuel", "DURATION: infinite", "PRICE: 15 Gems"],
            ["TYP: ???", "FUNC: ???", "DURATION: ???", "PRICE: ??? "]
        ]
        self.font = pygame.font.Font(f"{path.schrift}BreatheFireIi.ttf", 22)
        self.background = pygame.image.load(background_path).convert_alpha()
        self.back_rec = self.background.get_rect(topleft = (0,0))
        self.item_list = self.get_images()
        self.button_pressed_image = pygame.image.load(button_pressed_path).convert_alpha()
        self.button_not_pressed_image = pygame.image.load(button_path).convert_alpha()
        self.button_image = self.button_not_pressed_image
        self.button_pos_list = [button_info['pos'] for button_info in self.button_info]
        vert = [88, 118, 148, 178, 208]
        hor = [18, 222, 426]
        vert2 = [385, 415, 445, 475, 505]
        self.pos_info_list = [
            {
                'pic': (75, 30),
                'text': [(hor[0], vert[0]), (hor[0], vert[1]), (hor[0], vert[2]), (hor[0], vert[3]), (hor[0], vert[4])]
            },
            {
                'pic': (280, 30),
                'text': [(hor[1], vert[0]), (hor[1], vert[1]), (hor[1], vert[2]), (hor[1], vert[3]), (hor[1], vert[4])]
            },
            {
                'pic': (500, 35),
                'text': [(hor[2], vert[0]), (hor[2], vert[1]), (hor[2], vert[2]), (hor[2], vert[3]), (hor[2], vert[4])]
            },
            {
                'pic': (85, 335),
                'text': [(hor[0], vert2[0]), (hor[0], vert2[1]), (hor[0], vert2[2]), (hor[0], vert2[3]), (hor[0], vert2[4])]
            },
            {
                'pic': (290, 335),
                'text': [(hor[1], vert2[0]), (hor[1], vert2[1]), (hor[1], vert2[2]), (hor[1], vert2[3]), (hor[1], vert2[4])]
            },
            {
                'pic': (495, 330),
                'text': [(hor[2], vert2[0]), (hor[2], vert2[1]), (hor[2], vert2[2]), (hor[2], vert2[3]),(hor[2], vert2[4])]
            }
        ]

        self.pay = None
        self.full = None
        self.is_button_pressed = False
        self.current_pressed_button = None
        self.surface = pygame.Surface((624, 600))
        self.image = self.draw_table()
        self.rect = self.image.get_rect(center=(500, 500))
        self.click_cooldown = 400
        self.timer_start = 0

    def get_images(self):
        loaded_images = []
        for images in self.type_list:
            loaded_images.append(images.inventory_image)
        return loaded_images

    def draw_table(self):
        self.surface.blit(self.background, self.back_rec)

        for i, sprite in enumerate(self.item_list):
            pic_pos = self.pos_info_list[i]['pic']
            pic_rect = sprite.get_rect(topleft=pic_pos)
            self.surface.blit(sprite, pic_rect)

            text_pos_list = self.pos_info_list[i]['text']
            for j, text in enumerate(self.text_list[i]):
                text_surface = self.font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(topleft=text_pos_list[j])
                self.surface.blit(text_surface, text_rect)

            for button_info in self.button_info:
                if self.is_button_pressed and button_info['pos'] == self.current_pressed_button:
                    button_image = button_info['pressed_image']
                else:
                    button_image = button_info['image']
                rec = button_image.get_rect(topleft=button_info['pos'])
                self.button_rec_list.append(rec)
                self.surface.blit(button_image, rec)
                button_text = self.font.render(button_info['text'], True, (255, 255, 255))
                button_text_rect = button_text.get_rect(center=rec.center)
                self.surface.blit(button_text, button_text_rect)
        return self.surface

    def get_mouse_pos(self):
        pos_x, pos_y = pygame.mouse.get_pos()
        self.pos_mouse[0] = pos_x - self.rect.left
        self.pos_mouse[1] = pos_y - self.rect.top

    def check_Collision(self):
        self.get_mouse_pos()
        for i, button in enumerate(self.button_rec_list):
            if button.collidepoint(self.pos_mouse[0], self.pos_mouse[1]) and pygame.mouse.get_pressed()[0]:
                if not self.is_button_pressed:
                    self.is_button_pressed = True
                    self.current_pressed_button = self.button_info[i]['pos']
                    self.timer_start = pygame.time.get_ticks()
                    if not self.buy_item(self.button_info[i]['item_index']) and not self.full:
                        self.coin_count.colour_count = (255, 0, 0)
        if self.is_button_pressed:
            self.draw_table()
        self.pay = False
        self.full = False


        if self.is_button_pressed and pygame.time.get_ticks() - self.timer_start >= self.click_cooldown:
            self.is_button_pressed = False
            self.current_pressed_button = None
            self.button_image = self.button_not_pressed_image
            self.coin_count.colour_count = (0, 0, 0)
            self.power_up_bar.change_image(False)
            self.draw_table()

    def buy_item(self, item_index):
        item = self.button_info[item_index]
        if self.coin_item.check_coins(item['price']):
            if item['type'] == "item":
                self.inventory.update_inventory(item['count'], self.type_list[item['item_index']])
                self.pay = True
            elif self.power_up_bar.add_power_up(self.type_list[item['item_index']]):
                self.pay = True
            else:
                self.full = True
        if self.pay:
            self.coin_item.use_coins(item['price'])
        return self.pay


    def inventory_check(self, event, inventory,ui_group, egg_item, dealer):

        if not self.open_dealer:
            if event.key == pygame.K_1:
                inventory.check_slot(0, egg_item.open)
            elif event.key == pygame.K_2:
                inventory.check_slot(1, egg_item.open)
            elif event.key == pygame.K_3:
                inventory.check_slot(2, egg_item.open)
            elif event.key == pygame.K_4:
                inventory.check_slot(3, egg_item.open)
        if (event.key == pygame.K_i or event.key == pygame.K_ESCAPE) and not egg_item.open and dealer.in_range:
            if self.open_dealer:
                self.sound.play_voiceline("ShopAnytime")
            else:
                self.sound.play_voiceline("ShopBuying")
            self.open_dealer = not self.open_dealer
            if self.open_dealer:
                ui_group.add(self)
            else:
                ui_group.remove(self)


class Dealer(pygame.sprite.Sprite):
    def __init__(self, pos, group, dealer_path, wagon_path, light_player, sonar_item):
        self.wagon = wagon((pos[0], pos[1]-20), group, wagon_path)
        super().__init__(group)
        self.group = group
        self.light_player = light_player
        self.sonar_item = sonar_item
        self.pos = pos
        self.image = pygame.image.load(dealer_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (50, 50))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.visible = True
        self.obstical = True
        self.in_range = False
        self.bubble = speech_bubble(pos, group)
        self.hitbox_size = (300, 300)
        self.hitbox = Hitbox(pos, group, self.hitbox_size, self)
        Light((self.pos), 1000, 1000, 200, self.light_player, 3, self.group, self.sonar_item)
        self.max_rotation_per_frame = 3
        self.angle_last = 0

    def rotate_sprite(self, player, dealer):
        angle_now = math.degrees(
            math.atan2(dealer[1] - player[1], dealer[0] - player[0]))

        angle_diff = angle_now - math.degrees(self.angle_last)
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        max_allowed_angle_diff = self.max_rotation_per_frame
        if abs(angle_diff) > max_allowed_angle_diff:
            angle_diff = max_allowed_angle_diff if angle_diff > 0 else -max_allowed_angle_diff

        new_angle = math.radians(math.degrees(self.angle_last) + angle_diff)

        self.angle_last = new_angle

        rotated_image = pygame.transform.rotate(self.original_image, -(math.degrees(new_angle) + 90))
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.pos)


class wagon(pygame.sprite.Sprite):
    def __init__(self, pos, group, wagon_path):
        super().__init__(group)
        self.image = pygame.image.load(wagon_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=pos)
        self.obstical = True
        self.visible = True

class speech_bubble(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.surface = None
        self.font_size = 15
        self.bub = pygame.image.load(f"{path.gui}speechBubble.png").convert_alpha()
        self.back_bub = self.bub
        self.bub_rect = self.bub.get_rect(topleft=(0, 0))
        self.font = pygame.font.Font("freesansbold.ttf", self.font_size)
        self.num_text = 0
        self.text_list = ["The doors require the matching keys for unlocking.", "To replenish your fuel, make use of a fuel station.", "To buy items press -I- or -ESC-", "In the light, no fuel is consumed."]
        self.len_list = len(self.text_list) - 1
        self.calculate_bubble()
        self.image = self.draw_surface()
        self.rect = self.image.get_rect(bottomleft=pos)
        self.obstical = False
        self.visible = False
        self.num_text = -1
        self.current_time = 0
        self.last_refreshed = 0
        self.refresh_time = 3000

    def calculate_bubble(self):
        len_text = len(self.text_list[self.num_text])
        bubble_width = len_text * self.font_size / 2 + 20
        bubble_height = self.font_size + 30
        self.bub = pygame.transform.smoothscale(self.back_bub, (bubble_width, bubble_height))
        self.surface = pygame.Surface((self.bub.get_width(), self.bub.get_height()), pygame.SRCALPHA)

    def draw_surface(self):
        self.surface.blit(self.bub, self.bub_rect)
        text_box = self.font.render(self.text_list[self.num_text], True, (0, 0, 0))
        self.surface.blit(text_box, (10, 10))
        return self.surface

    def check_collision(self, player):
        if self.rect.colliderect(player):
            return True
        else:
            return False

    def change_text(self):
        if self.update_timer():
            if self.num_text + 1 > self.len_list:
                self.num_text = 0
            else:
                self.num_text += 1
        self.calculate_bubble()
        self.image = self.draw_surface()

    def update_timer(self):
        self.current_time = pygame.time.get_ticks()
        if not self.visible or self.current_time - self.last_refreshed >= self.refresh_time:
            self.last_refreshed = self.current_time
            return True
        else:
            return False












