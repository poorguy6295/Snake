import tkinter as tk

# GAME CONSTANTS
WIDTH = 400
HEIGHT = 400
BG_COLOR = "black"

class SnakeApp(tk.Tk):
  
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.cur_frame = None
    self.geometry(str(WIDTH) + "x" + str(HEIGHT))
    self.show_frame(MenuScreen)

  def show_frame(self, Screen):
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
    
    start_btn = tk.Button(self, text = "Start", command=lambda: container.show_frame(EnterNameScreen))
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

    play_btn = tk.Button(self, text = "Play", command=lambda: container.show_frame(GameScreen))
    play_btn.pack(pady=10)


class GameScreen(tk.Canvas):

  def __init__(self, container):
    super().__init__(container)
    self.configure(width=WIDTH, height=HEIGHT, bg=BG_COLOR)
  
  def start(self):
    self.snake = Snake(self)


class Snake:

  def __init__(self, game_controller):
    self.game_controller = game_controller



app = SnakeApp()
app.mainloop()