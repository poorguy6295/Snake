import tkinter as tk
from PIL import Image, ImageTk
from random import randint
import matplotlib, numpy, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# GAME CONSTANTS
WIDTH = 600
HEIGHT = 600
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
SNAKE_SIZE = 60
SNAKE_INIT_SPEED = 500 # Initial speed of snake
SNAKE_SPEED_DECREASE = 8 # The change of speed after eating an apple
SNAKE_INIT_DIRECTION = RIGHT
SNAKE_INIT_TAIL_COORD = (120, 300)
SNAKE_INIT_LENGTH = 3
APPLE_SIZE = 60
LEADER_BOARD_INIT = {
  "andy": 2,
  "vanh": 4
}


class SnakeApp(tk.Tk):

  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.cur_frame = None
    self.player_name = tk.StringVar()
    self.player_scores = LEADER_BOARD_INIT
    self.geometry(str(WIDTH) + "x" + str(HEIGHT))
    self.show_screen(MenuScreen)

  # Change to a new screen
  def show_screen(self, Screen):
    if self.cur_frame is not None:
      self.cur_frame.pack_forget()
    new_frame = Screen(self)
    new_frame.pack()
    self.cur_frame = new_frame

  # Save the score of player after game ends
  def save_score(self, score):
    player_name = self.player_name.get()
    self.player_scores[player_name] = max(self.player_scores.get(player_name, 0), score)


class MenuScreen(tk.Frame):
  def __init__(self, container):
    super().__init__(container)
    self.container = container
    
    game_title = tk.Label(self, text="Snake Game", font=("Helvetica", 30))
    game_title.pack(fill = tk.X, pady = 50)
    
    start_btn = tk.Button(self, text = "Start", command=lambda: container.show_screen(EnterNameScreen))
    start_btn.pack(fill = tk.X, pady = 10)

    leader_board_btn = tk.Button(self, text = "Show leaderboard", command=self.popup_leaderboard)
    leader_board_btn.pack(fill = tk.X, pady = 10)

  # Show the popup with leaderboard chart
  def popup_leaderboard(self):
    popup = tk.Toplevel()
    popup.wm_title("Leaderboard")

    sorted_player_score = [(k, v) for k, v in self.container.player_scores.items()]
    sorted_player_score.sort(key=lambda x: x[1], reverse = True)
    scores = [x[1] for x in sorted_player_score[:5]]
    players = [x[0] for x in sorted_player_score[:5]]

    f = Figure(figsize=(5, 4), dpi=100)
    ax = f.add_subplot()
    width = .5
    ax.bar(players, scores, width)
    ax.set_ylabel('Score')
    ax.set_xlabel("Player")

    canvas = FigureCanvasTkAgg(f, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP)

    back_btn = tk.Button(popup, text = "Back", command=popup.destroy)
    back_btn.pack(pady = 10)


class EnterNameScreen(tk.Frame):
  def __init__(self, container):
    super().__init__(container)

    name_label = tk.Label(self, text="Player name", font=("Helvetica", 10))
    name_label.pack(pady=(50, 5))

    name_input = tk.Entry(self, textvariable=container.player_name)
    name_input.pack()

    play_btn = tk.Button(self, text = "Play", command=lambda: container.show_screen(GameScreen))
    play_btn.pack(pady=10)


class GameScreen(tk.Canvas):
  def __init__(self, container):
    super().__init__(container)
    self.container = container
    self.configure(width=WIDTH, height=HEIGHT, bg="white")
    self.quit_btn = tk.Button(self, text="Quit", command=self.game_over)
    self.create_window(WIDTH - 10, 10, anchor="ne", window=self.quit_btn)
    self.snake = Snake(self)
    self.apple = Apple(self)
    self.score = 0
    self.bind_all("<Key>", self.onKeyPress)
    self.game_running = True
    self.update()

  # Handle the key press event from user (left, up, down, right)
  def onKeyPress(self, event):
    key = event.keysym
    for direction in DIRECTION.keys():
      if key == direction:
        self.snake.update_direction(direction)

  # Update the state of game and redraw whole game board
  def update(self):
    if self.game_running:
      # Tinh toan buoc di
      self.snake.move()

      # Ve lai game
      self.delete("removable")
      self.snake.render()
      self.apple.render()

      self.create_text(10, 10, fill="green", font=("Helvetica", 15), text=self.container.player_name.get(), anchor="nw", tag="removable")
      self.create_text(10, 40, fill="red", font=("Helvetica", 20), text=str(self.score), anchor="nw", tag="removable")
      
      self.after(self.snake.speed, self.update)

  # When snake eats an apple, generate a new apple, change snake's speed and increase score
  def snake_eat_apple(self):
    self.apple.generate_new()
    self.snake.speed -= SNAKE_SPEED_DECREASE
    self.score += 1

  # When the game end, snake hits its tail or nomore space left
  def game_over(self):
    self.game_running = False
    self.container.save_score(self.score)
    self.container.show_screen(MenuScreen)


