import pygame
import sys

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Code Runner 2D - Syntax Challenge")
clock = pygame.time.Clock()

# Шрифты для текста
font_small = pygame.font.SysFont("Courier New", 18)
font_bold = pygame.font.SysFont("Courier New", 20, bold=True)

# Игрок и его физика
player_rect = pygame.Rect(100, 350, 40, 60)
player_speed = 6
jump_buffer = 0
player_vel_y = 0      # Вертикальная скорость
gravity = 0.6         # Сила гравитации
jump_strength = -12   # Сила прыжка (отрицательная, так как ось Y идет вниз)
is_on_ground = False  # Проверка, стоит ли игрок на платформе

# Загрузка спрайта игрока
try:
    player_image = pygame.image.load("player.png").convert_alpha()
    # Подгоняем размер картинки под размеры нашего player_rect (40x60)
    player_image = pygame.transform.scale(player_image, (40, 60))
except Exception as e:
    print("Не удалось загрузить спрайт игрока, будет использован прямоугольник:", e)
    player_image = None

# Камера
camera_x = 0

# Платформы и Терминал (компьютер)
platforms = [
    pygame.Rect(0, 520, 2500, 80),   # Земля
    pygame.Rect(400, 400, 200, 20),  # Платформа
]
terminal_rect = pygame.Rect(500, 460, 50, 60)  # Сам компьютер на платформе

# Состояние терминала (ввода кода)
typing_mode = False
user_code = ""
task_status = "PRESS 'E' TO INTERACT"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка ввода текста, если терминал открыт
        if typing_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Проверяем введенный код при нажатии Enter
                    if user_code.strip() == "score = 100":
                        task_status = "SUCCESS! CODE COMPILED."
                        typing_mode = False
                    else:
                        task_status = "ERROR: TRY AGAIN (score = 100)"
                elif event.key == pygame.K_BACKSPACE:
                    user_code = user_code[:-1]
                else:
                    # Добавляем символ в строку ввода
                    if len(user_code) < 25:
                        user_code += event.unicode
        else:
            # Обычное управление вне терминала
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # Проверяем, стоит ли игрок рядом с терминалом
                    if player_rect.colliderect(terminal_rect):
                        typing_mode = True
                        user_code = ""
                # Прыжок по нажатию пробела, W или стрелки вверх
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    jump_buffer = 10  # Даем запас в 10 кадров «памяти» на нажатие


    # Если терминал не активен, обрабатываем движение и физику
    if not typing_mode:
        keys = pygame.key.get_pressed()

        # Горизонтальное движение
        move_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = player_speed

        # Движение по X и горизонтальные столкновения
        player_rect.x += move_x

        for p in platforms:
            if player_rect.colliderect(p):
                if move_x > 0:
                    player_rect.right = p.left
                elif move_x < 0:
                    player_rect.left = p.right

        # Уменьшаем буфер прыжка
        if jump_buffer > 0:
            jump_buffer -= 1

        # Применяем гравитацию
        player_vel_y += gravity
        player_rect.y += player_vel_y

        # Проверяем вертикальные столкновения
        is_on_ground = False

        for p in platforms:
            if player_rect.colliderect(p):
                if player_vel_y > 0:
                    # Игрок падает на платформу
                    player_rect.bottom = p.top
                    player_vel_y = 0
                    is_on_ground = True

                elif player_vel_y < 0:
                    # Игрок ударился головой
                    player_rect.top = p.bottom
                    player_vel_y = 0

        # Выполняем прыжок, если игрок на земле
        if is_on_ground and jump_buffer > 0:
            player_vel_y = jump_strength
            is_on_ground = False
            jump_buffer = 0

    # Ограничения движения в рамках уровня
    player_rect.x = max(0, min(player_rect.x, 2500 - player_rect.width))

    # Камера
    target_camera_x = player_rect.x - 300
    camera_x += (target_camera_x - camera_x) * 0.1
    camera_x = max(0, min(camera_x, 2500 - SCREEN_WIDTH))

    # ОТРИСОВКА
    screen.fill((15, 15, 35))

    # Рисуем платформы
    for p in platforms:
        r = p.copy()
        r.x -= camera_x
        pygame.draw.rect(screen, (0, 150, 255), r)

    # Рисуем терминал
    term_render = terminal_rect.copy()
    term_render.x -= camera_x
    pygame.draw.rect(screen, (0, 255, 200), term_render)

   # Рисуем игрока
    p_render = player_rect.copy()
    p_render.x -= camera_x

    if player_image:
        screen.blit(player_image, (p_render.x, p_render.y))
    else:
        # Запасной вариант, если картинка не найдена
        pygame.draw.rect(screen, (0, 255, 128), p_render)

    # Подсказка возле терминала
    if player_rect.colliderect(terminal_rect) and not typing_mode:
        prompt_surf = font_small.render(
            "[E] Terminal", True, (255, 255, 255)
        )
        screen.blit(
            prompt_surf,
            (terminal_rect.x - camera_x - 10, terminal_rect.y - 30)
        )

    # Окно задания
    if typing_mode:
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        win_rect = pygame.Rect(200, 150, 400, 300)
        pygame.draw.rect(screen, (25, 25, 50), win_rect)
        pygame.draw.rect(screen, (0, 255, 128), win_rect, 2)

        title_surf = font_bold.render(
            "SYNTAX CHALLENGE", True, (0, 255, 128)
        )
        mission_surf = font_small.render(
            "Mission: Type 'score = 100'", True, (200, 200, 200)
        )

        status_color = (
            (255, 100, 100)
            if "ERROR" in task_status
            else (100, 255, 100)
        )

        status_surf = font_small.render(
            task_status, True, status_color
        )

        input_rect = pygame.Rect(230, 280, 340, 40)
        pygame.draw.rect(screen, (10, 10, 25), input_rect)
        pygame.draw.rect(screen, (0, 200, 255), input_rect, 1)

        code_surf = font_small.render(
            user_code + "_", True, (255, 255, 255)
        )

        screen.blit(title_surf, (win_rect.x + 20, win_rect.y + 20))
        screen.blit(mission_surf, (win_rect.x + 20, win_rect.y + 60))
        screen.blit(status_surf, (win_rect.x + 20, win_rect.y + 100))
        screen.blit(code_surf, (input_rect.x + 10, input_rect.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
