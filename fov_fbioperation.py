import pygame
import math
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1100, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FBI Taktiksel Room Clearing - Agresif Çatışma")
clock = pygame.time.Clock()

BLACK = (5, 5, 10)
LIGHT_GRAY = (140, 140, 160)
WHITE = (240, 240, 240)
RED = (220, 50, 50)
FBI_BLUE = (25, 50, 100)
TACTICAL_DARK = (35, 40, 50)
YELLOW = (255, 220, 50)
GREEN = (50, 200, 50)
CYAN = (0, 200, 255)
ORANGE = (255, 140, 0)
WOOD_BROWN = (139, 69, 19)
SKIN_COLOR = (235, 180, 140)
GUN_METAL = (70, 75, 80)
SILVER = (200, 210, 220)

font = pygame.font.SysFont("Arial", 20, bold=True)
big_font = pygame.font.SysFont("Arial", 36, bold=True)

level = 1
money = 250
game_state = "SHOP"

player = {
    "x": 150,
    "y": 400,
    "base_speed": 4.5,
    "radius": 16,
    "health": 50,
    "max_health": 50,
    "clip": 6,
    "max_clip": 6,
    "reserve_ammo": 12,
    "reloading": False,
    "reload_timer": 0,
    "reload_duration": 180,
    "flashbangs": 2,
    "flares": 2,
    "knife_anim_timer": 0
}

ai_agent = {
    "hired": False,
    "x": 150,
    "y": 450,
    "speed": 3.8,
    "shoot_cooldown": 0
}

walls = []
doors = []
enemies = []
hostages = []
bullets = []
active_tools = []
extraction_zone = pygame.Rect(110, 85, 80, 80)


def load_level(lvl):
    global walls, doors, enemies, hostages, player, bullets, active_tools, ai_agent
    walls.clear()
    doors.clear()
    enemies.clear()
    hostages.clear()
    bullets.clear()
    active_tools.clear()

    ai_agent["hired"] = False
    player["x"] = 150
    player["y"] = 400
    player["health"] = player["max_health"]
    player["clip"] = player["max_clip"]
    player["reserve_ammo"] = 12
    player["reloading"] = False
    player["reload_timer"] = 0
    player["knife_anim_timer"] = 0

    ox, oy = 100, 75
    walls.append(pygame.Rect(ox, oy, 900, 20))
    walls.append(pygame.Rect(ox, oy + 650, 900, 20))
    walls.append(pygame.Rect(ox, oy, 20, 650))
    walls.append(pygame.Rect(ox + 880, oy, 20, 650))

    if lvl == 1:
        # Seviye 1: Daha kalabalık ve pusu odaları
        walls.append(pygame.Rect(ox + 350, oy, 20, 220))
        doors.append({"rect": pygame.Rect(ox + 350, oy + 220, 20, 100), "open": 0.0, "is_vertical": True})
        walls.append(pygame.Rect(ox + 350, oy + 320, 20, 330))

        walls.append(pygame.Rect(ox + 370, oy + 420, 280, 20))
        doors.append({"rect": pygame.Rect(ox + 650, oy + 420, 100, 20), "open": 0.0, "is_vertical": False})
        walls.append(pygame.Rect(ox + 750, oy + 420, 130, 20))

        # Agresif Düşmanlar (Şarjör, Atış hızı ve Reload özellikleri eklendi)
        for ex, ey in [(380, 90), (850, 90), (700, 250), (850, 380), (390, 600), (850, 600), (550, 200)]:
            enemies.append({
                "x": ox + ex, "y": oy + ey, "radius": 16, "health": 1,
                "shoot_cooldown": 0, "burst_count": 0, "reloading": False, "reload_timer": 0, "clip": 4, "stunned": 0
            })

        hostages.append({"x": ox + 820, "y": oy + 150, "radius": 14, "rescued": False})
        hostages.append({"x": ox + 780, "y": oy + 580, "radius": 14, "rescued": False})

    elif lvl == 2:
        # Seviye 2: Yoğun Çatışma Labirenti
        walls.append(pygame.Rect(ox + 280, oy, 20, 320))
        doors.append({"rect": pygame.Rect(ox + 280, oy + 320, 20, 100), "open": 0.0, "is_vertical": True})
        walls.append(pygame.Rect(ox + 280, oy + 420, 20, 230))

        walls.append(pygame.Rect(ox + 580, oy + 150, 20, 350))
        doors.append({"rect": pygame.Rect(ox + 580, oy + 500, 20, 100), "open": 0.0, "is_vertical": True})
        walls.append(pygame.Rect(ox + 580, oy + 600, 20, 50))

        walls.append(pygame.Rect(ox + 580, oy + 280, 200, 20))

        for ex, ey in [(310, 90), (540, 100), (850, 90), (700, 180), (850, 240), (450, 500), (620, 600), (850, 600)]:
            enemies.append({
                "x": ox + ex, "y": oy + ey, "radius": 16, "health": 1,
                "shoot_cooldown": 0, "burst_count": 0, "reloading": False, "reload_timer": 0, "clip": 4, "stunned": 0
            })

        hostages.append({"x": ox + 750, "y": oy + 200, "radius": 14, "rescued": False})
        hostages.append({"x": ox + 820, "y": oy + 520, "radius": 14, "rescued": False})
        hostages.append({"x": ox + 420, "y": oy + 300, "radius": 14, "rescued": False})


