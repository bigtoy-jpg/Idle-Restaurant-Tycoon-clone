import pygame
import random
import time
import math

pygame.init()

# ------------------------------------------------------------------------
# WINDOW / DISPLAY
# ------------------------------------------------------------------------
WIN_WIDTH, WIN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("All Upgrades - Restaurant Tycoon Demo")

current_width, current_height = WIN_WIDTH, WIN_HEIGHT

# ------------------------------------------------------------------------
# COLORS & FONTS
# ------------------------------------------------------------------------
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GREEN  = (0, 200,   0)
RED    = (200, 0,   0)
BROWN  = (139, 69,  19)
BLUE   = (0,   0,  255)
PURPLE = (128, 0,  128)

base_font = pygame.font.Font(None, 36)

# ------------------------------------------------------------------------
# CORE GAME STATE
# ------------------------------------------------------------------------
money = 100000000000000000000000000000000000000000000000000000000000000000000000
income_per_second = 1

# Timers
last_income_time = time.time()
last_food_time = time.time()
last_customer_spawn_time = time.time()
customer_spawn_delay = 5  # default 1 minute

chef_cook_interval = 2.0
conveyor_speed = 1.0

# Basic older upgrades
upgrade_cost           = 50   # "Upgrade Income"
chef_upgrade_cost      = 100  # Chef Speed
conveyor_upgrade_cost  = 150  # Conveyor Speed
chair_upgrade_cost     = 200  # Extra Chairs
hire_chef_cost         = 300  # Additional Chefs

# ------------------------------------------------------------------------
# NEW UPGRADE TRACKERS (20 total)
# ------------------------------------------------------------------------

# 1) Advertising (Marketing) - lowers spawn delay
marketing_level = 0
marketing_cost  = 250

# 2) Food Quality - increases per-customer tip
food_quality_level = 0
food_quality_cost  = 200

# 3) Menu Variety - also increases per-customer tip
menu_variety_level = 0
menu_variety_cost  = 300

# 4) Manager - each manager adds +1 income/sec & speeds up cooking
manager_count = 0
manager_cost  = 350

# 5) Online Ordering - periodic extra income
online_ordering_unlocked = False
online_ordering_cost     = 500
last_online_order_time   = time.time()
online_order_interval    = 15  # base 15 sec

# 6) Delivery Drones - halves the online order interval
delivery_drones_unlocked = False
delivery_drones_cost     = 800

# 7) Sous Chef Training - reduce chef cook interval further
sous_chef_training_level = 0
sous_chef_training_cost  = 400

# 8) Barista Bar - periodic coffee revenue
barista_bar_unlocked = False
barista_bar_cost     = 500
last_barista_time    = time.time()
barista_interval     = 15

# 9) Automation Software - +1 income/sec
automation_software_unlocked = False
automation_software_cost     = 600

# 10) Security & Surveillance - prevents random theft
security_surveillance_unlocked = False
security_surveillance_cost     = 250
last_theft_check_time = time.time()
theft_check_interval = 20  # check every 20s if no security

# 11) Kitchen Bot Assistants - produce extra food occasionally
kitchen_bots_unlocked = False
kitchen_bots_cost     = 700
kitchen_bot_counter   = 0  # track how many times a chef has cooked

# 12) Sushi Conveyor Extension - chance to produce sushi, worth higher tips
sushi_conveyor_unlocked = False
sushi_conveyor_cost     = 800
sushi_chance            = 0.0

# 13) Meal Kit Subscription - recurring large subscription payment
meal_kit_unlocked = False
meal_kit_cost     = 400
last_meal_kit_time = time.time()
meal_kit_interval  = 20

# 14) AI-Powered Waitlist - lowers spawn delay
ai_waitlist_unlocked = False
ai_waitlist_cost     = 300

# 15) Cocktail-Making Robot - each chef cook yields a small tip
robot_bartender_unlocked = False
robot_bartender_cost     = 600

# 16) Snack Vending Machines - small periodic vending machine revenue
snack_vending_unlocked = False
snack_vending_cost     = 200
last_snack_time        = time.time()
snack_interval         = 15

# For synergy demonstration:
#  - Chef Speed, Additional Chefs, Conveyor Speed, Extra Chairs are older.

# ------------------------------------------------------------------------
# TAB / SCREEN MANAGEMENT
# ------------------------------------------------------------------------
current_tab = "GAMEPLAY"  # or "UPGRADES"

