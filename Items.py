import pygame
from random import choice
import webbrowser
from DisplaySetup import Light
import path


class Item_List():
    def __init__(self, camera, player, sprite, sonar_player):
        self.camera = camera
        self.player = player
        self.sprite = sprite
        self.sonar_player = sonar_player

    def item_effect(self, item_list):
        for item in item_list:
            item.effect(self.camera, self.player, self.sprite, self.sonar_player)


class Fuel_Item(pygame.sprite.Sprite):

    def __init__(self, pos, group, image_path, tone, fuel, obstical, light_player, sound, ui_group,advanced_view):
        super().__init__(group)
        self.pos = pos
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.obstical = obstical
        self.visible = True
        self.sound = sound
        self.tone = tone
        self.light_player = light_player
        self.ui_group = ui_group
        self.fuel = fuel
        self.advanced_view = advanced_view
        self.refill_factor = 0.3

    def collect_item(self, count):
        self.sound.play_sound(self.tone)
        self.light_player.update_player_light(self.fuel, self.refill_factor, self.ui_group, self.advanced_view)


class Coin_Item(pygame.sprite.Sprite):

    money = 0

    def __init__(self, pos, group, ui_group, image_path, tone, inventory_path, sound, obstical=bool):
        super().__init__(group)
        self.ui_group = ui_group
        self.ui_image = pygame.image.load(inventory_path).convert_alpha()
        self.ui_rec = self.ui_image.get_rect(center=(800, 100))
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.obstical = obstical
        self.visible = True
        self.sound = sound
        self.tone = tone
        self.type = "coin"

    def collect_item(self, count):
        self.sound.play_sound(self.tone)
        Coin_Item.money += count

    def use_coins(self, price):
        self.sound.play_voiceline("ShopThankYou")
        self.sound.play_sound("BuyItem")
        Coin_Item.money -= price

    def check_coins(self, price):
        if Coin_Item.money >= price:
            return True
        else:
            self.sound.play_voiceline("ShopNoMoney")
            self.sound.play_sound("CoinPickUp")
            return False

    def reset(self):
        Coin_Item.money = 0


class Range_Item(pygame.sprite.Sprite):

    used = False
    in_use = False
    last_use_time = 0

    def __init__(self, pos, group, image_path, tone, inventory_path, obstical, inventory,sound):
        super().__init__(group)
        self.inventory_image = pygame.image.load(inventory_path).convert_alpha()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.obstical = obstical
        self.visible = True
        self.sound = sound
        self.tone = tone
        self.type = "range"
        self.timer = 3000
        self.inventory = inventory

    def effect(self, camera, player, sprite, sonar_player):
        if Range_Item.used and not Range_Item.in_use:
            self.sound.play_sound("RangeUp")
            Range_Item.last_use_time = pygame.time.get_ticks()
            camera.view(player)
            Range_Item.in_use = True
            Range_Item.used = False
        if Range_Item.in_use:
            current_time = pygame.time.get_ticks()
            if current_time - Range_Item.last_use_time >= self.timer:
                self.sound.play_sound("RangeDown")
                camera.view(player)
                Range_Item.last_use_time = 0
                Range_Item.in_use = False

    def use_item(self):
        if not Range_Item.in_use:
            Range_Item.used = True
            self.inventory.update_inventory(-1, self)

    def collect_item(self, count):
        self.sound.play_sound(self.tone)
        self.inventory.update_inventory(count, self)

    def reset(self):
        Range_Item.used = False
        Range_Item.in_use = False
        Range_Item.last_use_time = 0

class Sonar_Item(Range_Item):

    used = False
    in_use = False
    last_use_time = 0

    def __init__(self, pos, group, image_path, tone, inventory_path, obstical, inventory, sound, ui):
        super().__init__(pos, group, image_path, tone, inventory_path, obstical, inventory, sound)
        self.type = "sonar"
        self.timer = 3000
        self.ui = ui
        Sonar_Item.in_use = False

    def effect(self, camera, player, sprite, sonar_player):
        if Sonar_Item.used and not Sonar_Item.in_use:
            Sonar_Item.last_use_time = pygame.time.get_ticks()
            camera.add_sprite(sprite, player)
            camera.sonar_in_use = True
            self.ui.add_sprite(sonar_player)
            Sonar_Item.in_use = True
            Sonar_Item.used = False
        if Sonar_Item.in_use:
            current_time = pygame.time.get_ticks()
            if current_time - Sonar_Item.last_use_time >= self.timer:
                self.ui.remove_sprite(sonar_player)
                camera.remove_sprite(sprite, player)
                camera.sonar_in_use = False
                Sonar_Item.last_use_time = 0
                Sonar_Item.in_use = False

    def use_item(self):
        if not Sonar_Item.in_use:
            sonar_sound = choice(["Echo1", "Echo2"])
            self.sound.play_sound(sonar_sound)
            Sonar_Item.used = True
            self.inventory.update_inventory(-1, self)

    def reset(self):
        Sonar_Item.used = False
        Sonar_Item.in_use = False
        Sonar_Item.last_use_time = 0


class Egg_Item():
    def __init__(self, inventory_path, inventory, ui_group):
        self.inventory_image = pygame.image.load(inventory_path).convert_alpha()
        self.inventory = inventory
        self.qr = QR_Code(f"{path.weiteres}QR.png", ui_group)
        self.type = "egg"
        self.open = False

    def use_item(self):
        if not self.open:
            self.qr.open_window()
            self.open = True
        else:
            self.inventory.update_inventory(-1, self)
            self.qr.close_window()
            self.open = False

    def check_collision(self):
        self.qr.check_button()


