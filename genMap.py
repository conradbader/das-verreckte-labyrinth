from array_gen import *
from random import randint

from gameObjects import *
from Items import *
from dealer import *
from UI import *
import path


class Maze:
    def __init__(self, w, h, size, seed):
        self.cell_size = size
        self.window_width = w * self.cell_size
        self.window_height = h * self.cell_size
        self.seed = seed
        self.maze_height = h
        self.maze_width = w
        self.num_regions = 6
        self.wall_name = list({f"W_{i}" for i in range(1, self.num_regions + 1)} | {f"WW{i}" for i in range(1, self.num_regions + 1)} | {f"KW{i}" for i in range(1, self.num_regions + 1)} | {"WWW"})
        self.path_name = list({f"P_{i}" for i in range(1, self.num_regions + 1)} | {f"K_{i}" for i in range(1, self.num_regions + 1)} | {f"s_{i}" for i in range(1, self.num_regions + 1)} | {f"PW{i}" for i in range(1, self.num_regions + 1)})
        self.start_name = "S_1"  # nur der erste Start ist ein echter Start
        self.around_start_name = "s_1" # nur der erste Start Bereich ist ein echter Start Bereich
        self.finish_name = {f"E_{i}" for i in range(1, self.num_regions + 1)}
        self.dealer_name = {f"D_{i}" for i in range(1, self.num_regions + 1)}
        self.key_location = list({f"KY{i+1}" for i in range(1, self.num_regions + 1)})
        self.around_finish_name = {f"e_{self.num_regions}"}  # nur der letzte End-Bereich ist ein echter End-Bereich
        self.fake_door = "tU1", "tD1", "tL1", "tR1"
        self.dealer_list = []


    def get_texture_for_tile(self, tile_type):

        tile_textures = {
            # Path textures
            "P_2": random.choice([f"{path.bereiche}Bereich2/floor2.png", f"{path.bereiche}bereich2/floor2.png", f"{path.bereiche}bereich2/floor3.png"]),
            "P_3": f"{path.bereiche}Bereich3/floor.png",

            "DefaultPath": random.choice([f"{path.bereiche}Bereich2/floor2.png", f"{path.bereiche}bereich2/floor2.png", f"{path.bereiche}bereich2/floor3.png"]),

            "K_1": f"{path.knotenpunkte}knotenpunkt1/floor.png",
            "K_2": f"{path.knotenpunkte}knotenpunkt2/floor.png",
            "K_3": f"{path.knotenpunkte}knotenpunkt3/floor.png",
            "K_4": f"{path.knotenpunkte}knotenpunkt4/floor.png",
            "K_5": f"{path.knotenpunkte}knotenpunkt5/floor.png",
            "K_6": f"{path.knotenpunkte}knotenpunkt6/floor.png",

            "KY2": f"{path.bereiche}Bereich1/Bereich1_Weg_Grid_A_12.png",
            "KY3": random.choice([f"{path.bereiche}Bereich2/floor2.png", f"{path.bereiche}bereich2/floor2.png", f"{path.bereiche}bereich2/floor3.png"]),
            "KY4": f"{path.bereiche}Bereich3/floor.png",
            "KY5": random.choice([f"{path.bereiche}Bereich2/floor2.png", f"{path.bereiche}bereich2/floor2.png", f"{path.bereiche}bereich2/floor3.png"]),

            "KW1": f"{path.knotenpunkte}knotenpunkt1/wall.png",
            "KW2": f"{path.knotenpunkte}knotenpunkt2/wall.png",
            "KW3": f"{path.knotenpunkte}knotenpunkt3/wall.png",
            "KW4": f"{path.knotenpunkte}knotenpunkt4/wall.png",
            "KW5": f"{path.knotenpunkte}knotenpunkt5/wall.png",
            "KW6": f"{path.knotenpunkte}knotenpunkt6/wall.png",

            "self.around_finish_name[0]": random.choice([f"{path.bereiche}Bereich2/floor2.png", f"{path.bereiche}bereich2/floor2.png", f"{path.bereiche}bereich2/floor3.png"]),

            # Wall textures
            "WWW": random.choice([f"{path.www}Wall_1.png", f"{path.www}Wall_2.png", f"{path.www}Wall_3.png"]),
            "W_1": f"{path.bereiche}Bereich1/leaves_birch_colored.png",
            "W_2": random.choice([f"{path.bereiche}Bereich2/stonebrick.png", f"{path.bereiche}Bereich2/stonebrick_carved.png", f"{path.bereiche}Bereich2/stonebrick_cracked.png",f"{path.bereiche}Bereich2/stonebrick_mossy.png",f"{path.bereiche}Bereich2/stonebrick_cracked_2.png",f"{path.bereiche}Bereich2/stonebrick_cracked_3.png",f"{path.bereiche}Bereich2/stonebrick_moss_2.png",f"{path.bereiche}Bereich2/stonebrick_moss_3.png",f"{path.bereiche}Bereich2/stonebrick_NOTcarved.png",f"{path.bereiche}Bereich2/stonebrick_NOTcarved_mossy.png" ]),
            "W_3": random.choice([f"{path.bereiche}Bereich3/red_nether_brick.png"]),

            "WW1": f"{path.bereiche}Bereich1/leaves_birch_colored.png",
            "WW2": random.choice([f"{path.bereiche}Bereich2/stonebrick.png", f"{path.bereiche}Bereich2/stonebrick_carved.png", f"{path.bereiche}Bereich2/stonebrick_cracked.png", f"{path.bereiche}Bereich2/stonebrick_mossy.png"]),
            "WW3": random.choice([f"{path.bereiche}Bereich3/red_nether_brick.png"]),

            "DefaultWall" : random.choice([f"{path.www}Wall_1.png", f"{path.www}Wall_2.png", f"{path.www}Wall_3.png"]),

            # Lamp/Torch Texture
            "L_1": f"{path.bereiche}Bereich1/Lamp_1.png",
            "L_2": f"{path.bereiche}Bereich2/redstone_lamp_on.png",
            "L_3": f"{path.bereiche}Bereich3/red_nether_brick_lamp.png",

            "DefaultLamp": f"{path.bereiche}Fackel.png",

            #Victory Texture
            **{key: f"{path.bereiche}Victory_tile.png" for key in self.finish_name},

            #Start always S_1
            "S_1": f"{path.bereiche}Bereich1/Bereich1_Weg_Grid_A_12.png",
        }

        return tile_textures.get(tile_type, f"{path.bereiche}error.png") #"Bereich1_Weg_Grid_A_1.png" Als error "Erkennung"

    def fill_up_textures(self, maze, file_name):
        window = pygame.Surface((self.window_width, self.window_height))

        wall_image = pygame.image.load(f"{path.bereiche}Blue_tile.png").convert()
        path_image = pygame.image.load(f"{path.bereiche}Black_tile.png").convert()


        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell = maze[y][x]
                if cell in self.wall_name:
                    window.blit(wall_image, (x * self.cell_size, y * self.cell_size))
                elif cell in self.path_name:
                    window.blit(path_image, (x * self.cell_size, y * self.cell_size))
        pygame.image.save(window, file_name)

    def return_array(self):
        map = return_map(self.maze_width, self.maze_height, self.num_regions, self.seed)
        return map

    def render_map(self,camera_group,light_player,sonar_Item,game,ui_group,advanced_view,inventory,fuel, coin_item,coin_count, range_item, power_up_bar,better_tank, egg_item, key_chain):

        generated_maze_array = self.return_array()

        # "Hintergrund" Für das Sonar Item
        for i in range(self.maze_width):
            for j in range(self.maze_height):
                tile_type = generated_maze_array[i][j]
                tile_texture = self.get_texture_for_tile(tile_type)

                posX = j * self.cell_size
                posY = i * self.cell_size

                # Bestimmen der Texturnummer basierend auf der aktuellen Position (j und i)
                texture_number = (i % 4) * 4 + (j % 4) + 1
                variation = random.choice(["A", "B", "C"])

                ### Path Tiles ###
                if tile_type in self.path_name or tile_type in self.around_finish_name or tile_type in self.around_start_name or tile_type in self.key_location or tile_type in self.fake_door:
                    if tile_type == "P_1" or tile_type == "s_1" or tile_type.startswith("t"):
                        tile_texture = f"{path.bereiche}Bereich1/Bereich1_Weg_Grid_{variation}_{texture_number}.png"

                    elif self.get_texture_for_tile(tile_type) == f"{path.bereiche}error.png":
                        tile_texture = self.get_texture_for_tile("DefaultPath")

                    key_placed = False
                    Maze_Obstacle((posX, posY), camera_group, tile_texture, False)
                    if tile_type in self.key_location:
                        Key((posX, posY), camera_group, f"{path.items}KeyFolder", game.sound, "Key", key_chain, light_player,
                            sonar_Item, tile_type)
                        key_placed = True
                    if not key_placed:
                        if randint(1, 1000) <= 25:
                            Fuel_Item((posX, posY), camera_group, f"{path.items}fire.png", "flame1", fuel, True, light_player, game.sound,ui_group, advanced_view)
                        elif randint(1, 1000) <= 15:
                            Range_Item((posX, posY), camera_group, f"{path.items}scroll_ground.png", "ItemPickUp", f"{path.items}scroll_inventory.png", True, inventory, game.sound)
                        elif randint(1, 1000) <= 50:
                            Coin_Item((posX, posY), camera_group, ui_group, f"{path.items}emerald_ground.png", "CoinPickUp", f"{path.items}emerald_inventory.png",game.sound, True)
                        elif randint(1, 1000) <= 10:
                            Sonar_Item((posX, posY), camera_group, f"{path.items}Sonar_ground.png", "EchoPickUp", f"{path.items}Sonar_inventory.png", True,inventory, game.sound, ui_group)

                ### Player objects with predetermined position ###
                elif tile_type in self.start_name:
                    game.player_spawn = (posX, posY)
                    Maze_Obstacle((posX, posY), camera_group, tile_texture, False)
                elif tile_type in self.finish_name:
                    Victory_Item((posX, posY), camera_group, tile_texture, game)
                elif tile_type in self.dealer_name:
                    game.dealer_spawn = (posX, posY)
                    self.dealer_list.append(
                        Dealer((posX, posY), camera_group, f"{path.weiteres}Dealer.png", f"{path.weiteres}Dealer_wagon.png", light_player, sonar_Item))

                elif tile_type.startswith("T") or tile_type.startswith("t"):
                    floor_image = self.get_texture_for_tile("K_1")
                    Maze_Obstacle((posX, posY), camera_group, floor_image, False)
                    if tile_type.startswith("TU") or tile_type.startswith("tU"):
                        direction = Direction.UP
                    elif tile_type.startswith("TD") or tile_type.startswith("tD"):
                        direction = Direction.DOWN
                    elif tile_type.startswith("TL") or tile_type.startswith("tL"):
                        direction = Direction.LEFT
                    elif tile_type.startswith("TR") or tile_type.startswith("tR"):
                        direction = Direction.RIGHT
                    if tile_type.startswith("T"):
                        Door((posX, posY), camera_group, f"{path.animation}doorAnimation", direction, key_chain, game, tile_type)  # Richtung in welche die Tür führt
                    else:
                        door = Door((posX, posY), camera_group, f"{path.animation}doorAnimation", direction, key_chain, game, tile_type)
                        door.sound_item_1.collectable = True
                        door.sound_item_2.collectable = True
                        camera_group.remove(door)

                elif tile_type in self.wall_name:
                    if randint(1,100) == 1:
                        if tile_type == "W_1":
                            lamp_tile = "L_1"
                        elif tile_type == "W_2":
                            lamp_tile = "L_2"
                        elif tile_type == "W_3":
                            lamp_tile = "L_3"
                        else:
                            lamp_tile = "DefaultLamp"
                        tile_texture = self.get_texture_for_tile(lamp_tile)
                        Light((posX, posY), 1000, 1000, 50, light_player, randint(0, 1), camera_group, sonar_Item)

                    elif self.get_texture_for_tile(tile_type) == f"{path.bereiche}error.png":
                        tile_texture = self.get_texture_for_tile("DefaultWall")

                    Maze_Obstacle((posX, posY), camera_group, tile_texture, True)

                else:
                    Maze_Obstacle((posX, posY), camera_group, f"{path.bereiche}error.png", False)       #If no name found, set it as a path as to not block a possible way
                    print(f" Bei dem Tile: {tile_type} Ist ein Fehler aufgetreten. Am ort: {posX/64}x{posY/64} ")

        for dealer in self.dealer_list:
            camera_group.remove(dealer.wagon)
            camera_group.remove(dealer.bubble)
            camera_group.remove(dealer)
            camera_group.add(dealer.wagon)
            camera_group.add(dealer)
            camera_group.add(dealer.bubble)
