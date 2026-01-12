# camera.py
import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera_rect.topleft)
    
    # rect만 따로 변환하고 싶을 때 사용
    def apply_rect(self, rect):
        return rect.move(self.camera_rect.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_W / 2)
        y = -target.rect.centery + int(SCREEN_H / 2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_W), x)
        y = max(-(self.height - SCREEN_H), y)

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)