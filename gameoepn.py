import pygame
import json
import os
import sys
import random

# [1] 경로 및 초기화
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

from settings import *
from camera import Camera
from entities import Player, Enemy, Boss, Bullet, Explosion, DamageText, SpeedyEnemy, TankEnemy, SpeedyBoss, TankBoss
import ui

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Vampire Survivors Ultimate Edition")
clock = pygame.time.Clock()

# 폰트 설정
try:
    font = pygame.font.SysFont("malgungothic", 24, bold=True)
    large_font = pygame.font.SysFont("malgungothic", 60, bold=True)
except:
    font = pygame.font.SysFont("arial", 24, bold=True)
    large_font = pygame.font.SysFont("arial", 60, bold=True)

# 레벨업 선택지 정의
LEVEL_UP_OPTIONS = [
    {"name": "Power Up", "desc": "데미지 +20", "attr": "damage", "val": 20},
    {"name": "Speed Up", "desc": "이동속도 +1", "attr": "speed", "val": 1},
    {"name": "Rapid Fire", "desc": "공격 딜레이 -10", "attr": "attack_delay", "val": -100},
    {"name": "Vitality", "desc": "최대 체력 +20", "attr": "max_hp", "val": 20},
    {"name": "Multishot", "desc": "투사체 개수 +1", "attr": "bullet_count", "val": 1}
]

# 이미지 로드 함수
def get_ui_img(name, size):
    for ext in [".png", ".jpg", ".jpeg"]:
        path = name + ext
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
    return None

start_bg_img = get_ui_img("start image", (SCREEN_W, SCREEN_H))
btn_img = get_ui_img("option butten", (320, 90))

# [2] 데이터 관리
DATA_PATH, RANK_PATH = "game_data.json", "ranking.json"
game_data = {"money": 1000, "stats": {"체력(HP)": 0, "이동속도": 0, "데미지": 0, "공격 딜레이": 0}}
rank_data = []

def save_all():
    with open(DATA_PATH, "w", encoding='utf-8') as f: json.dump(game_data, f, ensure_ascii=False, indent=4)
    with open(RANK_PATH, "w", encoding='utf-8') as f: json.dump(rank_data, f, ensure_ascii=False, indent=4)

def load_all():
    global game_data, rank_data
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding='utf-8') as f:
                loaded = json.load(f); game_data["money"] = loaded.get("money", 0)
                for k in game_data["stats"]: game_data["stats"][k] = loaded.get("stats", {}).get(k, 0)
        except: save_all()
    if os.path.exists(RANK_PATH):
        try:
            with open(RANK_PATH, "r", encoding='utf-8') as f: rank_data = json.load(f)
        except: rank_data = []

load_all()

def draw_text(text, x, y, color=WHITE, center=False, is_large=False):
    f = large_font if is_large else font
    img = f.render(str(text), True, color)
    rect = img.get_rect(center=(int(x), int(y))) if center else img.get_rect(topleft=(int(x), int(y)))
    screen.blit(img, rect)

# [3] 메인 루프 변수
scene = "LOBBY"
running = True
ingame_init = False
is_game_over = False
current_level_options = []
game_over_start_tick = 0
last_hit_tick = 0 
shake_amount = 0 

