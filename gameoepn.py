import pygame
import json
import os
import sys
import webbrowser
import subprocess # 랭킹 서버 실행용
import time

# 1. 초기화 및 설정
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Vampire Survivors - Ultimate Lobby")

# 폰트 설정
font = pygame.font.SysFont("malgungothic", 20)
large_font = pygame.font.SysFont("malgungothic", 35)

# --- 경로 설정 (사용자 경로에 맞춤) ---
BASE_DIR = r"C:\Users\KDT38\Desktop\project"
DATA_PATH = os.path.join(BASE_DIR, "game_data.json")

# --- 자동 랭킹 서버 실행 ---
# 게임을 켤 때 랭킹 서버(rank_page.py)를 조용히 같이 실행합니다.
try:
    subprocess.Popen(
        ["C:/Users/KDT38/miniconda3/python.exe", "-m", "streamlit", "run", "rank_page.py"],
        cwd=BASE_DIR, # 파일이 있는 폴더에서 실행하도록 고정
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )
except Exception as e:
    print(f"서버 실행 실패: {e}")

# 2. 함수 정의
def draw_text(text, x, y, color=(255, 255, 255), center=False):
    screen_text = font.render(text, True, color)
    text_rect = screen_text.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(screen_text, text_rect)

def save_data():
    with open(DATA_PATH, "w", encoding='utf-8') as f:
        json.dump(game_data, f, ensure_ascii=False, indent=4)

def load_data():
    global game_data
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding='utf-8') as f:
                game_data = json.load(f)
        except:
            save_data()

# 데이터 로드 (돈이 없으면 강화 테스트가 안 되니 초기값 1000G 부여)
game_data = {
    "money": 1000, 
    "last_score": 0,
    "stats": {
        "체력(HP)": 0, "이동속도": 0, "데미지": 0,
        "공격 딜레이": 0, "투사체 개수": 0, "공격 범위": 0
    }
}
load_data()

scene = "LOBBY"
running = True

# 3. 메인 루프
while running:
    screen.fill((20, 20, 25))
    mx, my = pygame.mouse.get_pos()
    click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

    # --- 1. 메인 로비 화면 ---
    if scene == "LOBBY":
        screen.blit(large_font.render("VAMPIRE SURVIVORS", True, (200, 50, 50)), (230, 80))
        
        btn_start = pygame.Rect(300, 220, 200, 50)
        btn_powerup = pygame.Rect(300, 290, 200, 50)
        btn_ranking = pygame.Rect(300, 360, 200, 50)
        btn_exit = pygame.Rect(300, 430, 200, 50)
        
        pygame.draw.rect(screen, (50, 50, 150), btn_start, border_radius=10)
        pygame.draw.rect(screen, (50, 150, 50), btn_powerup, border_radius=10)
        pygame.draw.rect(screen, (241, 196, 15), btn_ranking, border_radius=10)
        pygame.draw.rect(screen, (150, 50, 50), btn_exit, border_radius=10)
        
        draw_text("시작 (START)", 400, 245, center=True)
        draw_text("파워 업 (POWER UP)", 400, 315, center=True)
        draw_text("랭킹 확인 (RANK)", 400, 385, (0, 0, 0), center=True)
        draw_text("나가기 (EXIT)", 400, 455, center=True)

        if click:
            if btn_start.collidepoint(mx, my): scene = "INGAME"
            if btn_powerup.collidepoint(mx, my): scene = "POWERUP"
            if btn_ranking.collidepoint(mx, my):
                webbrowser.open("http://localhost:8501")
            if btn_exit.collidepoint(mx, my):
                save_data(); running = False

    # --- 2. 파워업 화면 ---
    elif scene == "POWERUP":
        screen.fill((30, 30, 35))
        draw_text("능력치 강화 상점", 400, 50, (0, 255, 0), True)
        draw_text(f"보유 골드: {game_data['money']} G", 50, 50, (255, 215, 0))
        
        y_offset = 120
        for stat_name, value in game_data["stats"].items():
            draw_text(f"{stat_name}: +{value}", 200, y_offset)
            
            plus_rect = pygame.Rect(450, y_offset - 5, 80, 35)
            pygame.draw.rect(screen, (200, 200, 200), plus_rect, border_radius=5)
            draw_text("100G", 465, y_offset, (0, 0, 0))
            
            if click and plus_rect.collidepoint(mx, my):
                if game_data["money"] >= 100:
                    game_data["money"] -= 100
                    game_data["stats"][stat_name] += 1
                    save_data()
            y_offset += 65

        back_btn = pygame.Rect(300, 530, 200, 40)
        pygame.draw.rect(screen, (100, 100, 100), back_btn)
        draw_text("로비로 돌아가기", 400, 550, center=True)
        if click and back_btn.collidepoint(mx, my): 
            scene = "LOBBY"

    # --- 3. 인게임 화면 (전투 시스템 들어갈 자리) ---
    elif scene == "INGAME":
        screen.fill((0, 0, 0))
        draw_text("전투 준비 중...", 400, 300, center=True)
        draw_text("ESC: 로비로", 400, 350, center=True)
        if pygame.key.get_pressed()[pygame.K_ESCAPE]: scene = "LOBBY"

    pygame.display.flip()

pygame.quit()
sys.exit()