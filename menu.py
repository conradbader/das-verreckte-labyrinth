import pygame
import sys
import os
import inspect
from random import randint,choice
import path

class Menu():
    def __init__(self, game, sound, button):
        self.game = game
        self.sound = sound
        self.button = button
        self.mid_w, self.mid_h = self.game.display_w / 2, self.game.display_h / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 300
        self.font_distance = 50
        self.font_size_header = 80
        self.font_size_cursor = 150
        self.font_size = 50
        self.once = True
        self.playing = False
        self.current_volume = 1.0
        self.resolutions = pygame.display.list_modes()
        self.current_resolution_index = 7  # Standardmäßig auf 1280x720 setzen
        self.fullscreen = False


    def blit_screen(self):
        self.game.display.blit(self.game.display, (0, 0)) #changed from self.game.window.blit(self.game.display, (0, 0)) -> Effekt?
        pygame.display.update()
        self.game.reset_keys()

    def load_bg_image(self):
        if self.game.bg:
            file_path_sc = f"{path.weiteres}bg.png"
            load_bg = pygame.image.load(file_path_sc).convert_alpha()
            image = load_bg
        else:
            file_path_background = f"{path.weiteres}BangerBackground.png"
            background_image = pygame.image.load(file_path_background).convert_alpha()
            background_image = pygame.transform.scale(background_image, (self.game.display_w, self.game.display_h))
            image = background_image
        return image

    def button_name_translate(self,button_name):
        name = button_name.get_button_name()

        if name == "Start Game":
            self.sound.play_music("level1")
            self.sound.play_sound("Gong")
            self.game.prev_menu = self.game.main_menu
            self.game.running = False
            self.playing = True
        elif name == "Options":
            self.game.prev_menu = self.game.main_menu
            self.game.curr_menu = self.game.options
        elif name == "Credits":
            self.game.prev_menu = self.game.main_menu
            self.game.curr_menu = self.game.credits
        elif name == "Quit":
            self.game.prev_menu = self.game.main_menu
            self.game.curr_menu = self.game.quit
        elif name == "NO, I am NOT Scared!":
            self.game.prev_menu = self.game.main_menu
            self.game.curr_menu = self.game.main_menu
        elif name == "YES, get me out of here!":
            pygame.quit()
            sys.exit()
        elif name == "Controls":
            self.game.prev_menu = self.game.main_menu
            self.game.curr_menu = self.game.controls
        elif name.startswith("Volume: "):
            new_sound_volume = self.sound.sound_volume[0] - 0.1
            new_music_volume = self.sound.music_volume[0] - 0.1
            if new_sound_volume < 0.0:
                new_sound_volume = 1.0
            if new_music_volume < 0.0:
                new_music_volume = 1.0
            self.sound.sound_volume[0] = new_sound_volume
            self.sound.music_volume[0] = new_music_volume
        elif name.startswith("Vollbild"):
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                self.game.display = pygame.display.set_mode(self.resolutions[self.current_resolution_index], pygame.FULLSCREEN, 8)
            else:
                self.game.display = pygame.display.set_mode(self.resolutions[self.current_resolution_index], pygame.RESIZABLE, 8)

        elif name in ("Yes, I know I can do it!", "Lets go! This was easy!"):
                self.game.setup = True
                self.game.first_setup = False
                self.game.curr_menu.run_display = False
                if name == "Lets go! This was easy!":
                    self.game.seed += 5  #generate a new seed on replay

        elif name in ("Nope, im not cut out for this!", "As you said...Im already a Hero"):
            pygame.quit()
            sys.exit()


    def move_cursor(self, UP_KEY, mouse = False):
        self.sound.play_sound("UPDOWN")

        if self.state.startswith("Volume: "):
            self.local_state = f"Volume: {self.current_volume} %"
            button_value = self.button.all_buttons[self.local_state]
        elif self.state.startswith("Vollbild"):
            self.local_state = f"Vollbild: {'Ja' if self.fullscreen else 'Nein'}"
            button_value = self.button.all_buttons[self.local_state]
        else:
            button_value = self.button.all_buttons[self.state]

        current_key = button_value.get_button_name()
        button_list = list(self.button.all_buttons.keys())
        current_index = button_list.index(current_key)

        if UP_KEY:
            add = -1
        else:
            add = 1

        next_index = (current_index + add) % len(button_list) #wrap around to the beginning
        next_key = button_list[next_index]
        next_value = self.button.all_buttons[next_key]

        if mouse:
            next_value = button_value

        self.cursor_rect.midtop = (next_value.get_button_pos(next_value)[0]+ self.offset, next_value.get_button_pos(next_value)[1])
        self.state = next_value.get_button_name()


    def draw_cursor(self):
        for button in self.button.all_buttons.values():

            if button.already_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if button.once:
                    self.state = button.get_button_name()
                    self.move_cursor(False, True)
                    button.once = False

            elif not button.already_hovered and not button.once:
                button.once = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self.game.draw_text('=', self.font_size_cursor, self.cursor_rect.x, self.cursor_rect.y, False)


    def check_input(self):
        if self.game.UP_KEY or self.game.DOWN_KEY:
            self.move_cursor(self.game.UP_KEY)

        if self.game.START_KEY:
            current_line = inspect.currentframe().f_lineno
            #print(f"menu.py/{current_line}, self.state: {self.state}")

            if self.state.startswith("Volume: "):
                self.local_state = f"Volume: {self.current_volume} %"
                button_value = self.button.all_buttons[self.local_state]
            elif self.state.startswith("Vollbild"):
                current_resolution = self.resolutions[self.current_resolution_index]
                self.local_state = f"Vollbild: {'Ja' if self.fullscreen else 'Nein'}"
                button_value = self.button.all_buttons[self.local_state]
            else:
                button_value = self.button.all_buttons[self.state]
            self.button_name_translate(button_value)

            self.state = button_value.get_button_name()
            self.button.all_buttons.clear()
            self.run_display = False

        elif self.button.mouse_click():
            self.button_name_translate(self.button)
            self.state = self.button.get_button_name()
            self.button.all_buttons.clear()
            self.run_display = False

        if self.game.EXIT_KEY and not self.game.game_is_won:
            if self.playing:
                self.game.curr_menu.run_display = False
                self.game.curr_menu = self.game.main_menu
                self.game.running = False
            else:
                self.game.BACK_KEY = True

        if self.game.BACK_KEY and not self.game.game_is_won:
            self.game.curr_menu = self.game.prev_menu
            self.button.all_buttons.clear()
            self.run_display = False

