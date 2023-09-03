import pygame

pygame.init()
pygame.mixer.init()

    sound = pygame.mixer.Sound('1_BETT_Menue.wav')  # Musikbett soll unter dem Menü laufen.
    sound.play(loops=-1)                            # Musik soll hier gelooped laufen

        button_click_sound = pygame.mixer.Sound('1_1_SOUND_Menue_NO.wav')   #Sound 'NO' soll bei beim Hoch- und Runterklicken im Hauptmenü abgespielt werden
        def play_button_click_sound('1_1_SOUND_Menue_NO.wav'):              #Funktion definiert für das Abspielen des 'NO' Sounds beim Jumpen über Menüpunkte
            button_click_sound.play()

        button_click_sound = pygame.mixer.Sound('1_1_SOUND_Menue_YES.wav')  #Sound 'YES' soll bei getroffener Auswahl im Hauptmenü abgespielt werden


        def play_button_click_sound('1_1_SOUND_Menue_YES.wav'):             # Funktion definiert für das Abspielen des 'YES' Sounds bei Auswahl eines Menüpunktes
        button_click_sound.play()





    #sound.stop()                                   # Noch dort platzieren, wo dann das Spiel richtig losgeht, zur ersten Welt.


