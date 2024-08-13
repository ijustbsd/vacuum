import math
import random

import pygame

BG_COLOR = pygame.Color(33, 33, 33)
BALLS_COLOR = pygame.Color(255, 23, 68)
CLEANER_COLOR = pygame.Color(61, 90, 254)

pygame.init()
screen = pygame.display.set_mode([1280, 720], pygame.RESIZABLE)


class Point:
    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 10,
        color: pygame.Color = pygame.Color(255, 255, 255),
        is_movable: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.is_movable = is_movable

    def draw(self) -> None:
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pos_text = f"({self.x}, {self.y})"
        font = pygame.font.SysFont("Comic Sans MS", 16)
        text_w, _ = font.size(pos_text)
        text_surface = font.render(pos_text, True, (255, 255, 255))
        screen.blit(text_surface, (self.x - text_w / 2, self.y + self.radius + 2))


class Ball:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        radius: int = 10,
        color: pygame.Color = pygame.Color(255, 0, 0),
        platform: pygame.Rect | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.platform = platform

        self._clock = pygame.time.Clock()

    def draw(self) -> None:
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self) -> None:
        g = 9.8 * 8

        self._clock.tick()
        dt = self._clock.get_time() / 1000

        self.vy += g * dt
        self.x += self.vx
        self.y += self.vy - 1 / 2 * g * dt**2

        self._ground()
        self._walls()

    def _ground(self):
        if self.y - self.radius < 0:
            if self.vy < 0:
                self.vy *= -0.75
                self.vx *= 0.9
            self.y = 0 + self.radius
        elif self.y + self.radius > screen.get_height():
            if self.vy > 0:
                self.vy *= -0.75
                self.vx *= 0.9
            self.y = screen.get_height() - self.radius

    def _walls(self):
        if self.x - self.radius <= 0:
            if self.vx < 0:
                self.vx *= -0.75
                self.vy *= 0.9
            self.x = 0 + self.radius
        elif self.x + self.radius > screen.get_width():
            if self.vx >= 0:
                self.vx *= -0.75
                self.vy *= 0.9
            self.x = screen.get_width() - self.radius


def get_point_at_pos(x: int, y: int, points: list[Point]) -> Point | None:
    for point in points[::-1]:
        if math.sqrt((x - point.x) ** 2 + (y - point.y) ** 2) <= point.radius:
            return point
    return None


def get_nearest_ball(x, y, balls):
    if not balls:
        return
    nearest = balls[0]
    nearest_dist = (x - nearest.x) ** 2 + (y - nearest.y) ** 2
    for ball in balls[1:]:
        dist = (x - ball.x) ** 2 + (y - ball.y) ** 2
        if nearest_dist > dist:
            nearest = ball
            nearest_dist = dist
    return nearest


def setup_points(cleaner_x: int, points: list[Point]) -> None:
    h = screen.get_height()
    points[0].x = cleaner_x
    points[0].y = h - 185
    points[1].x = cleaner_x - 120
    points[1].y = h - 340
    points[2].x = cleaner_x + 160
    points[2].y = h - 400