# ------------------------------------------------------------------------
# GAME OBJECTS LISTS
# ------------------------------------------------------------------------
chairs     = []
customers  = []
food_items = []
chefs      = []

# ------------------------------------------------------------------------
# BUTTON RECTANGLES
# ------------------------------------------------------------------------
upgrade_tab_button   = pygame.Rect(50,  50, 200, 50)
back_to_game_button  = pygame.Rect(50,  50, 200, 50)

# NEW UPGRADE BUTTONS (we'll place them in columns/rows)
marketing_button         = pygame.Rect(50,   150, 250, 50)
food_quality_button      = pygame.Rect(50,   220, 250, 50)
menu_variety_button      = pygame.Rect(50,   290, 250, 50)
manager_button           = pygame.Rect(50,   360, 250, 50)
online_ordering_button   = pygame.Rect(50,   430, 250, 50)
delivery_drones_button   = pygame.Rect(50,   500, 250, 50)

sous_chef_button         = pygame.Rect(350, 150, 250, 50)
barista_bar_button       = pygame.Rect(350, 220, 250, 50)
automation_button        = pygame.Rect(350, 290, 250, 50)
security_button          = pygame.Rect(350, 360, 250, 50)
kitchen_bots_button      = pygame.Rect(350, 430, 250, 50)
sushi_conveyor_button    = pygame.Rect(350, 500, 250, 50)

meal_kit_button          = pygame.Rect(650, 150, 250, 50)
ai_waitlist_button       = pygame.Rect(650, 220, 250, 50)
robot_bartender_button   = pygame.Rect(650, 290, 250, 50)
snack_vending_button     = pygame.Rect(650, 360, 250, 50)

# Older upgrades
income_upgrade_button    = pygame.Rect(650, 430, 200, 50)
chef_upgrade_button      = pygame.Rect(650, 500, 200, 50)
conveyor_upgrade_button  = pygame.Rect(900, 150, 200, 50)
chair_upgrade_button     = pygame.Rect(900, 220, 200, 50)
add_chef_button          = pygame.Rect(900, 290, 200, 50)

# ------------------------------------------------------------------------
# HELPER: DRAW BUTTON WITH TEXT
# ------------------------------------------------------------------------
def draw_button_with_text(surface, rect, text, bg_color, text_color, font):
    pygame.draw.rect(surface, bg_color, rect)
    cur_size = font.get_height()
    temp_font = pygame.font.Font(None, cur_size)
    tw, th = temp_font.size(text)
    pad = 10
    while tw > (rect.width - pad) and cur_size > 10:
        cur_size -= 1
        temp_font = pygame.font.Font(None, cur_size)
        tw, th = temp_font.size(text)
    text_surf = temp_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

# ------------------------------------------------------------------------
# CLASSES
# ------------------------------------------------------------------------
class ConveyorBelt:
    def __init__(self):
        # Generate an ellipse of points
        cx = WIN_WIDTH // 2
        cy = WIN_HEIGHT // 2
        self.points = [
            (cx + 200 * math.cos(math.radians(a)),
             cy + 100 * math.sin(math.radians(a)))
            for a in range(0, 360, 10)
        ]

    def draw(self):
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, BROWN, self.points[i], self.points[i+1], 5)
        pygame.draw.line(screen, BROWN, self.points[-1], self.points[0], 5)

class Food:
    """Normal food on the conveyor."""
    def __init__(self):
        self.index = 0
        self.color = RED
    def move(self):
        self.index = int((self.index + conveyor_speed) % len(conveyor_belt.points))
    def draw(self):
        if 0 <= self.index < len(conveyor_belt.points):
            x, y = conveyor_belt.points[self.index]
            pygame.draw.circle(screen, self.color, (int(x), int(y)), 10)

class SushiFood(Food):
    """Special sushi that yields higher tips if sushi_conveyor_unlocked."""
    def __init__(self):
        super().__init__()
        self.color = PURPLE  # visually distinguish sushi