class Snake:
  def __init__(self, game_canvas):
    self.game_canvas = game_canvas
    self.headImg = ImageTk.PhotoImage(Image.open("head.png").resize((SNAKE_SIZE, SNAKE_SIZE)))
    self.bodyImg = ImageTk.PhotoImage(Image.open("body.png").resize((SNAKE_SIZE, SNAKE_SIZE)))
    self.direction = SNAKE_INIT_DIRECTION
    self.speed = SNAKE_INIT_SPEED

    # Calculate initial coordinates of snake
    self.coords = [SNAKE_INIT_TAIL_COORD]
    for index in range(1, SNAKE_INIT_LENGTH):
      self.coords = [self.next_coord(self.coords[0], self.direction)] + self.coords

  # Move snake
  def move(self):
    new_head = self.next_coord(self.coords[0], self.direction)

    # Check whether snake eats an apple
    if self.check_overlap(new_head, SNAKE_SIZE, self.game_canvas.apple.coord, APPLE_SIZE):
      self.game_canvas.snake_eat_apple()
      self.coords = [new_head] + self.coords
    else:
      self.coords = [new_head] + self.coords[:-1]

    # Check whether snake hits its tail
    for body_coord in self.coords[1:]:
      if self.check_overlap(new_head, SNAKE_SIZE, body_coord, SNAKE_SIZE):
        self.game_canvas.game_over()

    # Check whether there is no space left
    if (WIDTH // SNAKE_SIZE) * (HEIGHT // SNAKE_SIZE) - 1 == len(self.coords):
      self.game_canvas.game_over()

  # The next coordinate of snake's head
  def next_coord(self, coord, direction):
    return (
      (coord[0] + DIRECTION[direction][0] * SNAKE_SIZE) % WIDTH,
      (coord[1] + DIRECTION[direction][1] * SNAKE_SIZE) % HEIGHT
    )

  # Update the moving direction of snake
  def update_direction(self, direction):
    new_head = self.next_coord(self.coords[0], direction)
    if not self.check_overlap(new_head, SNAKE_SIZE, self.coords[1], SNAKE_SIZE):
      self.direction = direction

  # Check whether 2 blocks intersect
  def check_overlap(self, coord1, size1, coord2, size2):
    x1 = max(coord1[0], coord2[0])
    x2 = min(coord1[0] + size1, coord2[0] + size2)
    y1 = max(coord1[1], coord2[1])
    y2 = min(coord1[1] + size1, coord2[1] + size2)
    return x1 < x2 and y1 < y2

  # Redraw the snake
  def render(self):
    self.game_canvas.create_image(self.coords[0][0], self.coords[0][1], image=self.headImg, anchor="nw", tag="removable")
    for coord in self.coords[1:]:
      self.game_canvas.create_image(coord[0], coord[1], image=self.bodyImg, anchor="nw", tag="removable")


class Apple:
  def __init__(self, game_canvas):
    self.game_canvas = game_canvas
    self.appleImg = ImageTk.PhotoImage(Image.open("apple.png").resize((APPLE_SIZE, APPLE_SIZE)))
    self.generate_new()

  # Calculate a new coordinate of apple
  def generate_new(self):
    leftover_space = (WIDTH // APPLE_SIZE * HEIGHT // APPLE_SIZE) - len(self.game_canvas.snake.coords)
    next_apple_index = randint(1, leftover_space)
    coord_used = False

    for x in range(0, WIDTH, APPLE_SIZE):
      for y in range(0, HEIGHT, APPLE_SIZE):
        coord_used = False
        for snake_coord in self.game_canvas.snake.coords:
          if self.game_canvas.snake.check_overlap((x, y), APPLE_SIZE, snake_coord, SNAKE_SIZE):
            coord_used = True
            break
        if not coord_used:
          next_apple_index -= 1
        if next_apple_index == 0:
          self.coord = (x, y)
          return

  # Redraw the apple
  def render(self):
    self.game_canvas.create_image(self.coord[0], self.coord[1], image=self.appleImg, anchor="nw", tag="removable")

app = SnakeApp()
app.mainloop()