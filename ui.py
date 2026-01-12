# ui.py
import pygame
from settings import *

def draw_bar(surface, x, y, current, max_val, color, width, height):
    # 배경(회색)
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    # 현재 수치
    if max_val > 0:
        ratio = current / max_val
        pygame.draw.rect(surface, color, (x, y, width * ratio, height))
    # 테두리
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)

def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("arial", size, True)
    img = font.render(text, True, color)
    rect = img.get_rect(topleft=(x, y))
    surface.blit(img, rect)

def draw_hud(surface, player, elapsed_time, stage):
    # 1. 시간 표시 (중앙 상단)
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_str = f"{minutes:02}:{seconds:02}"
    draw_text(surface, time_str, 40, SCREEN_W//2 - 40, 20)

    # 2. 스테이지 & 골드
    draw_text(surface, f"STAGE: {stage}", 30, 20, 20, YELLOW)
    draw_text(surface, f"GOLD: {player.gold}", 30, 20, 60, YELLOW)

    # 3. 플레이어 상태창 (좌측 하단)
    # 체력바 (하트 대신 바로 표시)
    draw_text(surface, "HP", 20, 20, SCREEN_H - 70)
    draw_bar(surface, 60, SCREEN_H - 70, player.hp, player.max_hp, RED, 200, 20)
    draw_text(surface, f"{int(player.hp)}/{player.max_hp}", 20, 270, SCREEN_H - 70)

    # 4. 경험치바 (화면 최하단)
    draw_bar(surface, 0, SCREEN_H - 10, player.xp, player.next_xp, BLUE, SCREEN_W, 10)
    
    # 레벨 표시
    draw_text(surface, f"Lv.{player.level}", 30, SCREEN_W - 100, SCREEN_H - 50)