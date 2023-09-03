from genMap import *
from gameObjects import *
from Items import *
from dealer import *
from PowerUps import *
from door import *

from gameclass import *
from UI import *

import os
os.environ['SDL_RENDER_DRIVER'] = 'software'

import pygame.display
import path

pygame.mixer.pre_init(48000, -16, 2, 1024) #frequency = 44,1 kHz leads to audio glitching
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

light_timer = pygame.USEREVENT + 1
pygame.time.set_timer(light_timer, 300)

screen = pygame.display.set_mode((1000, 1000), pygame.RESIZABLE | pygame.DOUBLEBUF, 8)

game = Game(screen)

fps_count = 60

while True:
    if __name__ == '__main__':
        if game.setup:
            if not game.first_setup:

                screen.fill((0,0,0))
                pygame.display.update()

                light_player.game_over = False
                game.game_is_won = False
                game.reset_time = int(pygame.time.get_ticks() // 60000)

                game.sound.play_music("level1")
                coin_item.reset()
                sonar_Item.reset()
                range_item.reset()
                key.reset()
                camera_group.empty()
                ui_group.empty()


            maze_object = Maze(game.width, game.height, 64, game.seed)   # maze_width, maze_height, cell Size/resolution, Seed
            maze_object.fill_up_textures(maze_object.return_array(), f"{path.weiteres}Map.png")

            camera_group = Camera_Group(1)                                 # original Zoom
            ui_group = UI_Group()


            maze_sonar = Extra((-32, -32), f"{path.weiteres}Map.png", False, False, False)
            sonar_player = Extra((500, 500), f"{path.items}sonar_player.png", False, True, True)

            fuel_container = Fuel_Container((50, 902), ui_group, f"{path.gui}FuelContainer")
            fuel = Fuel_Container((50, 902), ui_group, f"{path.animation}Fuel")

            key_chain = Key_Inv((50, 70), ui_group, f"{path.gui}KeyChain")
            inventory = Inventory((500, 945), ui_group, f"{path.gui}inventory.png")
            sonar_Item = Sonar_Item((-2000, -2000), camera_group, f"{path.items}Sonar_ground.png", "ItemPickUp", f"{path.items}Sonar_inventory.png", True, inventory, game.sound, ui_group)
            egg_item = Egg_Item(f"{path.items}EasterEgg.png", inventory, ui_group)

            light_player = Light((500, 500), 2000, 2000, 400, None, None, None, sonar_Item)                  # 400 = Start-Sichtweite

            power_up_bar = Power_Up_Bar((930, 250), ui_group, f"{path.gui}PowerUPBar.png")
            better_tank = Better_Tank(f"{path.gui}BetterTank.png", f"{path.gui}BetterTank_full.png", f"{path.gui}Füllstand_full.png", fuel_container, light_player)
            advanced_view = Edvanced_View(f"{path.gui}AdvancedView.png", f"{path.gui}AdvancedView_full.png", light_player)
            door = Door((-2000, -2000), camera_group, f"{path.animation}doorAnimation", Direction.RIGHT, key_chain, game, "door1")    # Richtung in welche die Tür führt
            key = Key((-2000, -2000), camera_group, f"{path.items}KeyFolder", game.sound, "Key", key_chain, light_player, sonar_Item, "KY2")

            coin_item = Coin_Item((-2000, -2000), camera_group, ui_group, f"{path.items}emerald_ground.png", "CoinPickUp", f"{path.items}emerald_inventory.png",game.sound, True)
            coin_count = Coin_Count((930, 70), ui_group, f"{path.items}emerald_inventory.png", coin_item)

            range_item = Range_Item((-2000, -2000), camera_group, f"{path.items}scroll_ground.png", "ItemPickUp", f"{path.items}scroll_inventory.png", True,inventory, game.sound)

            maze_object.render_map(camera_group,light_player,sonar_Item,game,ui_group,advanced_view,inventory,fuel, coin_item,coin_count, range_item, power_up_bar,better_tank, egg_item,key_chain)

            main_player = Player(game.player_spawn, camera_group, 5, f"{path.animation}AnimationPlayer", False, game.sound)
            fuel_station = Fuel_Station(game.player_spawn, camera_group, f"{path.items}FuelStation.png", "EchoPickUp",f"{path.items}FuelStation.png", False, inventory, light_player, sonar_Item, main_player,game.sound)
            items = Item_List(camera_group, main_player, maze_sonar, sonar_player)


            dealer_shop = Dealer_Shop(game.dealer_spawn, f"{path.gui}DealerBackground.png", f"{path.gui}Button_shop.png", f"{path.gui}Button_shop_pressed.png",game.sound, inventory,  coin_item, coin_count, sonar_Item, range_item, advanced_view, power_up_bar, better_tank, egg_item, fuel_station)
            dealer = Dealer(game.dealer_spawn, camera_group, f"{path.weiteres}Dealer.png", f"{path.weiteres}Dealer_wagon.png", light_player, sonar_Item)

            Maze_Obstacle((-2000, -2000), camera_group,f"{path.www}wall_1.png", True)
            camera_group.fill_up_surface()

            game.setup = False


            # Funktion, um den aktuellen Spielzustand zu extrahieren
            def get_game_state():
                state = {
                    "player_position": main_player.pos,
                    "visible_items": [],  # Hier können Sie eine Liste von sichtbaren Items hinzufügen
                    "player_light_radius": light_player.light_radius,
                    # Fügen Sie hier weitere relevante Informationen hinzu
                }
                return state


            # Funktion, um Aktionen auszuführen
            def perform_action(action):
                if action == "MOVE_UP":
                    main_player.move_up()
                elif action == "MOVE_DOWN":
                    main_player.move_down()
                # ... Fügen Sie hier weitere Aktionen hinzu


            # Funktion, um eine Belohnung oder Strafe basierend auf dem Ergebnis der Aktion zurückzugeben
            def get_reward():
                reward = 0
                # Beispiel: Wenn der Spieler ein Item aufnimmt, erhöhen Sie die Belohnung
                # if item_collected:
                #     reward += 10
                # ... Fügen Sie hier weitere Belohnungsbedingungen hinzu
                return reward


            # Funktion, um zu überprüfen, ob das Spiel beendet ist
            def is_game_over():
                return light_player.game_over or game.game_is_won


            # Funktionen, um das Spiel zu initialisieren und neu zu starten
            def initialize_game():
            # Hier können Sie den Code aus dem Hauptteil von main.py verwenden, um das Spiel zu initialisieren
                return None

            def restart_game():
            # Hier können Sie den Code verwenden, um das Spiel zurückzusetzen und von vorne zu beginnen
                return None

        ### Start of the Game loop ###
        while game.running:
            game.curr_menu.display_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and advanced_view.active and not light_player.in_light:
                if event.button == 4 and light_player.light_scale_factor + 0.05 <= light_player.light_scale_factor_max:
                    light_player.light_scale_factor += 0.05
                elif event.button == 5 and light_player.light_scale_factor - 0.05 >= light_player.light_scale_factor_min:
                    light_player.light_scale_factor -= 0.05

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not dealer.in_range:
                    game.background_screenshot()
                    while game.running:
                        game.curr_menu.display_menu()

                dealer_shop.inventory_check(event, inventory, ui_group, egg_item, dealer) #check for opnening Dealer aswell as Item activation

            if event.type == light_timer and not dealer_shop.open_dealer and not egg_item.open:
                if light_player.game_over:
                    game.ending.display_menu()
                else:
                    light_player.update_player_light(fuel, 0, ui_group, advanced_view, len(camera_group.num_refuel_station))

        if not dealer_shop.open_dealer and not dealer_shop.is_button_pressed and not egg_item.open:
            items.item_effect([range_item, sonar_Item, fuel_station])
            fuel.animate()
            main_player.animate()
            camera_group.draw_camera(light_player, main_player, dealer, fuel_station)
        elif not egg_item.open:
            dealer_shop.check_Collision()
        else:
            egg_item.check_collision()
        coin_count.update_count()
        ui_group.draw_ui()

        if game.game_is_won:
            game.victory.display_menu()
        pygame.display.update()
        clock.tick(120)