class Chef:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = BLUE
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 40, 40))

    def cook(self):
        global last_food_time, money, kitchen_bot_counter
        # Effective cook interval is influenced by:
        # - base chef_cook_interval
        # - manager_count
        # - sous_chef_training_level
        manager_reduction = 0.1 * manager_count
        sous_chef_reduction = 0.1 * sous_chef_training_level
        effective_interval = max(0.1, chef_cook_interval - manager_reduction - sous_chef_reduction)

        if time.time() - last_food_time >= effective_interval:
            # Normal or sushi
            if sushi_conveyor_unlocked and random.random() < sushi_chance:
                food_items.append(SushiFood())
            else:
                food_items.append(Food())

            last_food_time = time.time()
            kitchen_bot_counter += 1

            # If Kitchen Bots are unlocked, produce an extra piece every 5th cook
            if kitchen_bots_unlocked and (kitchen_bot_counter % 5 == 0):
                if sushi_conveyor_unlocked and random.random() < sushi_chance:
                    food_items.append(SushiFood())
                else:
                    food_items.append(Food())

            # If we have a robot bartender, get a small tip each cook
            if robot_bartender_unlocked:
                money += random.randint(2, 5)

class Chair:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.occupied = False
    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, 30, 30))

class Customer:
    def __init__(self):
        self.chair = None
        for ch in chairs:
            if not ch.occupied:
                ch.occupied = True
                self.chair = ch
                break
        if not self.chair:
            return
        self.x = self.chair.x + 15
        self.y = self.chair.y + 15
        self.reach_x = self.x
        self.reach_y = self.y
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.hungry = True

    def draw(self):
        if self.chair:
            pygame.draw.circle(screen, self.color, (self.x, self.y), 20)
            pygame.draw.line(screen, self.color, (self.x, self.y), (self.reach_x, self.reach_y), 3)

    def check_food(self):
        global money
        if not self.chair:
            return
        for f in food_items:
            if 0 <= f.index < len(conveyor_belt.points):
                fx, fy = conveyor_belt.points[f.index]
                if abs(self.x - fx) < 50 and abs(self.y - fy) < 50 and self.hungry:
                    self.reach_x, self.reach_y = fx, fy
                    if abs(self.reach_x - fx) < 5 and abs(self.reach_y - fy) < 5:
                        # Sushi might yield a bigger tip
                        if isinstance(f, SushiFood):
                            tip = random.randint(10, 20)
                        else:
                            tip = random.randint(5, 15)
                        # Add synergy from Food Quality & Menu Variety
                        tip += (2 * food_quality_level) + (1 * menu_variety_level)
                        # Gain money
                        money += tip
                        # Remove the food
                        food_items.remove(f)
                        self.hungry = False
                        self.chair.occupied = False
                        customers.remove(self)
                        break