class MainMenu(Menu):
    def __init__(self, game,sound,button):
        Menu.__init__(self, game,sound,button)                   #use init func from the parent menu class
        self.state = "Start Game"
        self.cursor_rect.midtop = (self.mid_w + self.offset, self.mid_h + self.font_distance )

    def display_menu(self):
        self.run_display = True
        self.sound.play_music("Main Menu")

        if self.game.first_launch:
            self.launch_screen()

        while self.run_display:
            self.game.display.blit(self.load_bg_image(), (0, 0))


            if self.game.paused:
                self.game.draw_text("Pause Menu", self.font_size_header, self.mid_w, self.mid_h - 20, False)
            else:
                self.game.draw_text("Main Menu", self.font_size_header, self.mid_w, self.mid_h - 20, False)
                self.game.draw_text("Return: Backspace / Escape", self.font_size - 25, self.mid_w * 1.70, self.mid_h * 1.9, False)

            self.game.draw_text_loop("Start Game", "Options","Credits","Quit", size=self.font_size, x=self.mid_w, y=self.mid_h + self.font_distance, distance=self.font_distance)

            self.game.check_events()
            self.check_input()
            self.draw_cursor()
            self.blit_screen()

    def launch_screen(self):
        self.game.display.fill(self.game.black)
        self.sound.play_sound("Gong")
        self.game.draw_text("Willkommen:", self.font_size_header+30, self.mid_w, self.mid_h - 20, False)
        self.blit_screen()
        pygame.time.wait(700)


        text_to_display = "DaS vErÜcKtE LaByRiNtH"
        self.game.display.fill(self.game.black)

        for i, char in enumerate(text_to_display):
            char_font_size = self.font_size + randint(-20, 30)
            x_position = 50 + i * 40
            self.game.draw_text(char, char_font_size, x_position, self.mid_h - 20, False)
            self.blit_screen()
            pygame.time.wait(20)

        pygame.time.wait(500)
        self.game.first_launch = False

