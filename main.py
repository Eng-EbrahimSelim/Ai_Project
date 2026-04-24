import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import heapq
import random
from collections import deque

SIZE = 3
GOAL = tuple(range(1, SIZE*SIZE)) + (0,)

# ================= A* =================
def manhattan(state):
    dist = 0
    for i, val in enumerate(state):
        if val == 0:
            continue
        gi = GOAL.index(val)
        x1, y1 = divmod(i, SIZE)
        x2, y2 = divmod(gi, SIZE)
        dist += abs(x1-x2) + abs(y1-y2)
    return dist


def neighbors(state):
    res = []
    z = state.index(0)
    x, y = divmod(z, SIZE)

    dirs = {"U":(x-1,y),"D":(x+1,y),"L":(x,y-1),"R":(x,y+1)}

    for m,(nx,ny) in dirs.items():
        if 0<=nx<SIZE and 0<=ny<SIZE:
            ni = nx*SIZE+ny
            lst = list(state)
            lst[z], lst[ni] = lst[ni], lst[z]
            res.append((tuple(lst), m))
    return res


def a_star(start):
    pq = []
    heapq.heappush(pq,(manhattan(start),0,start,[]))
    best = {start: 0}

    while pq:
        f,g,cur,path = heapq.heappop(pq)

        if cur == GOAL:
            return path

        if g > best.get(cur, float("inf")):
            continue

        for nxt,move in neighbors(cur):
            ng = g + 1
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                heapq.heappush(pq,(ng + manhattan(nxt), ng, nxt, path+[move]))
    return []


# ================= BFS =================
def bfs(start):
    q = deque([(start, [])])
    visited = set([start])

    while q:
        cur, path = q.popleft()

        if cur == GOAL:
            return path

        for nxt, move in neighbors(cur):
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [move]))
    return []


# ================= DFS =================
def dfs(start, limit=50):
    stack = [(start, [], 0)]
    visited = set()

    while stack:
        cur, path, depth = stack.pop()

        if cur == GOAL:
            return path

        if depth > limit:
            continue

        if cur in visited:
            continue

        visited.add(cur)

        for nxt, move in neighbors(cur):
            stack.append((nxt, path + [move], depth + 1))

    return []


# ================= SHUFFLE =================
def shuffle(state, steps=50):
    state = list(state)
    for _ in range(steps):
        state = list(random.choice(neighbors(tuple(state)))[0])
    return tuple(state)