load_level(level)


def check_collision_rect(x, y, r, rect):
    closest_x = max(rect.left, min(x, rect.right))
    closest_y = max(rect.top, min(y, rect.bottom))
    return ((x - closest_x) ** 2 + (y - closest_y) ** 2) < (r ** 2)


def line_of_sight(x1, y1, x2, y2):
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        px = x1 + (x2 - x1) * t
        py = y1 + (y2 - y1) * t
        for w in walls:
            if w.collidepoint(px, py):
                return False
        for d in doors:
            if d["open"] < 0.7 and d["rect"].collidepoint(px, py):
                return False
    return True


def start_reload():
    if not player["reloading"] and player["clip"] < player["max_clip"] and player["reserve_ammo"] > 0:
        player["reloading"] = True
        player["reload_timer"] = player["reload_duration"]


def draw_tactical_agent(surface, x, y, angle, body_color, is_player=False, is_nemesis_reloading=False,
                        is_attacking=False):
    gun_len = 22
    r_hand_x = x + math.cos(angle + 0.5) * 16
    r_hand_y = y + math.sin(angle + 0.5) * 16
    l_hand_x = x + math.cos(angle - 0.4) * 18
    l_hand_y = y + math.sin(angle - 0.4) * 18

    pygame.draw.line(surface, body_color, (x, y), (r_hand_x, r_hand_y), 5)
    pygame.draw.line(surface, body_color, (x, y), (l_hand_x, l_hand_y), 5)
    pygame.draw.circle(surface, SKIN_COLOR, (int(r_hand_x), int(r_hand_y)), 3)
    pygame.draw.circle(surface, SKIN_COLOR, (int(l_hand_x), int(l_hand_y)), 3)

    if is_attacking:
        knife_base_x = x + math.cos(angle) * 15
        knife_base_y = y + math.sin(angle) * 15
        knife_tip_x = x + math.cos(angle) * 35
        knife_tip_y = y + math.sin(angle) * 35
        pygame.draw.line(surface, SILVER, (knife_base_x, knife_base_y), (knife_tip_x, knife_tip_y), 4)
    else:
        gun_end_x = x + math.cos(angle) * (gun_len + 8)
        gun_end_y = y + math.sin(angle) * (gun_len + 8)
        pygame.draw.line(surface, GUN_METAL, (x + math.cos(angle) * 8, y + math.sin(angle) * 8), (gun_end_x, gun_end_y),
                         4)

    pygame.draw.circle(surface, (15, 15, 20), (int(x), int(y) + 3), 16)
    pygame.draw.circle(surface, body_color, (int(x), int(y)), 15)
    pygame.draw.circle(surface, TACTICAL_DARK, (int(x), int(y)), 10)
    pygame.draw.circle(surface, BLACK if is_player else (120, 30, 30), (int(x), int(y)), 6)

    # Düşman reload yaparken baş üstünde uyarı simgesi
    if is_nemesis_reloading:
        pygame.draw.circle(surface, YELLOW, (int(x), int(y) - 22), 5)


