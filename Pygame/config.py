# config.py

# Screen settings
WIDTH, HEIGHT = 1600, 1600  # 遊戲窗口大小
TILE_SIZE = 80  # 每個瓦片的像素大小
FPS = 60  # 遊戲刷新率

# Gameplay constants
DISTANCE_THRESHOLD = 300  # 追蹤者進入追蹤狀態的距離閾值
WANDER_INTERVAL = 10.0  # 游蕩模式目標更換的間隔時間（秒）
WAITING_DURATION = 5.0  # 等待狀態持續時間（秒）
WANDER_SPEED = 100  # 游蕩模式速度
FOLLOW_SPEED = 300  # 追蹤模式速度
RUN_SPEED = 250  # 玩家奔跑速度
SNEAK_SPEED = 75  # 玩家潛行速度
VISIBILITY_RADIUS = 200  # 玩家可見區域半徑
MIN_TARGET_DISTANCE = 100  # 追蹤者與目標之間的最小距離

# Colors
WHITE = (50, 60, 60)  # 白色背景
BLACK = (30, 30, 35)  # 色牆壁
BLUE = (0, 0, 255)  # 游蕩狀態
GREEN = (0, 255, 0)  # 追蹤狀態
YELLOW = (255, 255, 0)  # 等待狀態
RED = (160, 160, 0)  # 玩家

# Radar settings
RADAR_CENTER = (WIDTH - 250, 250)  # Position on screen
RADAR_RADIUS = 200