# ================= APP =================
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("N-Puzzle AI (A* - BFS - DFS)")
        self.root.geometry("1000x650")

        self.mode = "number"
        self.state = shuffle(GOAL)
        self.solution = []
        self.step = 0

        self.sidebar = tk.Frame(self.root, bg="#222", width=220)
        self.sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(self.root)
        self.main.pack(side="right", fill="both", expand=True)

        tk.Label(self.sidebar, text="Modes", fg="white", bg="#222", font=("Arial",14)).pack(pady=10)

        tk.Button(self.sidebar, text="Number Puzzle", command=lambda:self.set_mode("number"), bg="#444", fg="white").pack(pady=5)
        tk.Button(self.sidebar, text="Image Puzzle", command=lambda:self.set_mode("image"), bg="#444", fg="white").pack(pady=5)
        tk.Button(self.sidebar, text="Upload Image", command=self.load_image, bg="#555", fg="white").pack(pady=10)

        # Algorithm selector
        self.algorithm = tk.StringVar(value="A*")
        tk.Label(self.sidebar, text="Algorithm", fg="white", bg="#222").pack(pady=10)
        tk.OptionMenu(self.sidebar, self.algorithm, "A*", "BFS", "DFS").pack()

        tk.Button(self.sidebar, text="Shuffle", command=self.do_shuffle, bg="#444", fg="white").pack(pady=5)
        tk.Button(self.sidebar, text="Solve", command=self.solve, bg="#444", fg="white").pack(pady=5)
        tk.Button(self.sidebar, text="Next Step", command=self.next_step, bg="#444", fg="white").pack(pady=5)
        tk.Button(self.sidebar, text="Auto", command=self.auto, bg="#444", fg="white").pack(pady=5)

        self.steps_label = tk.Label(self.sidebar, text="Steps: 0", fg="white", bg="#222")
        self.steps_label.pack(pady=10)

        self.canvas = tk.Canvas(self.main, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.tiles = []
        self.tk_tiles = []

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw()
        self.root.mainloop()

    # ================= MODE =================
    def set_mode(self, mode):
        self.mode = mode
        self.draw()

    # ================= IMAGE =================
    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.original_img = Image.open(path)
        self.prepare_tiles()

    def prepare_tiles(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        size = min(w, h)

        img = self.original_img.resize((size, size))

        tw = size // SIZE
        th = size // SIZE

        self.tiles = []
        for i in range(SIZE):
            for j in range(SIZE):
                tile = img.crop((j*tw, i*th, (j+1)*tw, (i+1)*th))
                self.tiles.append(tile)

        self.tk_tiles = [ImageTk.PhotoImage(t) for t in self.tiles]

    # ================= DRAW =================
    def draw(self):
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h)
        tile = size // SIZE

        ox = (w - size) // 2
        oy = (h - size) // 2

        for i in range(SIZE):
            for j in range(SIZE):
                val = self.state[i*SIZE+j]
                x = ox + j*tile
                y = oy + i*tile

                if self.mode == "image" and self.tk_tiles:
                    img_index = val-1 if val != 0 else len(self.tk_tiles)-1
                    self.canvas.create_image(x, y, anchor="nw", image=self.tk_tiles[img_index])

                else:
                    color = "gray" if val == 0 else "lightblue"
                    self.canvas.create_rectangle(x,y,x+tile,y+tile, fill=color)
                    if val != 0:
                        self.canvas.create_text(x+tile//2,y+tile//2, text=str(val), font=("Arial", tile//4))

                self.canvas.create_rectangle(x,y,x+tile,y+tile, outline="white")

    # ================= APPLY MOVE =================
    def apply(self, move):
        z = self.state.index(0)
        x,y = divmod(z,SIZE)

        moves = {"U":(x-1,y),"D":(x+1,y),"L":(x,y-1),"R":(x,y+1)}
        nx,ny = moves[move]
        ni = nx*SIZE+ny

        lst = list(self.state)
        lst[z], lst[ni] = lst[ni], lst[z]
        self.state = tuple(lst)

    # ================= SOLVE =================
    def solve(self):
        algo = self.algorithm.get()

        if algo == "A*":
            self.solution = a_star(self.state)
        elif algo == "BFS":
            self.solution = bfs(self.state)
        elif algo == "DFS":
            self.solution = dfs(self.state)

        self.step = 0
        self.steps_label.config(text=f"Steps: {len(self.solution)}")

    # ================= STEPS =================
    def next_step(self):
        if self.step < len(self.solution):
            self.apply(self.solution[self.step])
            self.step += 1
            self.draw()

    def auto(self):
        if self.step < len(self.solution):
            self.next_step()
            self.root.after(250, self.auto)

    # ================= SHUFFLE =================
    def do_shuffle(self):
        self.state = shuffle(GOAL)
        self.draw()

    # ================= RESIZE =================
    def on_resize(self, event):
        if self.mode == "image" and hasattr(self, "original_img"):
            self.prepare_tiles()
        self.draw()

    # ================= CLICK =================
    def on_click(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h)
        tile = size // SIZE

        ox = (w - size) // 2
        oy = (h - size) // 2

        col = (event.x - ox) // tile
        row = (event.y - oy) // tile

        if not (0 <= row < SIZE and 0 <= col < SIZE):
            return

        idx = row * SIZE + col
        z = self.state.index(0)

        zx, zy = divmod(z, SIZE)

        if abs(zx - row) + abs(zy - col) == 1:
            lst = list(self.state)
            lst[z], lst[idx] = lst[idx], lst[z]
            self.state = tuple(lst)
            self.draw()


# RUN
App()