class QR_Code(pygame.sprite.Sprite):
    def __init__(self, image_path, ui_group):
        super().__init__()
        self.font_big = pygame.font.Font(None, 100)
        self.font_small = pygame.font.Font(None, 25)
        self.text = self.font_big.render("OR", True, (255, 255, 255))
        self.button_text = self.font_small.render("Open Web Link", True, (255, 255, 255))
        self.button_image = pygame.image.load(f"{path.gui}Button_egg.png").convert()
        self.button_image_back = self.button_image
        self.button_image_pressed = pygame.image.load(f"{path.gui}Button_egg_pressed.png").convert()
        self.button_rec = self.button_image.get_rect(center=(250, 650))
        self.ui_group = ui_group
        self.surface = pygame.Surface((500, 700), pygame.SRCALPHA)
        self.qr = pygame.image.load(image_path).convert()
        self.qr = pygame.transform.smoothscale(self.qr, (500, 500))
        self.qr_rect = self.qr.get_rect(topleft=(0, 0))
        self.image = self.qr
        self.rect = self.surface.get_rect(center=(500, 500))
        self.link = r"https://wokwi.com/projects/343969264097559122"
        self.button_cooldown = 400
        self.last_button_click_time = 0

    def open_window(self):
        self.draw_surface()
        self.ui_group.add_sprite(self)

    def close_window(self):
        self.ui_group.remove_sprite(self)

    def draw_surface(self):
        self.surface.blit(self.qr, self.qr_rect)
        self.surface.blit(self.text, (200, 535))
        self.surface.blit(self.button_image, self.button_rec)
        self.surface.blit(self.button_text, (188, 642))
        self.image = self.surface

    def check_button(self):
        current_time = pygame.time.get_ticks()
        if self.button_rec.collidepoint(self.get_mouse_pos()) and pygame.mouse.get_pressed()[0]:
            if current_time - self.last_button_click_time >= self.button_cooldown:
                self.button_image = self.button_image_pressed
                self.last_button_click_time = current_time
                self.draw_surface()
        elif self.button_image != self.button_image_back and current_time - self.last_button_click_time >= self.button_cooldown:
            webbrowser.open(self.link)
            self.button_image = self.button_image_back
            self.draw_surface()


    def get_mouse_pos(self):
        pos_mouse = [0, 0]
        pos_x, pos_y = pygame.mouse.get_pos()
        pos_mouse[0] = pos_x - self.rect.left
        pos_mouse[1] = pos_y - self.rect.top
        return pos_mouse


class Fuel_Station(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path, tone, inventory_path, obstical, inventory, light_player, sonar_item, player, sound):
        super().__init__(group)
        self.group = group
        self.pos = pos
        self.light_player = light_player
        self.player = player
        self.sonar_item = sonar_item
        self.image_path = image_path
        self.inventory_path = inventory_path
        self.inventory_image = pygame.image.load(inventory_path).convert_alpha()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.obstical = obstical
        self.visible = True
        self.sound = sound
        self.tone = tone
        self.inventory = inventory
        self.size = (256, 256)
        self.hitbox = Hitbox(pos, group, self.size)
        self.type = "station"
        self.used = False
        self.set_up_light()

    def use_item(self):
        self.inventory.update_inventory(-1, self)
        self.used = True

    def effect(self, camera, player, sprite, sonar_player):
        if self.used:
            Fuel_Station((player.rect.center), self.group, self.image_path, self.tone, self.inventory_path, self.obstical, self.inventory, self.light_player, self.sonar_item, self.player, self.sound)
            self.used = False

    def play_sound(self):
        self.sound.play_sound("FuelCharge")

    def set_up_light(self):
        self.group.add_sprite(Light((self.pos), 1000, 1000, 200, self.light_player, 2, self.group, self.sonar_item), self.player)
        self.group.remove_sprite(self.player, self.player)
        self.group.add_sprite(self.player, self.player)


class Hitbox(pygame.sprite.Sprite):
    def __init__(self, pos, group, size=(256, 256), dealer=None):
        super().__init__(group)
        self.pos = pos
        self.size = size
        self.visible = False
        self.obstical = False
        self.image = pygame.Surface(self.size)
        self.rect = self.image.get_rect(center=self.pos)
        self.colliding = False
        self.dealer = dealer


class Victory_Item(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path, game):
        super().__init__(group)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.obstical = True
        self.visible = True
        self.game = game


    def collect_item(self,count):
        self.game.game_is_won = True

class Sound_Item(pygame.sprite.Sprite):
    def __init__(self, pos, group, game, music, collectable, type, dir):
        super().__init__(group)
        self.dir = dir
        self.position_type = type
        self.game = game
        self.pos = pos
        self.size = self.cal_size()
        self.image = pygame.Surface(self.size)
        self.rect = self.calculate_rect_position()
        self.image.fill((255, 255, 255))
        self.music = music
        self.collectable = collectable
        self.visible = False
        self.obstical = True

    def calculate_rect_position(self):
        if self.position_type == "top":
            return self.image.get_rect(midtop=self.pos)
        elif self.position_type == "bottom":
            return self.image.get_rect(midbottom=self.pos)
        elif self.position_type == "left":
            return self.image.get_rect(midleft=self.pos)
        elif self.position_type == "right":
            return self.image.get_rect(midright=self.pos)

    def cal_size(self):
        if self.dir == "up/down":
            size = (64, 32)
        else:
            size = (32, 64)
        return size

    def collect_item(self, count):
        if self.collectable:
            self.game.sound.play_music(self.music)