class OptionsMenu(Menu):
    def __init__(self, game,sound,button):
        Menu.__init__(self, game,sound,button)
        self.state = "Controls"
        self.sound = sound
        self.cursor_rect.midtop = (self.mid_w + self.offset, self.mid_h + self.font_distance)

    def display_menu(self):
        self.run_display = True
        self.sound.play_music("Main Menu")
        while self.run_display:
            self.game.display.fill((0, 0, 0))
            self.game.display.blit(self.load_bg_image(), (0, 0))
            self.game.draw_text("Options", self.font_size_header, self.mid_w, self.mid_h - 30, False)
            self.game.draw_text("Controls", self.font_size, self.mid_w, self.mid_h +  self.font_distance, True)

            self.current_volume = int(self.sound.sound_volume[0] * 100)
            self.game.draw_text(f"Volume: {self.current_volume} %", self.font_size, self.mid_w, self.mid_h + 2 * self.font_distance, True)
            self.game.draw_text(f"Vollbild: {'Ja' if self.fullscreen else 'Nein'}", self.font_size, self.mid_w, self.mid_h + 3 * self.font_distance, True)
            self.game.draw_text("Return: Backspace / Escape", self.font_size - 25, self.mid_w * 1.70, self.mid_h * 1.9, False)

            self.game.check_events()
            self.check_input()
            self.draw_cursor()
            self.blit_screen()



class ControlsMenu(Menu):
    def __init__(self, game,sound,button):
        Menu.__init__(self, game,sound,button)
        self.state = "Controls"
        self.cursor_rect.midtop = (self.mid_w + self.offset, self.mid_h + self.font_distance)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.display.fill((0, 0, 0))
            self.game.display.blit(self.load_bg_image(), (0, 0))
            self.game.draw_text("Controls", self.font_size_header, self.mid_w, self.mid_h - 150, False)
            self.game.draw_text("Bewege dich mit den Pfeiltasten!", self.font_size-10, self.mid_w, self.mid_h, False)
            self.game.draw_text("Erreiche den Ausgang bevor dir das Licht ausgeht!", self.font_size-10, self.mid_w, self.mid_h + 75, False)
            self.game.draw_text("Return: Backspace / Escape", self.font_size - 25, self.mid_w * 1.70, self.mid_h * 1.9, False)

            self.game.check_events()
            self.check_input()
            self.blit_screen()

class CreditsMenu(Menu):
    def __init__(self, game,sound,button):
        Menu.__init__(self, game,sound,button)
        self.state = "Credits"

    def display_menu(self):
        self.run_display = True
        self.sound.play_music("Credits")

        while self.run_display:
            self.game.check_events()

            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False

            self.game.display.fill(self.game.black)
            self.game.display.blit(self.load_bg_image(), (0, 0))

            self.game.draw_text('Game Made by:', self.font_size_header, self.mid_w, self.mid_h - 20, False)
            self.game.draw_text_loop("Lucca Kuvecke", "Conrad Bader", "Paul Bleyer", "Erik Weiß","Georg Czoske", size=self.font_size-10, x=self.mid_w,y=self.mid_h + self.font_distance, distance=self.font_distance, add = False)
            self.game.draw_text("Return: Backspace / Escape", self.font_size - 25, self.mid_w * 1.70, self.mid_h * 1.9, False)

            self.game.check_events()
            self.check_input()
            self.blit_screen()

class QuitMenu(Menu):
    def __init__(self, game,sound,button):
        Menu.__init__(self, game,sound,button)
        self.state = "NO, I am NOT Scared!"
        self.cursor_rect.midtop = (self.mid_w +  self.offset, self.mid_h + self.font_distance)

    def display_menu(self):
        self.run_display = True
        self.sound.play_music("Main Menu")
        while self.run_display:
            self.game.display.fill((0, 0, 0))
            self.game.display.blit(self.load_bg_image(), (0, 0))
            self.game.draw_text("You sure you wanna quit, fool?", self.font_size_header-20, self.mid_w, self.mid_h - self.font_distance, False)
            self.game.draw_text_loop("NO, I am NOT Scared!", "YES, get me out of here!", size=self.font_size-10, x=self.mid_w, y=self.mid_h + self.font_distance,distance=self.font_distance)
            self.game.draw_text("Return: Backspace / Escape", self.font_size - 25, self.mid_w * 1.70, self.mid_h * 1.9, False)

            self.game.check_events()
            self.check_input()
            self.draw_cursor()
            self.blit_screen()

