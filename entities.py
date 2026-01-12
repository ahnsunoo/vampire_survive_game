# entities.py
import pygame
import math
import random
from settings import *

# --- 투사체 (총알) 클래스 ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, camera_pos, damage, mask_img):
        super().__init__()
        
        # [수정] 이미지 로드 부분
        try:
            # "bullet.png" 이미지를 불러옵니다.
            img = pygame.image.load("bullet.png").convert_alpha()
            # 총알 크기에 맞게 조절 (예: 20x20 픽셀)
            self.image = pygame.transform.scale(img, (50, 50))
        except:
            # 이미지가 없으면 기존처럼 노란색 사각형 사용
            self.image = pygame.Surface((10, 10))
            self.image.fill(YELLOW)

        # 이미지의 중심을 (x, y)로 설정
        self.rect = self.image.get_rect(center=(x, y))
        
        self.mask_img = mask_img
        self.speed = 10
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000 

        # ... (이동 로직인 math.atan2 등은 기존과 동일) ...
        mouse_x, mouse_y = target_pos
        cam_x, cam_y = camera_pos
        world_mouse_x = mouse_x - cam_x
        world_mouse_y = mouse_y - cam_y
        
        angle = math.atan2(world_mouse_y - y, world_mouse_x - x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    # update 함수는 건드릴 필요 없음 (이미지만 바뀌고 이동 로직은 같음)
    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

        if not (0 <= self.rect.centerx < MAP_W and 0 <= self.rect.centery < MAP_H):
            self.kill()
            return

        try:
            check_pos = (int(self.rect.centerx), int(self.rect.centery))
            pixel_color = self.mask_img.get_at(check_pos)
            if sum(pixel_color[:3]) < 50: 
                self.kill()
        except IndexError:
            self.kill()

# --- 플레이어 클래스 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, mask_img):
        super().__init__()
        
        # 1. 이미지 로드 및 좌우 반전 이미지 생성
        try:
            # 원본 이미지 (기본적으로 오른쪽을 보고 있다고 가정)
            self.original_image = pygame.image.load("player.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        except:
            # 이미지가 없으면 파란색 네모
            self.original_image = pygame.Surface((40, 40))
            self.original_image.fill(BLUE)
            
        # [핵심 추가] 오른쪽 보는 이미지 & 왼쪽 보는 이미지 미리 준비
        self.image_right = self.original_image
        # pygame.transform.flip(이미지, 좌우반전여부, 상하반전여부)
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        
        # 현재 이미지 설정 (처음엔 오른쪽)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.mask_img = mask_img
        
        # 스폰 위치 설정
        self.spawn_random_safe()
        
        # 스탯 등 나머지 설정은 동일
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.speed = PLAYER_SPEED
        self.damage = PLAYER_DMG
        self.attack_delay = ATTACK_DELAY
        self.level = 1
        self.xp = 0
        self.next_xp = 100
        self.gold = 0
        self.last_shot_time = 0
        # [핵심] 투사체 개수 (기본 1개)
        self.bullet_count = 1
        
        # 레벨링
        self.level = 1
        self.xp = 0
        self.next_xp = 100
        self.gold = 0
        
        self.last_shot_time = 0

    def spawn_random_safe(self):
        """ 장애물이 없는 땅을 찾을 때까지 랜덤 위치를 계속 뽑습니다 """
        while True:
            # 1. 맵 안에서 랜덤 좌표 뽑기 (가장자리 여백 100픽셀 둠)
            x = random.randint(100, MAP_W - 100)
            y = random.randint(100, MAP_H - 100)
            
            # 2. 마스크 이미지에서 해당 좌표의 색깔 확인
            # (주의: get_at은 (x, y) 정수 좌표를 받습니다)
            try:
                pixel_color = self.mask_img.get_at((x, y))
                
                # 3. 색이 밝으면(땅이면) 위치 확정 후 반복 종료
                # 검은색(0,0,0)은 합이 0, 흰색(255,255,255)은 합이 765
                if sum(pixel_color[:3]) > 50: 
                    self.rect.center = (x, y)
                    print(f"플레이어 스폰 위치: {x}, {y}") # 디버깅용 출력
                    break
            except IndexError:
                continue # 혹시라도 좌표가 벗어나면 다시 뽑기

    def get_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # [수정] 방향키 대신 WASD로 변경
        if keys[pygame.K_a]:      # A 키 (왼쪽)
            dx = -self.speed
        if keys[pygame.K_d]:      # D 키 (오른쪽)
            dx = self.speed
        if keys[pygame.K_w]:      # W 키 (위쪽)
            dy = -self.speed
        if keys[pygame.K_s]:      # S 키 (아래쪽)
            dy = self.speed
            
        return dx, dy

    def check_collision(self, dx, dy):
        # ... (이전과 동일) ...
        if dx != 0:
            next_x = self.rect.x + dx
            if 0 <= next_x < MAP_W - self.rect.width:
                cx = next_x + self.rect.width // 2
                cy = self.rect.centery
                if sum(self.mask_img.get_at((cx, cy))[:3]) > 50:
                    self.rect.x += dx
        
        if dy != 0:
            next_y = self.rect.y + dy
            if 0 <= next_y < MAP_H - self.rect.height:
                cx = self.rect.centerx
                cy = next_y + self.rect.height // 2
                if sum(self.mask_img.get_at((cx, cy))[:3]) > 50:
                    self.rect.y += dy

    # [수정됨] 멀티샷 지원 사격 함수
    def shoot(self, camera_pos, bullet_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.attack_delay:
            self.last_shot_time = now
            
            mx, my = pygame.mouse.get_pos()
            
            # 플레이어의 화면상 좌표
            px = self.rect.centerx + camera_pos[0]
            py = self.rect.centery + camera_pos[1]
            
            # 기준 각도 (마우스 방향)
            base_angle = math.atan2(my - py, mx - px)
            
            # 멀티샷 각도 벌림 (15도)
            spread = math.radians(15)
            start_angle = base_angle - ((self.bullet_count - 1) * spread / 2)
            
            for i in range(self.bullet_count):
                angle = start_angle + (i * spread)
                
                # Bullet 생성자는 '목표 지점(Screen Pos)'을 요구하므로
                # 해당 각도 방향으로 멀리 있는 가상의 화면 좌표를 계산해 넘겨줌
                target_screen_x = px + math.cos(angle) * 1000
                target_screen_y = py + math.sin(angle) * 1000
                
                b = Bullet(self.rect.centerx, self.rect.centery, 
                           (target_screen_x, target_screen_y), 
                           camera_pos, self.damage, self.mask_img)
                bullet_group.add(b)

    def update(self):
        # 1. 키 입력 받기
        dx, dy = self.get_input()
        
        # [핵심 추가] 이동 방향에 따라 이미지 교체
        if dx > 0: # 오른쪽으로 이동 중
            self.image = self.image_right
        elif dx < 0: # 왼쪽으로 이동 중
            self.image = self.image_left
        
        # (참고: dx == 0 일 때는 아무것도 안 하므로, 마지막으로 본 방향을 유지함)

        # 2. 충돌 체크 및 이동
        self.check_collision(dx, dy)
        
        # 3. 레벨업 체크
        if self.xp >= self.next_xp:
            self.level_up()


    def level_up(self):
        self.level += 1

        self.xp -= self.next_xp
        
        self.next_xp = int(self.next_xp+50)
        
        # self.damage += 2
        # self.max_hp += 10
        self.hp = self.max_hp
        print(f"Level Up! Lv.{self.level}")




# --- 적(Enemy) 클래스  ---
# entities.py

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, stage, mask_img):
        super().__init__()
        self.player = player
        self.mask_img = mask_img
        
        # ... (이미지 로드 코드 생략) ...
        try:
            self.original_image = pygame.image.load("enemy.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (55, 55))
        except:
            self.original_image = pygame.Surface((30, 30))
            self.original_image.fill(RED)

        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        self.image = self.image_right
        
        # ... (스폰 위치 계산 코드 생략) ...
        scale_factor = 1+stage*0.3
        angle = random.uniform(0, 360)
        distance = random.randint(500, 800)
        spawn_x = player.rect.centerx + math.cos(angle) * distance
        spawn_y = player.rect.centery + math.sin(angle) * distance
        spawn_x = max(50, min(spawn_x, MAP_W-50))
        spawn_y = max(50, min(spawn_y, MAP_H-50))
        
        # [중요] self.rect가 여기서 정의됩니다!
        self.rect = self.image.get_rect(center=(spawn_x, spawn_y))
        
        # ---------------------------------------------------------
        # [수정] 갇힘 감지 변수들은 반드시 self.rect 밑에 써야 합니다!
        # ---------------------------------------------------------
        self.last_pos = pygame.math.Vector2(self.rect.center) # 이제 self.rect가 있어서 에러 안 남
        self.stuck_timer = 0
        self.escape_timer = 0
        self.escape_dir = (0, 0)
        # ---------------------------------------------------------

        
        ####적의 능력치 관련 스테이지 마다 달라짐
        self.hp = 30 * scale_factor
        # self.damage = 10 * scale_factor
        self.speed = random.uniform(2, 5) + (stage * 0.2)
        self.xp_value = 10 

    def update(self):
        # --- [1] 탈출 모드인지 확인 ---
        if self.escape_timer > 0:
            self.escape_timer -= 1
            # 탈출 중일 때는 플레이어가 아니라 '탈출 방향'으로 강제 이동
            dx, dy = self.escape_dir
        else:
            # 평소에는 플레이어 추적
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
        
        # 거리 계산 및 정규화 (방향 벡터 만들기)
        dist = math.hypot(dx, dy)
        if dist != 0:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            
            # --- [2] 이미지 방향 전환 (탈출 중이 아닐 때만) ---
            if self.escape_timer == 0:
                if dx > 0: self.image = self.image_right
                elif dx < 0: self.image = self.image_left

            # --- [3] 이동 및 충돌 처리 (기존 코드) ---
            # X축 이동
            self.rect.x += move_x
            check_pos = (int(self.rect.centerx), int(self.rect.centery))
            # 맵 밖이거나 벽이면 되돌리기
            if not (0 <= self.rect.centerx < MAP_W) or \
               (sum(self.mask_img.get_at(check_pos)[:3]) <= 50):
                self.rect.x -= move_x

            # Y축 이동
            self.rect.y += move_y
            check_pos = (int(self.rect.centerx), int(self.rect.centery))
            if not (0 <= self.rect.centery < MAP_H) or \
               (sum(self.mask_img.get_at(check_pos)[:3]) <= 50):
                self.rect.y -= move_y

        # --- [4] 갇힘 감지 로직 (핵심!) ---
        # 현재 위치 벡터
        current_pos = pygame.math.Vector2(self.rect.center)
        
        # 저번 프레임 위치와 비교해서 이동 거리가 1 픽셀 미만이면 (거의 안 움직임)
        if current_pos.distance_to(self.last_pos) < 0.5:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0 # 잘 움직이면 타이머 초기화
            
        # 위치 업데이트
        self.last_pos = current_pos
        
        # 60프레임(1초) 동안 갇혀있으면 탈출 모드 발동!
        if self.stuck_timer > 30: # 0.5초 정도 비비면
            self.stuck_timer = 0
            self.escape_timer = 40 # 약 0.7초 동안 다른 곳으로 도망
            
            # 랜덤한 방향으로 튀기 (-1 ~ 1 사이의 랜덤 벡터)
            rand_angle = random.uniform(0, 360)
            ex = math.cos(rand_angle) * 100 # 좀 멀리 찍음
            ey = math.sin(rand_angle) * 100
            self.escape_dir = (ex, ey)



# --- [추가] 빠른 몬스터 (체력 낮음, 속도 빠름) ---
class SpeedyEnemy(Enemy):
    def __init__(self, player, stage, mask_img):
        super().__init__(player, stage, mask_img)
        # 이미지 덮어쓰기
        try:
            self.original_image = pygame.image.load("enemy_speed.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        except:
            self.original_image = pygame.Surface((40, 40))
            self.original_image.fill(GREEN) # 이미지가 없으면 초록색

        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        self.image = self.image_right
        
        # 스탯 재설정 (부모 클래스 값 덮어쓰기)
        self.speed = random.uniform(4, 6) + (stage * 0.3) # 기본보다 훨씬 빠름
        self.hp = 15 + (stage * 5)                        # 체력은 절반 수준
        self.xp_value = 15

# --- [추가] 탱커 몬스터 (체력 높음, 속도 느림) ---
class TankEnemy(Enemy):
    def __init__(self, player, stage, mask_img):
        super().__init__(player, stage, mask_img)
        try:
            self.original_image = pygame.image.load("enemy_tank.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (120, 120)) # 덩치 큼
        except:
            self.original_image = pygame.Surface((70, 70))
            self.original_image.fill(BLUE) # 이미지가 없으면 파란색

        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=self.rect.center) # 크기가 바뀌었으니 rect 갱신

        # 스탯 재설정
        self.speed = random.uniform(1, 2) + (stage * 0.1) # 매우 느림
        self.hp = 80 + (stage * 20)                       # 체력은 2배 이상
        self.xp_value = 30





# --- 보스 클래스 수정 ---
class Boss(Enemy):
    def __init__(self, player, stage, mask_img):
        super().__init__(player, stage, mask_img) # 부모 초기화 (위치 잡기 등)

        # 1. 보스 이미지 로드
        try:
            # "boss.png" 파일 로드
            img = pygame.image.load("boss.png").convert_alpha()
            self.original_image = pygame.transform.scale(img, (250, 250)) # 보스는 크니까 150x150
        except:
            # 파일이 없으면 보라색 사각형
            self.original_image = pygame.Surface((100, 100))
            self.original_image.fill(PURPLE)

        # 2. 좌우 이미지 재설정 (중요!)
        # 이걸 안 하면 보스가 움직일 때 일반 몬스터(enemy.png) 그림이 튀어나옵니다.
        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        
        self.image = self.image_right

        # 3. Rect 및 중심점 재설정
        # 이미지가 커졌으므로 중심점을 기준으로 다시 rect를 잡아야 위치가 안 튀고 자연스럽습니다.
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)
        
        # 4. 보스 스탯 설정
        self.hp = 5000 + (stage * 500)
        self.speed = 2 # 보스는 거대하니까 조금 느리게
        self.damage = 50
        self.xp_value = 1000
        
        # 5. 갇힘 감지용 위치 변수 업데이트 (rect가 바뀌었으므로)
        self.last_pos = pygame.math.Vector2(self.rect.center)



# --- [추가] 빠른 보스 ---
class SpeedyBoss(Boss):
    def __init__(self, player, stage, mask_img):
        super().__init__(player, stage, mask_img)
        try:
            self.original_image = pygame.image.load("boss_speed.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (200, 200))
        except:
            self.original_image = pygame.Surface((120, 120))
            self.original_image.fill((255, 100, 255)) # 연보라색

        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=self.rect.center)

        self.speed = 4 + (stage * 0.1) # 플레이어만큼 빠름
        self.hp = 3000 + (stage * 300) # 체력은 일반 보스보다 낮음
        self.damage = 30

# --- [추가] 탱커 보스 ---
class TankBoss(Boss):
    def __init__(self, player, stage, mask_img):
        super().__init__(player, stage, mask_img)
        try:
            self.original_image = pygame.image.load("boss_tank.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (300, 300)) # 엄청 큼
        except:
            self.original_image = pygame.Surface((200, 200))
            self.original_image.fill((50, 0, 50)) # 아주 진한 보라색

        self.image_right = self.original_image
        self.image_left = pygame.transform.flip(self.original_image, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=self.rect.center)

        self.speed = 1 # 아주 느림
        self.hp = 10000 + (stage * 1000) # 체력이 엄청남
        self.damage = 80 # 한방이 아픔




















class Explosion(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        
        # 1. 폭발 이미지 로드
        try:
            img = pygame.image.load("explosion.png").convert_alpha()
            self.image = pygame.transform.scale(img, (60, 60)) # 크기 조절
        except:
            # 이미지 없으면 주황색 원
            self.image = pygame.Surface((30, 30))
            self.image.fill((0,0,0)) # 투명 처리를 위해 검은색 채움
            self.image.set_colorkey((0,0,0))
            pygame.draw.circle(self.image, (255, 100, 0), (15, 15), 15)
            
        self.rect = self.image.get_rect(center=center_pos)
        
        # 2. 보여줄 시간 설정 (프레임 단위)
        self.timer = 10 # 10프레임(약 0.16초) 동안 보여줌

    def update(self):
        # 시간이 지나면 알아서 사라짐
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# 데미지 텍스트 클래스
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        try:
            self.font = pygame.font.SysFont("malgungothic", 24, bold=True)
        except:
            self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.image = self.font.render(str(damage), True, (255, 200, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.vy = -2
    def update(self):
        self.rect.y += self.vy
        self.alpha -= 8 
        if self.alpha <= 0: self.kill()
        else: self.image.set_alpha(self.alpha)