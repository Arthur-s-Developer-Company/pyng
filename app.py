import pygame as pg

from classes.Menus.Menu_opcoes import Opcoes
from classes.Menus.Menu_principal import Main

"""def run_game():
    op = Opcoes()
    op.mostrar_menus()
    pg.quit()"""


def run_game():
    main = Main()
    main.mostrar_menus()
    pg.quit()


"""def run_game():
    game = Game()
    game.run()
    pg.quit()
"""
if __name__ == "__main__":
    run_game()
