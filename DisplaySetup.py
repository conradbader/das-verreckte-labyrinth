import pygame
import math

def get_screen_dim(normal_screen_size):
    monitor_info = pygame.display.Info()
    monitor_height = monitor_info.current_h
    print(monitor_info)
    adjusted_height = int(monitor_height * normal_screen_size)
    adjusted_width = adjusted_height
    scale_factor = monitor_height / 1440 * normal_screen_size
    return adjusted_width, adjusted_height, scale_factor

class Light(pygame.sprite.Sprite):

    def __init__(self, pos, width, height, max_radius, player=None, surface=None, group=None, sonar=None):
        self.scaled_surfaces = []
        if group:
            super().__init__(group)
            self.surface = player.scaled_surfaces[surface]
            self.rect = self.surface.get_rect(center=pos)
        self.pos = pos
        self.width = width
        self.height = height
        self.max_radius = max_radius
        self.black_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.black_surface.fill((0, 0, 0))
        self.visibility_surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.scaled_surface = self.visibility_surface
        self.scaled_rec = self.scaled_surface.get_rect(center=(1000, 1000))
        self.visible = False
        self.obstical = False
        self.light_scale_factor = 1
        self.light_scale_factor_max = self.light_scale_factor
        self.light_scale_factor_min = 0.08
        self.sonar = sonar
        self.fuel_usage = 0.01
        self.fuel_reduktion = self.light_scale_factor / self.fuel_usage
        self.in_light = False
        self.refueling = False
        self.refueling_factor = 3
        self.line_thickness = 4
        self.line_colour = (20, 157, 105)
        self.tank_full = False
        self.game_over = False
        self.playing_sound = False

        self.set_up_light()
        self.generate_list()


    def calculate_alpha(self, distance):
        max_alpha = 255
        min_alpha = 0
        alpha = (distance / self.max_radius) * max_alpha
        return max(min_alpha, min(max_alpha, alpha))

    def calculate_visibility_surface(self):
        for y in range(self.max_radius * 2):
            for x in range(self.max_radius * 2):
                distance = math.sqrt((x - self.max_radius) ** 2 + (y - self.max_radius) ** 2)
                if distance <= self.max_radius:
                    alpha = self.calculate_alpha(distance)
                    color_with_alpha = (0, 0, 0, alpha)
                    self.visibility_surface.set_at((x, y), color_with_alpha)
                else:
                    self.visibility_surface.set_at((x, y), (0, 0, 0, 255))

    def generate_list(self):
        for i in range(6):
            scale_factor = (i + 1) / 3
            new_width = int(self.visibility_surface.get_width() * scale_factor)
            new_height = int(self.visibility_surface.get_height() * scale_factor)
            self.scaled_surfaces.append(pygame.transform.smoothscale(self.visibility_surface, (new_width, new_height)))

    def set_up_light(self):
        self.calculate_visibility_surface()

    def blit_light(self, light_list, pos_list, surface_black):
        for i, light in enumerate(light_list):
            surface_black.blit(light.surface, pos_list[i], special_flags=pygame.BLEND_RGBA_MULT)
        if not self.in_light:
            surface_black.blit(self.scaled_surface, self.scaled_rec, special_flags=pygame.BLEND_RGBA_MULT)
        return self.black_surface

    def update_player_light(self, fuel, fuel_item, ui_group, advanced_view, station_num=0):
        if not advanced_view.active:
            self.update_normal_light(fuel_item, station_num)
        else:
            self.update_advanced_light(fuel, fuel_item, station_num)

        new_width = int(self.visibility_surface.get_width() * self.light_scale_factor)
        new_height = int(self.visibility_surface.get_height() * self.light_scale_factor)


        self.scaled_surface = pygame.transform.smoothscale(self.visibility_surface, (new_width, new_height))
        self.scaled_rec = self.scaled_surface.get_rect(center=(1000, 1000))

        if not self.tank_full:
            self.map_fuel(fuel, advanced_view)
        fuel.rect = fuel.image.get_rect(center=fuel.pos)
        self.close_game(fuel)
        ui_group.draw_ui()

    def update_normal_light(self, fuel_item, station_num):
        if not self.in_light and not self.game_over:
            self.light_scale_factor -= self.fuel_usage
        if self.refueling:
            self.light_scale_factor += self.fuel_usage * self.refueling_factor * station_num
        if fuel_item:
            self.light_scale_factor += fuel_item
        if self.light_scale_factor > self.light_scale_factor_max:
            self.light_scale_factor = self.light_scale_factor_max
            self.tank_full = True
        else:
            self.tank_full = False

    def update_advanced_light(self, fuel, fuel_item, station_num):
        if self.refueling:
            mapped_value = fuel.pos[1] - (fuel.range / self.fuel_reduktion * self.refueling_factor * station_num)
            fuel.pos = (fuel.pos[0], mapped_value)
        if fuel_item:
            mapped_value = fuel.pos[1] - (fuel.range * fuel_item)
            fuel.pos = (fuel.pos[0], mapped_value)
        if fuel.pos[1] < fuel.posY_max:
            fuel.pos = (fuel.pos[0], fuel.posY_max)
            self.tank_full = True
        else:
            self.tank_full = False



    def draw_lights(self, l_list, p_list, in_light):
        self.in_light = in_light
        if self.sonar.in_use:
            self.black_surface.fill((0, 0, 0, 0))
        else:
            self.black_surface.fill((0, 0, 0))
        return self.blit_light(l_list, p_list, self.black_surface)

    def map_fuel(self, fuel, advanced_view):
        if not advanced_view.active:
            mapping = (self.light_scale_factor - self.light_scale_factor_min) / (
                        self.light_scale_factor_max - self.light_scale_factor_min)
            mapped_value = fuel.posY_min - mapping * fuel.range
            fuel.pos = (fuel.pos[0], mapped_value)
        elif not self.in_light:
            mapping = self.fuel_reduktion / self.light_scale_factor
            mapped_value = fuel.range / mapping
            fuel.pos = (fuel.pos[0], fuel.pos[1] + mapped_value)

    def draw_fuel_line(self, player, fuel_station, surface, station):
        if self.refueling:
            if not self.playing_sound:
                self.playing_sound = True
                station.play_sound()
            angle = math.atan2(fuel_station[1] - player[1], fuel_station[0] - player[0])
            line_length = math.sqrt(
                (fuel_station[1] - player[1]) ** 2 + (fuel_station[0] - player[0]) ** 2)
            line_end_x = player[0] + line_length * math.cos(angle)
            line_end_y = player[1] + line_length * math.sin(angle)
            pygame.draw.line(surface, self.line_colour, player, (line_end_x,  line_end_y), self.line_thickness)

    def close_game(self, fuel):
        if self.light_scale_factor < self.light_scale_factor_min or fuel.pos[1] > fuel.posY_min:
            self.game_over = True