running = True
while running:
    screen.fill(BLACK)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if game_state == "SHOP":
                if event.key == pygame.K_1 and money >= 80:
                    money -= 80
                    player["reserve_ammo"] += 12
                elif event.key == pygame.K_2 and money >= 120:
                    money -= 120
                    player["flashbangs"] += 1
                elif event.key == pygame.K_3 and money >= 120:
                    money -= 120
                    player["flares"] += 1
                elif event.key == pygame.K_4 and money >= 300 and not ai_agent["hired"]:
                    money -= 300
                    ai_agent["hired"] = True
                elif event.key == pygame.K_RETURN:
                    game_state = "PLAYING"

            elif game_state == "PLAYING":
                if event.key == pygame.K_r:
                    start_reload()
                elif event.key == pygame.K_q and player["flares"] > 0:
                    if line_of_sight(player["x"], player["y"], mouse_x, mouse_y):
                        player["flares"] -= 1
                        active_tools.append({"type": "flare", "x": mouse_x, "y": mouse_y, "timer": 240})
                elif event.key == pygame.K_e and player["flashbangs"] > 0:
                    if line_of_sight(player["x"], player["y"], mouse_x, mouse_y):
                        player["flashbangs"] -= 1
                        active_tools.append({"type": "flashbang", "x": mouse_x, "y": mouse_y, "timer": 30})
                elif event.key == pygame.K_SPACE:
                    player["knife_anim_timer"] = 12
                    for e in enemies[:]:
                        if math.hypot(player["x"] - e["x"], player["y"] - e["y"]) < 40:
                            enemies.remove(e)
                            money += 40
                            break

            elif game_state == "LEVEL_WON":
                level += 1
                if level > 2: level = 1
                load_level(level)
                game_state = "SHOP"
            elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                level = 1
                money = 250
                load_level(level)
                game_state = "SHOP"

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "PLAYING":
            if event.button == 1:
                if player["reloading"]:
                    pass
                elif player["clip"] > 0:
                    player["clip"] -= 1
                    angle = math.atan2(mouse_y - player["y"], mouse_x - player["x"])
                    bullets.append({
                        "x": player["x"], "y": player["y"],
                        "dx": math.cos(angle) * 22, "dy": math.sin(angle) * 22,
                        "from_player": True
                    })
                    if player["clip"] == 0:
                        start_reload()

    keys = pygame.key.get_pressed()
    if game_state == "PLAYING":
        if player["knife_anim_timer"] > 0:
            player["knife_anim_timer"] -= 1

        if player["reloading"]:
            player["reload_timer"] -= 1
            if player["reload_timer"] <= 0:
                needed = player["max_clip"] - player["clip"]
                to_reload = min(needed, player["reserve_ammo"])
                player["clip"] += to_reload
                player["reserve_ammo"] -= to_reload
                player["reloading"] = False

        rescued_count = sum(1 for h in hostages if h["rescued"] and h["x"] > 0)
        current_speed = player["base_speed"] * (0.75 ** rescued_count)

        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += current_speed

        for d in doors:
            dist_to_door = math.hypot(player["x"] - d["rect"].centerx, player["y"] - d["rect"].centery)
            if dist_to_door < 55:
                d["open"] = min(1.0, d["open"] + 0.1)
            else:
                d["open"] = max(0.0, d["open"] - 0.03)

        next_x = player["x"] + dx
        if not any(check_collision_rect(next_x, player["y"], player["radius"], w) for w in walls) and \
                not any(
                    d["open"] < 0.4 and check_collision_rect(next_x, player["y"], player["radius"], d["rect"]) for d in
                    doors):
            player["x"] = next_x

        next_y = player["y"] + dy
        if not any(check_collision_rect(player["x"], next_y, player["radius"], w) for w in walls) and \
                not any(
                    d["open"] < 0.4 and check_collision_rect(player["x"], next_y, player["radius"], d["rect"]) for d in
                    doors):
            player["y"] = next_y

        # AI Destek Ajanı
        if ai_agent["hired"]:
            target_x, target_y = player["x"] - 30, player["y"] + 30
            angle_to_p = math.atan2(target_y - ai_agent["y"], target_x - ai_agent["x"])
            if math.hypot(target_x - ai_agent["x"], target_y - ai_agent["y"]) > 18:
                ai_agent["x"] += math.cos(angle_to_p) * ai_agent["speed"]
                ai_agent["y"] += math.sin(angle_to_p) * ai_agent["speed"]

            ai_agent["shoot_cooldown"] += 1
            if ai_agent["shoot_cooldown"] > 30:
                for e in enemies:
                    if math.hypot(ai_agent["x"] - e["x"], ai_agent["y"] - e["y"]) < 300 and line_of_sight(ai_agent["x"],
                                                                                                          ai_agent["y"],
                                                                                                          e["x"],
                                                                                                          e["y"]):
                        ai_agent["shoot_cooldown"] = 0
                        angle = math.atan2(e["y"] - ai_agent["y"], e["x"] - ai_agent["x"])
                        bullets.append({
                            "x": ai_agent["x"], "y": ai_agent["y"],
                            "dx": math.cos(angle) * 20, "dy": math.sin(angle) * 20,
                            "from_player": True
                        })
                        break

        for h in hostages:
            if not h["rescued"]:
                if math.hypot(player["x"] - h["x"], player["y"] - h["y"]) < 25:
                    h["rescued"] = True
            else:
                h["x"] = player["x"] - 18
                h["y"] = player["y"] - 18
                if extraction_zone.collidepoint(player["x"], player["y"]):
                    h["x"] = -100
                    h["y"] = -100
                    money += 200

        if all(h["x"] < 0 for h in hostages):
            game_state = "LEVEL_WON"

        for tool in active_tools[:]:
            tool["timer"] -= 1
            if tool["timer"] <= 0:
                if tool["type"] == "flashbang":
                    for e in enemies:
                        if math.hypot(tool["x"] - e["x"], tool["y"] - e["y"]) < 150:
                            if line_of_sight(tool["x"], tool["y"], e["x"], e["y"]):
                                e["stunned"] = 180
                active_tools.remove(tool)

        for b in bullets[:]:
            b["x"] += b["dx"]
            b["y"] += b["dy"]

            if any(w.collidepoint(b["x"], b["y"]) for w in walls) or any(
                    d["open"] < 0.4 and d["rect"].collidepoint(b["x"], b["y"]) for d in doors):
                bullets.remove(b)
                continue

            if b["from_player"]:
                hit = False
                for e in enemies[:]:
                    if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["radius"]:
                        enemies.remove(e)
                        money += 30
                        hit = True
                        break
                if hit:
                    bullets.remove(b)
            else:
                if math.hypot(b["x"] - player["x"], b["y"] - player["y"]) < player["radius"]:
                    player["health"] -= 25
                    bullets.remove(b)
                    if player["health"] <= 0:
                        game_state = "GAME_OVER"

        # --- AGRESİF DÜŞMAN YAPAY ZEKASI (Seri Atış ve Reload Mekaniği) ---
        for e in enemies:
            if e["stunned"] > 0:
                e["stunned"] -= 1
                continue

            # Düşman reload yapıyorsa
            if e["reloading"]:
                e["reload_timer"] -= 1
                if e["reload_timer"] <= 0:
                    e["clip"] = 4  # Şarjörünü doldurur
                    e["reloading"] = False
                continue

            # Oyuncuyu görüyor mu?
            if math.hypot(player["x"] - e["x"], player["y"] - e["y"]) < 380 and line_of_sight(e["x"], e["y"],
                                                                                              player["x"], player["y"]):
                e["shoot_cooldown"] += 1
                # Çok daha hızlı ve agresif ateş aralığı (25 karede bir)
                if e["shoot_cooldown"] > 25:
                    e["shoot_cooldown"] = 0
                    angle = math.atan2(player["y"] - e["y"], player["x"] - e["x"])
                    bullets.append({
                        "x": e["x"], "y": e["y"],
                        "dx": math.cos(angle) * 11, "dy": math.sin(angle) * 11,
                        "from_player": False
                    })
                    e["clip"] -= 1
                    # Şarjör bittiyse reload yapmaya başla
                    if e["clip"] <= 0:
                        e["reloading"] = True
                        e["reload_timer"] = 90  # Düşman 1.5 saniyede doldurur

    # --- ÇİZİMLER ---

    if game_state == "SHOP":
        screen.fill((15, 20, 30))
        title = big_font.render("FBI OPERASYON ÖNCESİ İKMAL MERKEZİ", True, YELLOW)
        m_text = font.render(f"Mevcut Bütçe: ${money}", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(m_text, (WIDTH // 2 - m_text.get_width() // 2, 180))

        opts = [
            "[1] Yedek Şarjör Satın Al (+12 Mermi) ($80)",
            "[2] Flashbang Satın Al (+1) ($120)",
            "[3] Flare Satın Al (+1) ($120)",
            f"[4] Destek FBI Ajanı Kirala ($300) - Durum: {'KİRALANDI' if ai_agent['hired'] else 'MÜSAİT'}",
            "",
            "--> OPERASYONA BAŞLAMAK İÇİN [ENTER] TUŞUNA BAS <--"
        ]
        for idx, opt in enumerate(opts):
            col = WHITE if idx < 4 else CYAN
            txt = font.render(opt, True, col)
            screen.blit(txt, (WIDTH // 2 - 280, 260 + idx * 45))

    else:
        pygame.draw.rect(screen, (20, 60, 20), extraction_zone)
        pygame.draw.rect(screen, GREEN, extraction_zone, 2)

        for w in walls:
            shadow_rect = pygame.Rect(w.x + 4, w.y + 6, w.width, w.height)
            pygame.draw.rect(screen, (10, 10, 18), shadow_rect)
            pygame.draw.rect(screen, TACTICAL_DARK, w)
            pygame.draw.rect(screen, LIGHT_GRAY, w, 2)

        for d in doors:
            r = d["rect"]
            if d["open"] < 0.95:
                draw_w = int(r.width * (1.0 - d["open"])) if not d["is_vertical"] else r.width
                draw_h = int(r.height * (1.0 - d["open"])) if d["is_vertical"] else r.height
                door_rect = pygame.Rect(r.x, r.y, max(4, draw_w), max(4, draw_h))
                pygame.draw.rect(screen, WOOD_BROWN, door_rect)
                pygame.draw.rect(screen, BLACK, door_rect, 1)

        for h in hostages:
            if h["x"] > 0:
                pygame.draw.circle(screen, ORANGE, (int(h["x"]), int(h["y"])), h["radius"])
                pygame.draw.circle(screen, WHITE, (int(h["x"]), int(h["y"])), 5)

        # Düşmanlar (Agresif ve Reload durum göstergeli)
        for e in enemies:
            dist = math.hypot(player["x"] - e["x"], player["y"] - e["y"])
            is_visible = False
            if dist < 340 and line_of_sight(player["x"], player["y"], e["x"], e["y"]):
                is_visible = True
            for tool in active_tools:
                if tool["type"] == "flare" and math.hypot(tool["x"] - e["x"], tool["y"] - e["y"]) < 140:
                    if line_of_sight(tool["x"], tool["y"], e["x"], e["y"]):
                        is_visible = True

            if is_visible:
                e_angle = math.atan2(player["y"] - e["y"], player["x"] - e["x"])
                color = CYAN if e["stunned"] > 0 else RED
                draw_tactical_agent(screen, e["x"], e["y"], e_angle, color, is_player=False,
                                    is_nemesis_reloading=e["reloading"])

        if ai_agent["hired"]:
            ai_angle = math.atan2(mouse_y - ai_agent["y"], mouse_x - ai_agent["x"])
            draw_tactical_agent(screen, ai_agent["x"], ai_agent["y"], ai_angle, (30, 90, 140), is_player=True)

        # Oyuncu
        player_angle = math.atan2(mouse_y - player["y"], mouse_x - player["x"])
        draw_tactical_agent(screen, player["x"], player["y"], player_angle, FBI_BLUE, is_player=True,
                            is_attacking=(player["knife_anim_timer"] > 0))

        if player["reloading"]:
            progress = (player["reload_duration"] - player["reload_timer"]) / player["reload_duration"]
            pygame.draw.arc(screen, YELLOW, (player["x"] - 22, player["y"] - 22, 44, 44), 0, progress * math.pi * 2, 4)
            rel_txt = font.render("RELOADING...", True, YELLOW)
            screen.blit(rel_txt, (player["x"] - 45, player["y"] - 40))

        for b in bullets:
            color = YELLOW if b["from_player"] else RED
            pygame.draw.circle(screen, color, (int(b["x"]), int(b["y"])), 3)

        for tool in active_tools:
            if tool["type"] == "flare":
                pygame.draw.circle(screen, (255, 200, 50), (int(tool["x"]), int(tool["y"])), 140, 2)
                pygame.draw.circle(screen, (255, 200, 50), (int(tool["x"]), int(tool["y"])), 6)
            elif tool["type"] == "flashbang" and tool["timer"] < 5:
                pygame.draw.circle(screen, WHITE, (int(tool["x"]), int(tool["y"])), 150)

        # --- FOG OF WAR ---
        shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shadow_surface.fill((8, 8, 14, 243))

        ray_count = 160
        max_view_dist = 340
        fov = math.pi * 1.1

        for i in range(ray_count):
            angle = player_angle - fov / 2 + (fov / ray_count) * i
            cx, cy = player["x"], player["y"]

            for step in range(max_view_dist):
                cx += math.cos(angle) * 2.5
                cy += math.sin(angle) * 2.5
                hit_block = any(w.collidepoint(cx, cy) for w in walls) or any(
                    d["open"] < 0.4 and d["rect"].collidepoint(cx, cy) for d in doors)
                if hit_block:
                    break

            pygame.draw.circle(shadow_surface, (0, 0, 0, 0), (int(cx), int(cy)), 22)

        pygame.draw.circle(shadow_surface, (0, 0, 0, 0), (int(player["x"]), int(player["y"])), 55)

        for tool in active_tools:
            if tool["type"] == "flare":
                pygame.draw.circle(shadow_surface, (0, 0, 0, 0), (int(tool["x"]), int(tool["y"])), 130)

        screen.blit(shadow_surface, (0, 0))

        can_throw = line_of_sight(player["x"], player["y"], mouse_x, mouse_y)
        cursor_color = GREEN if can_throw else RED
        pygame.draw.circle(screen, cursor_color, (mouse_x, mouse_y), 6, 2)

        # UI Arayüz
        status_text = font.render(
            f"Bütçe: ${money} | Can: {player['health']} | Mermi: {player['clip']}/{player['max_clip']} (Yedek: {player['reserve_ammo']})",
            True, WHITE)
        tools_text = font.render(
            f"Q: Flare({player['flares']}) | E: Flash({player['flashbangs']}) | R: Reload | SPACE: Bıçak", True, YELLOW)
        screen.blit(status_text, (105, 40))
        screen.blit(tools_text, (520, 40))

        if game_state == "LEVEL_WON":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            text = big_font.render("REHİNELER KURTARILDI! (Market için bir tuşa bas)", True, GREEN)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

        elif game_state == "GAME_OVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((80, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            text = big_font.render("ETKİSİZ HALE GETİRİLDİN! ('R' ile Yeniden Başla)", True, RED)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

    pygame.display.flip()
    clock.tick(60)