import pygame
import random
import sys

# --- [설정] ---
MAP_SIZE = 10000    # 10000 x 10000 픽셀
OBSTACLE_COUNT = 3000 # 장애물(나무/돌) 개수
DECO_COUNT = 10000    # 장식(꽃/풀) 개수

# 색상 정의
COLOR_GRASS = (30, 60, 30)       # 어두운 잔디색 (배경)
COLOR_GRASS_LIGHT = (40, 70, 40) # 약간 밝은 잔디 (타일 효과)
COLOR_TREE = (20, 20, 20)        # 나무/돌 (장애물)
COLOR_FLOWER = (200, 50, 50)     # 꽃 (장식)
COLOR_WEED = (50, 100, 50)       # 잡초 (장식)

# 마스크용 색상
MASK_WALL = (0, 0, 0)       # 벽 (검은색)
MASK_GROUND = (255, 255, 255) # 땅 (흰색)

def create_maps():
    print("🎨 맵 생성을 시작합니다... (메모리에 따라 5~10초 정도 걸립니다)")
    pygame.init()

    # 1. 캔버스 만들기 (게임용, 마스크용)
    # 10000x10000 크기의 거대한 도화지 생성
    game_map = pygame.Surface((MAP_SIZE, MAP_SIZE))
    collision_map = pygame.Surface((MAP_SIZE, MAP_SIZE))

    # 2. 배경 채우기
    game_map.fill(COLOR_GRASS)
    collision_map.fill(MASK_GROUND) # 기본은 다 지나갈 수 있는 땅

    # 3. 바둑판 무늬 넣기 (타일 느낌)
    print("⬜ 바닥 타일 패턴 그리는 중...")
    tile_size = 200
    for y in range(0, MAP_SIZE, tile_size):
        for x in range(0, MAP_SIZE, tile_size):
            if (x // tile_size + y // tile_size) % 2 == 0:
                pygame.draw.rect(game_map, COLOR_GRASS_LIGHT, (x, y, tile_size, tile_size))

    # 4. 장식 그리기 (꽃, 풀) - 충돌 마스크에는 안 그림!
    print("🌸 꽃과 잡초 심는 중...")
    for _ in range(DECO_COUNT):
        x = random.randint(0, MAP_SIZE)
        y = random.randint(0, MAP_SIZE)
        
        # 잡초
        pygame.draw.circle(game_map, COLOR_WEED, (x, y), random.randint(2, 5))
        
        # 꽃 (가끔)
        if random.random() < 0.1:
            pygame.draw.circle(game_map, COLOR_FLOWER, (x, y), random.randint(3, 6))

    # 5. 장애물 그리기 (나무, 돌) - 충돌 마스크에도 그림!
    print("🌳 나무와 바위 배치 중...")
    for _ in range(OBSTACLE_COUNT):
        x = random.randint(100, MAP_SIZE - 100)
        y = random.randint(100, MAP_SIZE - 100)
        size = random.randint(30, 60) # 장애물 크기

        # (1) 게임 맵에 그리기 (진한 회색 원)
        pygame.draw.circle(game_map, COLOR_TREE, (x, y), size)
        # 나무 질감 표현 (테두리)
        pygame.draw.circle(game_map, (10, 10, 10), (x, y), size, 5)

        # (2) 충돌 맵에 그리기 (검은색 원 = 못 지나감)
        pygame.draw.circle(collision_map, MASK_WALL, (x, y), size)

    # 6. 맵 테두리 막기 (맵 밖으로 못 나가게 벽으로 감싸기)
    border_thick = 50
    pygame.draw.rect(game_map, COLOR_TREE, (0, 0, MAP_SIZE, MAP_SIZE), border_thick)
    pygame.draw.rect(collision_map, MASK_WALL, (0, 0, MAP_SIZE, MAP_SIZE), border_thick)

    # 7. 파일로 저장
    print("💾 파일 저장 중... (거의 다 됐습니다!)")
    pygame.image.save(game_map, "huge_map.png")
    pygame.image.save(collision_map, "huge_mask.png")
    
    print("✅ 완료! 'huge_map.png'와 'huge_mask.png'가 생성되었습니다.")
    pygame.quit()

if __name__ == "__main__":
    create_maps()