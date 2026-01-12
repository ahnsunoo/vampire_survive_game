# settings.py

# 화면 및 맵 설정
SCREEN_W, SCREEN_H = 1280, 720
MAP_W, MAP_H = 10000, 10000
FPS = 60

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128)

# 플레이어 기본 스탯
PLAYER_SPEED = 4
PLAYER_HP = 100
PLAYER_DMG = 20
ATTACK_DELAY = 1000  # ms 단위 (1초)

# 스테이지 설정
STAGE_DURATION = 20 # 60초마다 스테이지(난이도) 증가
BOSS_SPAWN_TIME = 2 # 180초(3분) 뒤 보스 등장