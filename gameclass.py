import pygame.font
import time
from menu import *
from PIL import Image
import path

class Game():
    def __init__(self,screen):
        pygame.init()

        self.running = True
        self.playing = False
        self.setup = True
        self.first_setup = True
        self.first_launch = True
        self.sound = Sound()
        self.button = Button(self,  None, self.sound,)
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.EXIT_KEY = False,False,False,False,False
        self.display = screen
        self.display_w, self.display_h = self.display.get_width(), self.display.get_height()
        path_parts = path.schrift.split('/')
        self.font_name = os.path.join(os.path.dirname(__file__), *path_parts, "BreatheFireIi.ttf")
        self.black, self.white = (0,0,0),(255,255,255)
        self.main_menu = MainMenu(self,self.sound,self.button)
        self.options = OptionsMenu(self,self.sound,self.button)
        self.controls = ControlsMenu(self, self.sound, self.button)
        self.credits = CreditsMenu(self,self.sound,self.button)
        self.quit = QuitMenu(self,self.sound,self.button)
        self.ending = EndScreen(self, self.sound, self.button)
        self.victory = VictoryScreen(self, self.sound, self.button)
        self.curr_menu = self.main_menu
        self.prev_menu = self.main_menu

        self.player_spawn = (0,0)
        self.dealer_spawn = (0,0)
        self.game_is_won = False
        self.reset_time = 0
        self.paused = False
        self.bg = False                                             # bg = Background, for the background image in menu

        self.seed = int(time.time())  # Konvertiere das Datum und die Uhrzeit in einen Seed
        self.width = 150
        self.height = 150


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.UP_KEY = True
                if event.key == pygame.K_ESCAPE:
                    self.EXIT_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY,self.EXIT_KEY = False, False, False, False,False

    def draw_text(self, text, size, x, y, clickable_button = True):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.white)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        # use clickable_button  = False to exclude from being added, so not being a clickable button
        if text not in Button.all_buttons and clickable_button:
                button = Button(self,text,x,y)
                button.name_rect = text_rect
                button.all_buttons[text] = button  # Add the button to the class-level all_buttons dictionary
                button.set_button_pos(x,y)

        self.display.blit(text_surface, text_rect)

    def draw_text_loop(self,*args,size, x,y, distance, add = True,):
        for text in args:
            self.draw_text(text,size,x,y, add)
            y += distance

    def background_screenshot(self):
        self.running = True
        self.paused = True
        screenshot = pygame.surfarray.array3d(self.display)
        screenshot = screenshot.transpose([1, 0, 2])
        img = Image.fromarray(screenshot)
        img.save(f"{path.weiteres}bg.png")
        self.bg = True

class Button():
    all_buttons = {}

    def __init__(self, game, name, sound, x=0,y=0):
        self.game = game
        self.button_name = name
        self.sound = sound
        self.clicked = False
        self.already_hovered= False
        self.once = True
        self.name_rect = None
        self.button_pos = (x,y)
        self.button_rects = []

    def set_button_name(self, name):
        self.button_name = name

    def get_button_name(self):
        return self.button_name

    def set_button_pos(self,x,y):
        self.button_pos = (x,y)

    def get_button_pos(self, button):
        return self.button_pos

    def mouse_click(self):

        for name, button in Button.all_buttons.items():
            rect_value = button.name_rect
            mouse_pos = pygame.mouse.get_pos()

            if button.name_rect is not None and rect_value.collidepoint(mouse_pos):

                if not button.already_hovered:
                    self.sound.play_sound("UPDOWN")
                    pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
                    button.already_hovered = True

                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:

                    self.set_button_name(button.button_name)
                    self.set_button_pos(*button.get_button_pos(self))
                    self.sound.play_sound("UPDOWN")
                    self.clicked = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return True
            else:
                button.already_hovered = False

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)