while running:
    mx, my = pygame.mouse.get_pos()
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT: save_all(); running = False
        if event.type == pygame.MOUSEBUTTONDOWN: click = True

    # --- [SCENE: LOBBY] ---
    if scene == "LOBBY":
        if start_bg_img: screen.blit(start_bg_img, (0, 0))
        else: screen.fill((200, 20, 25))
        btn_names = ["START", "SHOP", "RANKING", "EXIT"]
        for i, name in enumerate(btn_names):
            bx, by = SCREEN_W - 350, 100 + i * 120
            rect = pygame.Rect(bx, by, 320, 90)
            if btn_img: screen.blit(btn_img, rect)
            else: pygame.draw.rect(screen, (50, 50, 100), rect, border_radius=10)
            draw_text(name, rect.centerx + 0, rect.centery, WHITE, center=True)
            if click and rect.collidepoint(mx, my):
                if name == "START": scene, ingame_init = "INGAME", False
                if name == "SHOP": scene = "SHOP"
                if name == "RANKING": scene = "RANKING"
                if name == "EXIT": running = False

    # --- [SCENE: INGAME] ---
    elif scene == "INGAME":
        if not ingame_init:
            try:
                bg_img = pygame.image.load("huge_map.png").convert()
                mask_img = pygame.image.load("huge_mask.png").convert()
                camera = Camera(MAP_W, MAP_H)
                player = Player(mask_img)
                # 스탯 적용
                player.speed += game_data["stats"].get("이동속도", 0)
                player.max_hp += game_data["stats"].get("체력(HP)", 0) * 10
                player.attack_delay -= game_data["stats"].get("공격 딜레이", 0) * 50
                player.damage += game_data["stats"].get("데미지", 0) * 10
                player.hp = player.max_hp
                
                all_sprites = pygame.sprite.Group(player)
                enemies, bullets, damage_texts = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
                
                start_ticks = pygame.time.get_ticks()
                spawn_timer = 0
                ingame_init = True
                is_game_over = False
                
                # [수정 1] 보스 스폰 관리 변수 추가
                # 이미 보스가 나온 스테이지 번호를 저장할 리스트
                boss_spawned_stages = [] 
                
                shake_amount = 0
                last_hit_tick = 0
            except: scene = "LOBBY"; continue

        sec = (pygame.time.get_ticks() - start_ticks) / 1000
        
        # 스테이지 계산 (1부터 시작, STAGE_DURATION 마다 증가)
        stage = 1 + int(sec // STAGE_DURATION)

        if not is_game_over:
            # 레벨업 체크
            if player.xp >= player.next_xp:
                # player.level += 1
                # player.xp -= player.next_xp
                # player.next_xp = int(player.next_xp * 1.2)
                player.level_up()
                current_level_options = random.sample(LEVEL_UP_OPTIONS, 3)
                scene = "LEVEL_UP"
                click = False
                continue

            # -----------------------------------------------------------
            # [수정 2] 스테이지별 보스 스폰 로직 (3, 6, 9, 10 스테이지)
            # -----------------------------------------------------------
            
            # 3스테이지: 기본 보스 (아직 안 나왔다면)
            if stage == 3 and 3 not in boss_spawned_stages:
                boss = Boss(player, stage, mask_img)
                all_sprites.add(boss); enemies.add(boss)
                boss_spawned_stages.append(3) # 기록해서 중복 스폰 방지
                
            # 6스테이지: 탱크 보스
            elif stage == 6 and 6 not in boss_spawned_stages:
                boss = TankBoss(player, stage, mask_img)
                all_sprites.add(boss); enemies.add(boss)
                boss_spawned_stages.append(6)

            # 9스테이지: 스피드 보스
            elif stage == 9 and 9 not in boss_spawned_stages:
                boss = SpeedyBoss(player, stage, mask_img)
                all_sprites.add(boss); enemies.add(boss)
                boss_spawned_stages.append(9)

            # 10스테이지: 3종류 전부 등장 (최종 난관)
            elif stage == 10 and 10 not in boss_spawned_stages:
                # 1. 기본
                b1 = Boss(player, stage, mask_img)
                all_sprites.add(b1); enemies.add(b1)
                # 2. 탱크
                b2 = TankBoss(player, stage, mask_img)
                all_sprites.add(b2); enemies.add(b2)
                # 3. 스피드
                b3 = SpeedyBoss(player, stage, mask_img)
                all_sprites.add(b3); enemies.add(b3)
                
                boss_spawned_stages.append(10)
            # -----------------------------------------------------------

            player.shoot(camera.camera_rect.topleft, bullets)
            spawn_timer += 1
            
            # 일반 몬스터 스폰 (스테이지 비례)
            if spawn_timer > 30:
                dice = random.random()
                if dice < 0.6: MobClass = Enemy
                elif dice < 0.8: MobClass = SpeedyEnemy
                else: MobClass = TankEnemy
                
                en = MobClass(player, stage, mask_img)
                all_sprites.add(en)
                enemies.add(en)
                spawn_timer = 0

            all_sprites.update(); bullets.update(); damage_texts.update(); camera.update(player)

            # 충돌 로직
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True) 
            for enemy, hit_bullets in hits.items():
                for b in hit_bullets:
                    enemy.hp -= player.damage
                    
                    rand_x = random.randint(-20, 20)
                    rand_y = random.randint(-20, -5)
                    damage_texts.add(DamageText(enemy.rect.centerx + rand_x, enemy.rect.top + rand_y, player.damage))
                    
                    all_sprites.add(Explosion(b.rect.center))
                
                if enemy.hp <= 0:
                    player.xp += enemy.xp_value
                    player.gold += random.randint(1, 5)
                    enemy.kill()

            # 플레이어 피격
            if pygame.sprite.spritecollide(player, enemies, False):
                player.hp -= 0.5
                
                last_hit_tick = pygame.time.get_ticks()
                shake_amount = 12 

                if player.hp <= 0:
                    is_game_over = True
                    game_over_start_tick = pygame.time.get_ticks()
                    game_data["money"] += player.gold
                    rank_data.append({"score": player.gold, "time": sec})
                    rank_data = sorted(rank_data, key=lambda x: x['score'], reverse=True)[:10]
                    save_all()

        # 그리기
        offset_x, offset_y = 0, 0
        if shake_amount > 0:
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
            shake_amount -= 1

        screen.blit(bg_img, (camera.camera_rect.x + offset_x, camera.camera_rect.y + offset_y))
        for s in all_sprites:
            p = camera.apply(s)
            final_pos = (p.x + offset_x, p.y + offset_y)
            
            if s == player and pygame.time.get_ticks() - last_hit_tick < 150:
                flash_surf = s.image.copy()
                flash_surf.fill((255, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(flash_surf, final_pos)
            else:
                screen.blit(s.image, final_pos)
        
        for b in bullets: screen.blit(b.image, camera.apply(b))
        for dt in damage_texts: screen.blit(dt.image, camera.apply(dt))
        
        ui.draw_hud(screen, player, sec, stage)
        
        if is_game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H)); overlay.set_alpha(150); overlay.fill((0, 0, 0)); screen.blit(overlay, (0, 0))
            draw_text("GAME OVER", SCREEN_W//2, SCREEN_H//2 - 40, RED, True, True)
            if pygame.time.get_ticks() - game_over_start_tick > 2500: scene = "RANKING"
        if pygame.key.get_pressed()[pygame.K_ESCAPE]: scene = "LOBBY"

    # --- [SCENE: LEVEL_UP] ---
    elif scene == "LEVEL_UP":
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)); screen.blit(overlay, (0, 0))
        draw_text("LEVEL UP!", SCREEN_W//2, 100, YELLOW, True, True)
        for i, opt in enumerate(current_level_options):
            card_rect = pygame.Rect(SCREEN_W//2 - 450 + i*310, 250, 280, 400)
            pygame.draw.rect(screen, (50, 50, 80), card_rect, border_radius=15)
            draw_text(opt["name"], card_rect.centerx, card_rect.top + 40, WHITE, True)
            draw_text(opt["desc"], card_rect.centerx, card_rect.centery, (200, 200, 200), True)
            if click and card_rect.collidepoint(mx, my):
                v = getattr(player, opt["attr"])
                setattr(player, opt["attr"], v + opt["val"])
                if opt["attr"] == "max_hp": player.hp = player.max_hp
                scene = "INGAME"; click = False

    # --- [SCENE: SHOP] ---
    elif scene == "SHOP":
        screen.fill((30, 30, 35))
        draw_text("강화 상점", SCREEN_W//2, 50, GREEN, True, True)
        draw_text(f"Gold: {game_data['money']}", 50, 50, YELLOW)
        y = 150
        for stat, val in game_data["stats"].items():
            draw_text(f"{stat}: +{val}", 300, y)
            btn = pygame.Rect(600, y-5, 100, 35)
            pygame.draw.rect(screen, WHITE, btn, border_radius=5)
            draw_text("100G", btn.centerx, btn.centery, BLACK, True)
            if click and btn.collidepoint(mx, my) and game_data["money"] >= 100:
                game_data["money"] -= 100; game_data["stats"][stat] += 1; save_all()
            y += 60
        back = pygame.Rect(SCREEN_W//2-100, 600, 200, 45); pygame.draw.rect(screen, (150, 50, 50), back)
        draw_text("BACK", back.centerx, back.centery, WHITE, True)
        if click and back.collidepoint(mx, my): scene = "LOBBY"

    # --- [SCENE: RANKING] ---
    elif scene == "RANKING":
        screen.fill((20, 20, 20)); draw_text("TOP 10 RANKING", SCREEN_W//2, 80, YELLOW, True, True)
        for i, r in enumerate(rank_data[:10]):
            draw_text(f"{i+1}위: {r['score']} Gold", SCREEN_W//2, 180 + i*40, WHITE, True)
        back = pygame.Rect(SCREEN_W//2-100, 600, 200, 45); pygame.draw.rect(screen, (100, 100, 100), back)
        draw_text("BACK", back.centerx, back.centery, WHITE, True)
        if click and back.collidepoint(mx, my): scene = "LOBBY"

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()