def draw_bezier(points: list[Point]) -> None:
    p0, p1, p2, p3 = points
    t = 0.0
    dt = 0.01
    curve_points = []
    while t <= 1:
        x = (1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t**2 * p2.x + t**3 * p3.x
        y = (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t**2 * p2.y + t**3 * p3.y
        curve_points.append((x, y))
        t += dt
    for point in curve_points:
        pygame.draw.circle(screen, CLEANER_COLOR, point, 15)


def draw_cleaner(x: int, target: Ball | None, fill_factor: float) -> None:
    def eye(x, y):
        angle = math.atan2(target.y - y, target.x - x) if target else 0
        px = x + (math.cos(angle) * 5) + 10
        py = y + (math.sin(angle) * 5) + 15
        pygame.draw.ellipse(screen, (255, 255, 255), (x, y, 25, 30))
        pygame.draw.circle(screen, (0, 0, 0), (px, py), 5)

    h = screen.get_height()
    pygame.draw.circle(screen, CLEANER_COLOR, (x - 50, h - 15), 15, width=5)
    pygame.draw.circle(screen, CLEANER_COLOR, (x + 50, h - 15), 15, width=5)
    pygame.draw.rect(screen, CLEANER_COLOR, (x - 80, h - 30, 160, 15), border_radius=10)
    pygame.draw.rect(screen, CLEANER_COLOR, (x - 75, h - 35, 150, 15), border_radius=10)
    pygame.draw.rect(
        screen,
        BALLS_COLOR,
        (x - 68, h - 130 + (100 * (1 - fill_factor)), 136, 100 * fill_factor),
    )
    pygame.draw.rect(screen, CLEANER_COLOR, (x - 70, h - 130, 140, 100), width=5)
    pygame.draw.rect(screen, CLEANER_COLOR, (x - 80, h - 140, 160, 15), border_radius=10)
    pygame.draw.arc(screen, CLEANER_COLOR, (x - 70, h - 190, 140, 100), 0, math.pi, width=50)
    eye(x - 30, h - 175)
    eye(x + 5, h - 175)


def draw_help() -> None:
    font = pygame.font.SysFont("mono", 20)
    lines = (
        "d -- debug",
        "f -- fullscreen",
        "up -- faster",
        "down -- slower",
        "esc -- exit",
    )
    dy = 0
    for line in lines:
        _, text_h = font.size(line)
        text_surface = font.render(line, True, (66, 66, 66))
        screen.blit(text_surface, (0, dy))
        dy += text_h


def main() -> None:
    debug = False
    min_fps = 10
    max_fps = 120
    fps = 60

    clock = pygame.time.Clock()

    points: list[Point] = [
        Point(300, 500, color=pygame.Color(255, 0, 0)),
        Point(400, 460, color=pygame.Color(0, 255, 0), is_movable=True),
        Point(400, 550, color=pygame.Color(0, 0, 255), is_movable=True),
        Point(500, 560, color=pygame.Color(255, 255, 0)),
    ]
    selected_point = None

    balls: list[Ball] = []
    balls_count = 100
    target_ball = None

    cleaner_x = 400
    cleaner_speed = 8
    trunk = points[-1]
    trunk_speed = 10
    balls_catch = 0

    for _ in range(balls_count):
        ball = Ball(
            x=random.randint(0, screen.get_width()),
            y=random.randint(50, screen.get_height() - 50),
            vx=random.randint(-10, 10),
            vy=random.randint(-10, 10),
            color=BALLS_COLOR,
        )
        balls.append(ball)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    debug = not debug
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_UP:
                    fps = min(fps + 10, max_fps)
                if event.key == pygame.K_DOWN:
                    fps = max(fps - 10, min_fps)
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    selected_point = get_point_at_pos(x, y, points)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_point = None
            if event.type == pygame.QUIT:
                running = False
                continue

        screen.fill(BG_COLOR)

        draw_help()

        if not balls:
            balls_catch = 0
            for _ in range(balls_count):
                ball = Ball(
                    x=cleaner_x,
                    y=screen.get_height() - 200,
                    vx=random.randint(-50, 50),
                    vy=random.randint(-50, 50),
                    color=BALLS_COLOR,
                )
                balls.append(ball)

        if target_ball is None:
            target_ball = get_nearest_ball(trunk.x, trunk.y, balls)

        setup_points(cleaner_x, points)
        draw_cleaner(cleaner_x, target_ball, fill_factor=balls_catch / balls_count)

        for ball in balls:
            ball.move()
            ball.draw()

        if target_ball is not None:
            if target_ball.x < cleaner_x:
                cleaner_x -= cleaner_speed
            elif target_ball.x > cleaner_x:
                cleaner_x += cleaner_speed

        if target_ball is not None:
            angle = math.atan2(target_ball.y - trunk.y, target_ball.x - trunk.x)
            d = min(
                math.sqrt((trunk.x - target_ball.x) ** 2 + (trunk.y - target_ball.y) ** 2),
                trunk_speed,
            )
            trunk.x = int(trunk.x + (math.cos(angle) * d))
            trunk.y = int(trunk.y + (math.sin(angle) * d))

        draw_bezier(points)

        if target_ball is not None:
            if (trunk.x - target_ball.x) ** 2 + (trunk.y - target_ball.y) ** 2 < 10:
                balls.remove(target_ball)
                target_ball = None
                balls_catch += 1

        if debug:
            if selected_point is not None and selected_point.is_movable:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                selected_point.x = mouse_x
                selected_point.y = mouse_y

            for point in points:
                point.draw()

            if target_ball is not None:
                target_ball.color = pygame.Color(255, 0, 255)

        pygame.display.flip()
        pygame.display.set_caption(f"FPS: {clock.get_fps():.2f}")
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
