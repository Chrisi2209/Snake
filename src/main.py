from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import pygame

def setup_logging(name: str) -> logging.Logger:
    path_to_dir: str = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs"))
    path_to_log: str = os.path.abspath(os.path.join(path_to_dir, f"{name}.log"))

    if not os.path.exists(path_to_dir):
        os.mkdir(path_to_dir)

    file_handler: logging.FileHandler = logging.FileHandler(path_to_log)    
    file_handler.setFormatter(logging.Formatter("%(levelname)-7s %(processName)s %(threadName)s %(asctime)s %(funcName)s: %(message)s"))

    logger: logging.Logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def main():
    pygame.display.init()
    pygame.display.set_mode((600, 800))
    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    print("w")
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    print("a")
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    print("s")
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    print("d")
            
        pass

if __name__ == "__main__":
    logger: logging.Logger = setup_logging("game")
    main()