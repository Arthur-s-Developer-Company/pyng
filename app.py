from classes.Game import Game
import pygame as pg

def run_game():
    game = Game()
    game.run()
    pg.quit()

if __name__ == "__main__":
    run_game()