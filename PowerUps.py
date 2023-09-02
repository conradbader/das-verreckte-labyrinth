import pygame

class Edvanced_View():
    def __init__(self, image_path, full_image_path, light_player):
        self.light_player = light_player
        self.full_image = pygame.image.load(full_image_path).convert_alpha()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image_back = self.image
        self.inventory_image = self.image
        self.active = False

    def activate(self):
        self.active = True
        self.light_player.light_scale_factor_max = 3



class Better_Tank():
    def __init__(self, image_path, full_image_path, updgrade_image, fuel_container, player_light):
        self.player_light = player_light
        self.fuel_container = fuel_container
        self.full_image = pygame.image.load(full_image_path).convert_alpha()
        self.updgrade_image = pygame.image.load(updgrade_image).convert_alpha()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image_back = self.image
        self.inventory_image = self.image
        self.active = False

    def activate(self):
        self.active = True
        self.fuel_container.image = self.updgrade_image
        self.player_light.fuel_usage = self.player_light.fuel_usage * (2/3)
        self.player_light.fuel_reduktion = self.player_light.light_scale_factor / self.player_light.fuel_usage


class Power_Up_Bar(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path):
        super().__init__(group)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image_back = self.image
        self.rect = self.image.get_rect(center=pos)
        self.rect_back = self.image_back.get_rect(topleft=(0, 0))
        self.power_up_list = []
        self.pos_list = [(25, 26), (25, 90), (25, 156)]
        self.surface = pygame.Surface((50, 180), pygame.SRCALPHA)
        self.pay = None

    def add_power_up(self, power_up):
        if power_up not in self.power_up_list:
            self.power_up_list.append(power_up)
            self.pay = True
            power_up.activate()
        else:
            self.pay = False
            self.change_image(True, power_up)
        self.draw_bar()
        self.image = self.surface
        return self.pay

    def change_image(self, full, power_up=None):
        if full:
            power_up.image = power_up.full_image
        else:
            for power in self.power_up_list:
                power.image = power.image_back
        self.draw_bar()

    def draw_bar(self):
        self.surface.blit(self.image_back, self.rect_back)
        for i, power in enumerate(self.power_up_list):
            self.surface.blit(power.image, power.image.get_rect(center=self.pos_list[i]))
        self.image = self.surface