# ------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------
def add_chairs(num_chairs, radius_offset=0):
    cx = WIN_WIDTH // 2
    cy = WIN_HEIGHT // 2
    for angle in range(0, 360, 360 // num_chairs):
        rx = 220 + radius_offset
        ry = 120 + radius_offset
        x = cx + rx * math.cos(math.radians(angle))
        y = cy + ry * math.sin(math.radians(angle))
        chairs.append(Chair(int(x), int(y)))

# ------------------------------------------------------------------------
# CREATE INITIAL OBJECTS
# ------------------------------------------------------------------------
conveyor_belt = ConveyorBelt()
chefs.append(Chef(WIN_WIDTH // 2, (WIN_HEIGHT // 2) - 50))
add_chairs(8, 0)

# For random theft checks if no security
def maybe_theft():
    global money
    if security_surveillance_unlocked:
        return
    # 30% chance to lose random money
    if random.random() < 0.3:
        stolen = random.randint(10, 50)
        money = max(0, money - stolen)

# ------------------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------------------
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    screen.fill(WHITE)
    now = time.time()

    # -------------------------
    # Passive Income & Timers
    # -------------------------
    # 1) Basic passive income each second
    if now - last_income_time >= 1:
        # +1 for each Manager, +1 if Automation is unlocked
        manager_bonus = manager_count
        automation_bonus = 1 if automation_software_unlocked else 0
        money += (income_per_second + manager_bonus + automation_bonus)
        last_income_time = now

    # 2) Online Ordering
    if online_ordering_unlocked:
        if now - last_online_order_time >= online_order_interval:
            # synergy with menu variety
            money += (25 + (menu_variety_level * 2))
            last_online_order_time = now

    # 3) Barista Bar
    if barista_bar_unlocked:
        if now - last_barista_time >= barista_interval:
            money += random.randint(10, 25)
            last_barista_time = now

    # 4) Meal Kit Subscription
    if meal_kit_unlocked:
        if now - last_meal_kit_time >= meal_kit_interval:
            money += 30
            last_meal_kit_time = now

    # 5) Snack Vending Machines
    if snack_vending_unlocked:
        if now - last_snack_time >= snack_interval:
            money += random.randint(5, 15)
            last_snack_time = now

    # 6) Check for theft if no security
    if now - last_theft_check_time >= theft_check_interval:
        maybe_theft()
        last_theft_check_time = now

    # -------------------------
    # Customer Spawning
    # -------------------------
    if now - last_customer_spawn_time >= customer_spawn_delay:
        new_cust = Customer()
        if new_cust.chair:
            customers.append(new_cust)
        last_customer_spawn_time = now

    # Update logic depending on tab
    if current_tab == "GAMEPLAY":
        # Chefs cook
        for chf in chefs:
            chf.cook()

        # Move food
        for f in food_items:
            f.move()

        # Check if customers take food
        for c in customers[:]:
            c.check_food()

        # DRAW GAMEPLAY
        conveyor_belt.draw()
        for chair in chairs:
            chair.draw()
        for chf in chefs:
            chf.draw()
        for f in food_items:
            f.draw()
        for c in customers:
            c.draw()

        # "Upgrades" button
        draw_button_with_text(screen, upgrade_tab_button, "Upgrades", GREEN, BLACK, base_font)

        # Show money
        money_text = base_font.render(f"Money: ${money}", True, BLACK)
        screen.blit(money_text, (50, 120))

    else:
        # current_tab == "UPGRADES"
        # "Back" button
        draw_button_with_text(screen, back_to_game_button, "Back", GREEN, BLACK, base_font)

        # 1) Marketing
        draw_button_with_text(
            screen, marketing_button,
            f"Marketing Lvl {marketing_level} (${marketing_cost})",
            GREEN, BLACK, base_font
        )
        # 2) Food Quality
        draw_button_with_text(
            screen, food_quality_button,
            f"Food Quality Lvl {food_quality_level} (${food_quality_cost})",
            GREEN, BLACK, base_font
        )
        # 3) Menu Variety
        draw_button_with_text(
            screen, menu_variety_button,
            f"Menu Variety Lvl {menu_variety_level} (${menu_variety_cost})",
            GREEN, BLACK, base_font
        )
        # 4) Manager
        draw_button_with_text(
            screen, manager_button,
            f"Manager x{manager_count} (${manager_cost})",
            GREEN, BLACK, base_font
        )
        # 5) Online Ordering
        if not online_ordering_unlocked:
            draw_button_with_text(
                screen, online_ordering_button,
                f"Online Ordering (${online_ordering_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, online_ordering_button,
                "Online Ordering (Active)",
                GREEN, BLACK, base_font
            )
        # 6) Delivery Drones
        if not delivery_drones_unlocked:
            draw_button_with_text(
                screen, delivery_drones_button,
                f"Delivery Drones (${delivery_drones_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, delivery_drones_button,
                "Delivery Drones (Active)",
                GREEN, BLACK, base_font
            )
        # 7) Sous Chef Training
        draw_button_with_text(
            screen, sous_chef_button,
            f"Sous Chef Lvl {sous_chef_training_level} (${sous_chef_training_cost})",
            GREEN, BLACK, base_font
        )
        # 8) Barista Bar
        if not barista_bar_unlocked:
            draw_button_with_text(
                screen, barista_bar_button,
                f"Barista Bar (${barista_bar_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, barista_bar_button,
                "Barista Bar (Active)",
                GREEN, BLACK, base_font
            )
        # 9) Automation
        if not automation_software_unlocked:
            draw_button_with_text(
                screen, automation_button,
                f"Automation (${automation_software_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, automation_button,
                "Automation (Active)",
                GREEN, BLACK, base_font
            )
        # 10) Security
        if not security_surveillance_unlocked:
            draw_button_with_text(
                screen, security_button,
                f"Security (${security_surveillance_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, security_button,
                "Security (Active)",
                GREEN, BLACK, base_font
            )
        # 11) Kitchen Bots
        if not kitchen_bots_unlocked:
            draw_button_with_text(
                screen, kitchen_bots_button,
                f"Kitchen Bots (${kitchen_bots_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, kitchen_bots_button,
                "Kitchen Bots (Active)",
                GREEN, BLACK, base_font
            )
        # 12) Sushi Conveyor
        if not sushi_conveyor_unlocked:
            draw_button_with_text(
                screen, sushi_conveyor_button,
                f"Sushi Ext (${sushi_conveyor_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, sushi_conveyor_button,
                "Sushi Ext (Active)",
                GREEN, BLACK, base_font
            )
        # 13) Meal Kit
        if not meal_kit_unlocked:
            draw_button_with_text(
                screen, meal_kit_button,
                f"Meal Kits (${meal_kit_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, meal_kit_button,
                "Meal Kits (Active)",
                GREEN, BLACK, base_font
            )
        # 14) AI Waitlist
        if not ai_waitlist_unlocked:
            draw_button_with_text(
                screen, ai_waitlist_button,
                f"AI Waitlist (${ai_waitlist_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, ai_waitlist_button,
                "AI Waitlist (Active)",
                GREEN, BLACK, base_font
            )
        # 15) Robot Bartender
        if not robot_bartender_unlocked:
            draw_button_with_text(
                screen, robot_bartender_button,
                f"Robot Bartender (${robot_bartender_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, robot_bartender_button,
                "Robot Bartender (Active)",
                GREEN, BLACK, base_font
            )
        # 16) Snack Vending
        if not snack_vending_unlocked:
            draw_button_with_text(
                screen, snack_vending_button,
                f"Snack Vending (${snack_vending_cost})",
                GREEN, BLACK, base_font
            )
        else:
            draw_button_with_text(
                screen, snack_vending_button,
                "Snack Vending (Active)",
                GREEN, BLACK, base_font
            )

        # Older upgrades (17) Income, (18) Chef Speed, (19) Conveyor Speed, (20) Extra Chairs, plus "Additional Chefs"
        draw_button_with_text(screen, income_upgrade_button,   f"Income (${upgrade_cost})", GREEN, BLACK, base_font)
        draw_button_with_text(screen, chef_upgrade_button,     f"Chef Speed (${chef_upgrade_cost})", GREEN, BLACK, base_font)
        draw_button_with_text(screen, conveyor_upgrade_button, f"Conveyor Speed (${conveyor_upgrade_cost})", GREEN, BLACK, base_font)
        draw_button_with_text(screen, chair_upgrade_button,    f"Add Chairs (${chair_upgrade_cost})", GREEN, BLACK, base_font)
        draw_button_with_text(screen, add_chef_button,         f"Hire Chef (${hire_chef_cost})", GREEN, BLACK, base_font)

        # Show money
        money_text = base_font.render(f"Money: ${money}", True, BLACK)
        screen.blit(money_text, (50, 50))

    # --------------------------------------------------------------------
    # EVENT HANDLING
    # --------------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
            # You could re-center or re-scale chairs, belt, etc., here if desired

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_tab == "GAMEPLAY":
                if upgrade_tab_button.collidepoint(event.pos):
                    current_tab = "UPGRADES"
            else:
                # current_tab == "UPGRADES"
                if back_to_game_button.collidepoint(event.pos):
                    current_tab = "GAMEPLAY"
                # New Upgrades
                elif marketing_button.collidepoint(event.pos) and money >= marketing_cost:
                    money -= marketing_cost
                    marketing_level += 1
                    # reduce spawn delay by 5, min 10
                    customer_spawn_delay = max(10, customer_spawn_delay - 5)
                    marketing_cost = int(marketing_cost * 1.5)

                elif food_quality_button.collidepoint(event.pos) and money >= food_quality_cost:
                    money -= food_quality_cost
                    food_quality_level += 1
                    food_quality_cost = int(food_quality_cost * 1.5)

                elif menu_variety_button.collidepoint(event.pos) and money >= menu_variety_cost:
                    money -= menu_variety_cost
                    menu_variety_level += 1
                    menu_variety_cost = int(menu_variety_cost * 1.5)

                elif manager_button.collidepoint(event.pos) and money >= manager_cost:
                    money -= manager_cost
                    manager_count += 1
                    manager_cost = int(manager_cost * 2)

                elif online_ordering_button.collidepoint(event.pos) and (not online_ordering_unlocked) and money >= online_ordering_cost:
                    money -= online_ordering_cost
                    online_ordering_unlocked = True
                    online_ordering_cost = 999999999

                elif delivery_drones_button.collidepoint(event.pos) and (not delivery_drones_unlocked) and money >= delivery_drones_cost:
                    money -= delivery_drones_cost
                    delivery_drones_unlocked = True
                    # half the interval
                    online_order_interval = max(5, online_order_interval * 0.5)
                    delivery_drones_cost = 999999999

                elif sous_chef_button.collidepoint(event.pos) and money >= sous_chef_training_cost:
                    money -= sous_chef_training_cost
                    sous_chef_training_level += 1
                    sous_chef_training_cost = int(sous_chef_training_cost * 1.6)

                elif barista_bar_button.collidepoint(event.pos) and (not barista_bar_unlocked) and money >= barista_bar_cost:
                    money -= barista_bar_cost
                    barista_bar_unlocked = True

                elif automation_button.collidepoint(event.pos) and (not automation_software_unlocked) and money >= automation_software_cost:
                    money -= automation_software_cost
                    automation_software_unlocked = True

                elif security_button.collidepoint(event.pos) and (not security_surveillance_unlocked) and money >= security_surveillance_cost:
                    money -= security_surveillance_cost
                    security_surveillance_unlocked = True
                    security_surveillance_cost = 999999999

                elif kitchen_bots_button.collidepoint(event.pos) and (not kitchen_bots_unlocked) and money >= kitchen_bots_cost:
                    money -= kitchen_bots_cost
                    kitchen_bots_unlocked = True

                elif sushi_conveyor_button.collidepoint(event.pos) and (not sushi_conveyor_unlocked) and money >= sushi_conveyor_cost:
                    money -= sushi_conveyor_cost
                    sushi_conveyor_unlocked = True
                    sushi_chance = 0.3  # 30% chance
                    sushi_conveyor_cost = 999999999

                elif meal_kit_button.collidepoint(event.pos) and (not meal_kit_unlocked) and money >= meal_kit_cost:
                    money -= meal_kit_cost
                    meal_kit_unlocked = True

                elif ai_waitlist_button.collidepoint(event.pos) and (not ai_waitlist_unlocked) and money >= ai_waitlist_cost:
                    money -= ai_waitlist_cost
                    ai_waitlist_unlocked = True
                    # reduce spawn delay by 15, min 10
                    customer_spawn_delay = max(10, customer_spawn_delay - 15)

                elif robot_bartender_button.collidepoint(event.pos) and (not robot_bartender_unlocked) and money >= robot_bartender_cost:
                    money -= robot_bartender_cost
                    robot_bartender_unlocked = True

                elif snack_vending_button.collidepoint(event.pos) and (not snack_vending_unlocked) and money >= snack_vending_cost:
                    money -= snack_vending_cost
                    snack_vending_unlocked = True

                # Older upgrades
                elif income_upgrade_button.collidepoint(event.pos) and money >= upgrade_cost:
                    money -= upgrade_cost
                    income_per_second += 1
                    upgrade_cost += 25

                elif chef_upgrade_button.collidepoint(event.pos) and money >= chef_upgrade_cost:
                    money -= chef_upgrade_cost
                    # base cook interval reduction
                    chef_cook_interval = max(0.5, chef_cook_interval - 0.5)
                    chef_upgrade_cost = int(chef_upgrade_cost * 1.5)

                elif conveyor_upgrade_button.collidepoint(event.pos) and money >= conveyor_upgrade_cost:
                    money -= conveyor_upgrade_cost
                    conveyor_speed += 0.5
                    conveyor_upgrade_cost = int(conveyor_upgrade_cost * 1.5)

                elif chair_upgrade_button.collidepoint(event.pos) and money >= chair_upgrade_cost:
                    money -= chair_upgrade_cost
                    add_chairs(6, 30 + len(chairs)//2)
                    chair_upgrade_cost = int(chair_upgrade_cost * 1.5)

                elif add_chef_button.collidepoint(event.pos) and money >= hire_chef_cost:
                    money -= hire_chef_cost
                    new_chef_y = (current_height // 2) - 50 + (len(chefs)*60)
                    chefs.append(Chef(current_width // 2, new_chef_y))
                    hire_chef_cost = int(hire_chef_cost * 1.5)

    pygame.display.flip()

pygame.quit()