class EndScreen(Menu):
    def __init__(self,game,sound,button):
        Menu.__init__(self, game, sound, button)
        self.state = "Yes, I know I can do it!"
        self.cursor_rect.midtop = (self.mid_w + self.offset, self.mid_h + self.font_distance)

    def ending_screen(self):
        self.game.display.fill(self.game.black)
        self.blit_screen()

        text_to_display = "... So that is it,hm?"

        for i, char in enumerate(text_to_display):
            self.game.draw_text(char, self.font_size+10, 50 + i * 40, self.mid_h - 20, False)

            pygame.time.wait(80)
            self.blit_screen()

        pygame.time.wait(3500)

    def display_menu(self):
        self.run_display = True
        self.playing = False
        self.sound.play_music("Credits")

        ending_line = choice(["SlowDeath","Overconfidence", "Slowly", "NoHope", "Dissappointment"])
        self.sound.play_sound(ending_line)
        self.ending_screen()

        time = int(pygame.time.get_ticks() // 60000) - self.game.reset_time

        while self.run_display:
            self.game.display.fill(self.game.black)
            self.game.draw_text("Do you wanna try Again?", self.font_size_header - 20, self.mid_w,self.mid_h - self.font_distance, False)
            self.game.draw_text_loop("Yes, I know I can do it!", "Nope, im not cut out for this!", size=self.font_size - 10,x=self.mid_w, y=self.mid_h + self.font_distance, distance=self.font_distance)
            self.game.draw_text(f"You lived for: {time} minutes", self.font_size - 20, self.mid_w,self.mid_h + 250, False)
            self.game.draw_text(f"Map seed: {self.game.seed}", self.font_size - 20, self.mid_w, self.mid_h + 280, False)

            self.game.check_events()
            self.check_input()
            self.draw_cursor()
            self.blit_screen()

class VictoryScreen(Menu):
    def __init__(self,game,sound,button):
        Menu.__init__(self, game, sound, button)
        self.state = "Lets go! This was easy!"
        self.cursor_rect.midtop = (self.mid_w + self.offset, self.mid_h + self.font_distance)

    def Victory_screen(self):
        self.game.display.fill(self.game.black)
        self.game.draw_text("You actually did it!", self.font_size_header - 20, self.mid_w,self.mid_h - self.font_distance, False)
        self.sound.play_sound("VictorySound")
        self.blit_screen()

        pygame.time.wait(3500)

    def display_menu(self):
        self.run_display = True
        self.sound.play_music("Credits")

        victory_line = choice(["Impressive"])
        self.sound.play_sound(victory_line)
        self.Victory_screen()

        time = int(pygame.time.get_ticks() // 60000) - self.game.reset_time

        while self.run_display:
            self.game.display.fill(self.game.black)
            self.game.draw_text("You earned your place among Heroes!", self.font_size_header - 20, self.mid_w,self.mid_h - 5*self.font_distance, False)
            self.game.draw_text("You wanna try Again?", self.font_size_header - 20,self.mid_w, self.mid_h - 3*self.font_distance, False)
            self.game.draw_text_loop("Lets go! This was easy!", "As you said...Im already a Hero", size=self.font_size - 10,x=self.mid_w, y=self.mid_h + self.font_distance, distance=self.font_distance)
            self.game.draw_text(f"It took you: {time} minutes to escape", self.font_size - 20, self.mid_w,self.mid_h + 250, False)
            self.game.draw_text(f"Map seed: {self.game.seed}", self.font_size - 20, self.mid_w, self.mid_h + 280,False)

            self.game.check_events()
            self.check_input()
            self.draw_cursor()
            self.blit_screen()