class Sound():

    music_volume = [1]
    sound_volume = [1]

    def __init__(self):
        pygame.mixer.init()
        self.currently_playing = None
        self.playing_music = False
        self.parent_dir = os.path.dirname(__file__)
        path_parts = path.sound.split('/')
        self.sound_dir = os.path.join(self.parent_dir, *path_parts)
        self.voice_channel = pygame.mixer.Channel(0)
        self.footsteps_channel = pygame.mixer.Channel(1)
        self.current_footsteps = True
        self.sound_effects = {}
        self.music_tracks = {}

        self.sound_setup()

    def search_file(self, file_name):
        for path, _, files in os.walk(self.sound_dir):
            if file_name in files:
                return os.path.join(path, file_name)


    def add_sound_effect(self, event, sound_filename):
        self.sound_effects[event] = sound_filename

    def add_music_track(self, event, music_filename):
        self.music_tracks[event] = music_filename

    def play_sound(self, event):
        if event in self.sound_effects:
            sound_file = pygame.mixer.Sound(self.search_file(self.sound_effects[event]))
            sound_file.set_volume(Sound.sound_volume[0])
            sound_file.play()

    def play_music(self, event):
        music_filename = self.music_tracks[event]
        pygame.mixer.music.set_volume(Sound.music_volume[0])

        if pygame.mixer.music.get_busy():
            if not self.currently_playing == music_filename:   #keep it from restarting the music when the loop is called again
                pygame.mixer.music.unload()
                pygame.mixer.music.load(self.search_file(music_filename))
                pygame.mixer.music.play(-1, fade_ms = 1500)
        else:
            pygame.mixer.music.load(self.search_file(music_filename))
            pygame.mixer.music.play(-1)
        self.currently_playing = music_filename

    def play_voiceline(self,line):
        self.voice_channel.set_volume(Sound.sound_volume[0] * 0.9)
        voice_line = pygame.mixer.Sound(self.search_file(self.sound_effects[line]))
        if self.voice_channel.get_busy():
            self.voice_channel.stop()
        self.voice_channel.play(voice_line)

    def play_footsteps(self, stop=False):
        self.footsteps_channel.set_volume(Sound.sound_volume[0] * 0.4)
        if stop:
            self.footsteps_channel.stop()
        elif not self.footsteps_channel.get_busy():
            if self.current_footsteps:                              #switching between two sets of footsteps
                footsteps_sound = pygame.mixer.Sound(self.search_file(self.sound_effects["Footsteps"]))
            else:
                footsteps_sound = pygame.mixer.Sound(self.search_file(self.sound_effects["Footsteps2"]))
            self.current_footsteps = not self.current_footsteps
            self.footsteps_channel.play(footsteps_sound)

    def sound_setup(self):
        pygame.mixer.set_num_channels(16)

        ### Music ###
        self.add_music_track("Main Menu" , "1_BETT_Menue.wav")
        self.add_music_track("level1", "2_BETT_Korianderworld.wav")
        self.add_music_track("Credits", "4_BETT_Credits.wav")
        self.add_music_track("SaveSpace","Save_Space_atmo.wav")
        self.add_music_track("Dungeon","Dungeon_ATMO_v1.0.wav")
        self.add_music_track("Moonlight","Moonlight_ATMO_v1.0.wav")
        self.add_music_track("Horns","3_BETT_Underwaterworld2_Horns.wav")

        ### Menu ###
        self.add_sound_effect("Gong", "2_SOUND_Gong_Einstieg.wav")
        self.add_sound_effect("UPDOWN", "1_1_SOUND_Menue_YES.wav")

        ### Items ###
        self.add_sound_effect("ItemPickUp", "paper_sound.wav")
        self.add_sound_effect("CoinPickUp", "SOUND_Bling_Money1_Clear_Short.wav")
        self.add_sound_effect("Echo1","SOUND_Echolot_V1.wav")
        self.add_sound_effect("Echo2", "SOUND_Echolot_V2.wav")
        self.add_sound_effect("EchoPickUp", "SOUND_Echolot_V3.wav")
        self.add_sound_effect("flame1", "SOUND_Fire_Flame_V1.wav")
        self.add_sound_effect("flame2", "SOUND_Fire_Flame_V2.wav")
        self.add_sound_effect("RangeUp", "swoosh_effect_up_shorted.wav")
        self.add_sound_effect("RangeDown", "swoosh_effect_down_shorted.wav")
        self.add_sound_effect("Key","getting_key.wav")
        self.add_sound_effect("DoorOpen","door_open.wav")
        self.add_sound_effect("DoorClosed","closed_door_sound.wav")
        self.add_sound_effect("FuelCharge","shield_recharge.wav")

        ### SHOP ###
        self.add_sound_effect("BuyItem", "SOUND_SHOP_Selection_High.wav")
        self.add_sound_effect("noMoney", "SOUND_SHOP_No_Money.wav")
        self.add_sound_effect("ShopAnytime", "Merchant_quote_-_Come_back_anytime-Kopie.wav")
        self.add_sound_effect("ShopNoMoney", "Merchant_quote_-_Not_enough_cash,_stranger.ogg")
        self.add_sound_effect("ShopThankYou", "Merchant_quote_-_Thank_you.ogg")
        self.add_sound_effect("ShopBuying", "Merchant_quote_-_What're_ya_buyin'.ogg")

        ### Ending ###
        self.add_sound_effect("SlowDeath", "darkest-dungeon-the-slow-death.mp3")
        self.add_sound_effect("Overconfidence", "darkest-dungeon-remind-yourself-that-overconfidence.mp3")
        self.add_sound_effect("Slowly", "darkest-dungeon-slowly-gently-1.mp3")
        self.add_sound_effect("NoHope", "darkest-dungeon-there-can-be-no-hope-in-this-hell.mp3")
        self.add_sound_effect("Dissappointment", "more-dust-more-ashes-more-disappointment.mp3")

        ### Victory ###
        self.add_sound_effect("Impressive", "darkest-dungeon-impressive.mp3")
        self.add_sound_effect("VictorySound", "winning_sound.wav")

        ### Footsteps ###
        self.add_sound_effect("Footsteps", "single_footstep__1_.wav")
        self.add_sound_effect("Footsteps2", "single_footstep__2_.wav")
