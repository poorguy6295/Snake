import tkinter as tk
from PIL import Image, ImageTk
from random import randint

# GAME CONSTANTS
WIDTH = 800
HEIGHT = 800
BG_COLOR = "black"
LEFT = "Left"
UP = "Up"
RIGHT = "Right"
DOWN = "Down"
DIRECTION = {
  LEFT: (-1, 0),
  UP: (0, -1),
  RIGHT: (1, 0),
  DOWN: (0, 1)
}
REVERT_DIRECTION = {
  LEFT: RIGHT,
  UP: DOWN,
  RIGHT: LEFT,
  DOWN: UP
}
SNAKE_SIZE = 40
SNAKE_SPEED = 500 # so ms moi buoc chay
SNAKE_INIT_DIRECTION = RIGHT
SNAKE_INIT_HEAD_COORD = (100, 20)
SNAKE_INIT_LENGTH = 3
APPLE_SIZE = 40

class SnakeApp(tk.Tk):
  
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.cur_frame = None
    self.geometry(str(WIDTH) + "x" + str(HEIGHT))
    self.show_screen(GameScreen)

  # Chuyen sang screen moi
  def show_screen(self, Screen):
    if self.cur_frame is not None:
      self.cur_frame.pack_forget()
    new_frame = Screen(self)
    new_frame.pack()
    self.cur_frame = new_frame


class MenuScreen(tk.Frame):
  def __init__(self, container):
    super().__init__(container)

    game_title = tk.Label(self, text="Snake Game", font=("Helvetica", 20))
    game_title.pack(fill = tk.X, pady = 50)
    
    start_btn = tk.Button(self, text = "Start", command=lambda: container.show_screen(EnterNameScreen))
    start_btn.pack(fill = tk.X, pady = 10)

    leader_board_btn = tk.Button(self, text = "Show leaderboard")
    leader_board_btn.pack(fill = tk.X, pady = 10)


class EnterNameScreen(tk.Frame):
  def __init__(self, container):
    super().__init__(container)

    name_label = tk.Label(self, text="Player name", font=("Helvetica", 10))
    name_label.pack(pady=(50, 5))

    name_input = tk.Entry(self)
    name_input.pack()

    play_btn = tk.Button(self, text = "Play", command=lambda: container.show_screen(GameScreen))
    play_btn.pack(pady=10)


class GameScreen(tk.Canvas):
  def __init__(self, container):
    super().__init__(container)
    self.container = container
    self.configure(width=WIDTH, height=HEIGHT)
    self.snake = Snake(self)
    self.apple = Apple(self)
    self.point = 0
    self.bind_all("<Key>", self.onKeyPress)
    self.game_running = True
    self.update()

  # Xu ly khi user an vao ban phim
  def onKeyPress(self, event):
    key = event.keysym
    for direction in DIRECTION.keys():
      if key == direction and self.snake.direction != REVERT_DIRECTION[direction]:
        self.snake.direction = direction

  # Di chuyen ran va ve lai game
  def update(self):
    if self.game_running:
      # Tinh toan buoc di
      self.snake.move()

      # Ve lai game
      self.delete("all")
      self.snake.render()
      self.apple.render()

      self.after(SNAKE_SPEED, self.update)

  def snake_eat_apple(self):
    self.apple.generate_new()
    self.point += 1

  def game_over(self):
    self.game_running = False
    self.container.show_screen(MenuScreen)


class Snake:
  def __init__(self, game_canvas):
    self.game_canvas = game_canvas
    self.headImg = ImageTk.PhotoImage(Image.open("head.png").resize((SNAKE_SIZE, SNAKE_SIZE)))
    self.bodyImg = ImageTk.PhotoImage(Image.open("body.png").resize((SNAKE_SIZE, SNAKE_SIZE)))
    self.direction = SNAKE_INIT_DIRECTION

    # Tinh toa do ran ban dau
    next_move = DIRECTION[REVERT_DIRECTION[self.direction]]
    self.coords = [
      (
        (SNAKE_INIT_HEAD_COORD[0] + x * next_move[0] * SNAKE_SIZE) % WIDTH,
        (SNAKE_INIT_HEAD_COORD[1] + x * next_move[1] * SNAKE_SIZE) % HEIGHT
      )
      for x in range(SNAKE_INIT_LENGTH)
    ]

  # Di chuyen ran
  def move(self):
    next_move = DIRECTION[self.direction]
    new_head = (
      (self.coords[0][0] + next_move[0] * SNAKE_SIZE) % WIDTH,
      (self.coords[0][1] + next_move[1] * SNAKE_SIZE) % HEIGHT
    )

    # Kiem tra neu ran an duoc tao
    if self.check_overlap(new_head, SNAKE_SIZE, self.game_canvas.apple.coord, APPLE_SIZE):
      self.game_canvas.snake_eat_apple()
      self.coords = [new_head] + self.coords
    else:
      self.coords = [new_head] + self.coords[:-1]

    # Kiem tra tu can minh
    for body_coord in self.coords[1:]:
      if self.check_overlap(new_head, SNAKE_SIZE, body_coord, SNAKE_SIZE):
        self.game_canvas.game_over()

  def check_overlap(self, coord1, size1, coord2, size2):
    x1 = max(coord1[0] - size1 / 2, coord2[0] - size2 / 2)
    x2 = min(coord1[0] + size1 / 2, coord2[0] + size2 / 2)
    y1 = max(coord1[1] - size1 / 2, coord2[1] - size2 / 2)
    y2 = min(coord1[1] + size1 / 2, coord2[1] + size2 / 2)
    return x1 < x2 and y1 < y2

  # Ve lai ran
  def render(self):
    self.game_canvas.create_image(self.coords[0][0], self.coords[0][1], image=self.headImg)
    for coord in self.coords[1:]:
      self.game_canvas.create_image(coord[0], coord[1], image=self.bodyImg)


class Apple:
  def __init__(self, game_canvas):
    self.game_canvas = game_canvas
    self.appleImg = ImageTk.PhotoImage(Image.open("apple.png").resize((APPLE_SIZE, APPLE_SIZE)))
    self.generate_new()

  def generate_new(self):
    self.coord = (
      randint(0, WIDTH // APPLE_SIZE - 1) * APPLE_SIZE + APPLE_SIZE / 2,
      randint(0, HEIGHT // APPLE_SIZE - 1) * APPLE_SIZE + APPLE_SIZE / 2
    )

  def render(self):
    self.game_canvas.create_image(self.coord[0], self.coord[1], image=self.appleImg)

app = SnakeApp()
app.mainloop()