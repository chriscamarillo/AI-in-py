from tkinter import *
from math import sqrt
from heapq import heapify, heappush, heappop 

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
GRID_ROWS = 40
GRID_COLS = 40
START_COLOR = 'purple'
GOAL_COLOR = 'red'
PATH_COLOR = 'lawn green'
DISCOVERED_COLOR = 'forest green'
BARRIER_COLOR = 'gray'
SPACE_COLOR = 'white'

# call this heuristic path algorithm

class App:
    # set up GUI
    def __init__(self, root):
        self.canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.bind('<B1-Motion>', self.toggle_barrier)
        self.canvas.bind('<Button-2>', self.move_start)
        self.canvas.bind('<Button-3>', self.move_goal)
        self.canvas.grid(row=0)
        self.root = root
        self.root.title('Heuristic Path Algorithm')

        self.mode = IntVar()
        self.mode.set(0)

        options = Frame(root)
        options.grid(row=1)
        
        button_frame = Frame(options)
        button_frame.grid(row=0)
        Button(button_frame, text='Search', command=self.search).grid(row=0)
        Button(button_frame, text='Clear', command=self.clear).grid(row=0, column=1)

        radio_frame = Frame(options)
        # w is used for the evaluation function f(n) = (2-w)g(n) + wh(n)
        for w, algo in enumerate(['Uniform', 'A*', 'Greedy']):
            Radiobutton(radio_frame, text=algo, variable=self.mode, value=w).grid(row=0, column=w+2)
        radio_frame.grid(row=0, column=1)

        
        self.generate_tiles()
        
        # set start tile to the top left of the screen
        self.tile_start = (1,)
        self.tile_goal = (GRID_ROWS * GRID_COLS,)
        
        self.canvas.itemconfig(self.tile_start, fill=START_COLOR)
        self.canvas.itemconfig(self.tile_goal, fill=GOAL_COLOR)

    # avoids overwriting start and goal positions        
    def toggle_barrier(self, event):
        tile_selected = event.widget.find_closest(event.x, event.y)
        current_color = self.canvas.itemcget(tile_selected, 'fill')
        
        if current_color == SPACE_COLOR or current_color == PATH_COLOR:
            current_color = BARRIER_COLOR

        self.canvas.itemconfig(tile_selected, fill=current_color)

    # avoids overwriting goal position only
    def move_start(self, event):
        tile_selected = event.widget.find_closest(event.x, event.y)
        pos_color = self.canvas.itemcget(tile_selected, 'fill')
        
        if pos_color != GOAL_COLOR:    
            self.canvas.itemconfig(self.tile_start, fill=SPACE_COLOR)
            self.tile_start = tile_selected 
            self.canvas.itemconfig(self.tile_start, fill=START_COLOR)
        
    # avoids overwriting start position only
    def move_goal(self, event):
        tile_selected = event.widget.find_closest(event.x, event.y)
        pos_color = self.canvas.itemcget(tile_selected, 'fill')
        
        if pos_color != START_COLOR:
            self.canvas.itemconfig(self.tile_goal, fill=SPACE_COLOR)
            self.tile_goal = tile_selected
            self.canvas.itemconfig(self.tile_goal, fill=GOAL_COLOR)


    def generate_tiles(self):
        w = self.canvas
        
        # recreate tiles
        w.delete(ALL)
        tile_w = CANVAS_WIDTH // GRID_COLS
        tile_h = CANVAS_HEIGHT // GRID_ROWS

        self.tiles = [w.create_rectangle(x, y, x + tile_w, y + tile_h, fill='white')
                      for y in range(0, tile_h * GRID_ROWS, tile_h)
                      for x in range(0, tile_w * GRID_COLS, tile_w)]

    def clear(self):
        for tile in self.tiles:
            self.canvas.itemconfig(tile, fill=SPACE_COLOR)
        self.canvas.itemconfig(self.tile_start, fill=START_COLOR)
        self.canvas.itemconfig(self.tile_goal, fill=GOAL_COLOR)

    def create_path(self, paths, current):
        path = [current]
        while current in paths.keys():
            current = paths[current]
            path.insert(0, current)
        return path

    def dist(self, tile_A, tile_B):
        A_row = (tile_A[0] - 1) // GRID_COLS
        A_col = (tile_A[0] - 1) % GRID_COLS

        B_row = (tile_B[0] - 1) // GRID_COLS
        B_col = (tile_B[0] - 1) % GRID_COLS

        dist_x = B_col - A_col
        dist_y = B_row - A_row
            
        return sqrt(dist_x*dist_x + dist_y*dist_y)

    def get_neighbors(self, n):
        n_row = (n[0] - 1) // GRID_COLS
        n_col = (n[0] - 1) % GRID_COLS
        
        possible = [(n_row + dr, n_col + dc) for dr in [0, 1, -1] for dc in [0, 1, -1]][1:] # exclude (0, 0)
        neighbors = list(filter(lambda p: 0 <= p[0] < GRID_ROWS and 0 <= p[1] < GRID_COLS, possible)) # make sure neighbors are inbounds
        neighbors = [(r * GRID_COLS + c + 1,) for r, c in neighbors] # the ordering of tile creation makes this possible
        neighbors = list(filter(lambda item: self.canvas.itemcget(item, 'fill') != BARRIER_COLOR, neighbors)) # no barriers counted
        return neighbors

    # debug basically halts the search early after N iterations (for inspection on neighbors and other stuff)
    # 0 will allow search to terminate once it finds the goal or runs out of new neighbors to check out
    def search(self, debug=0):
        mode = self.mode.get()
        root.title('Heuristic Path Algorithm: running - ' + ['Uniform', 'A*', 'Greedy'][mode] + ' search')
        paths = {}
        seen = []
        index = 0 
        closest_score = float('inf')
        iterations = 0

        # cost so far
        g_scores = {}
        
        # begin A*
        g_scores[self.tile_start] = 0

        # distance from a node/tile to a goal
        h = lambda n: self.dist(n, self.tile_goal)

        discover = [(h(self.tile_start), index, self.tile_start)]
        heapify(discover)


        while discover:
            f, dummy, current = heappop(discover) # dummy stops a comparing issue with tuples and heapq

            if not any(current == node for node in seen):
                seen.append(current)

                # current == goal
                if h(current) == 0 or debug > 0 and iterations >= debug:
                    print('DONEEE!')
                    final_path = self.create_path(paths, current)
                    print(final_path)
                    for step in final_path:
                        color = self.canvas.itemcget(step, 'fill')
                        if color == SPACE_COLOR or color == DISCOVERED_COLOR:
                            self.canvas.itemconfig(step, fill=PATH_COLOR)
                    return final_path
                        
                
                # get neighbors who are inbounds and aren't barriers
                neighbors = self.get_neighbors(current)
                
                # debug
                # print('run ', iterations, ' neighbors: ', len(neighbors))

                for n in neighbors:
                    # new g score is the current node's g score + distance to the neighbor
                    g_new = g_scores[current] + 1
                    
                    # add this new entry if the current path is better than any known ones
                    if n not in g_scores or g_new < g_scores[n]:
                        g_scores[n] = g_new

                        # THANKS Exercise 3.1
                        # f(n) = (2 - w)g(n) + wh(n).
                        f_score = (2 - mode) * g_scores[n] + mode * h(n)


                        if closest_score > f_score:
                            closest_score = f_score
                            print('closest so far F-Score: ', f_score, ' Closest Node: ', n)

                        # expand on this node when possible
                        if not any(n == entry[-1] in entry for entry in discover):
                            node_color = self.canvas.itemcget(n, 'fill')
                            if node_color == SPACE_COLOR:
                                self.canvas.itemconfig(n, fill=DISCOVERED_COLOR)
                            
                            index += 1
                            paths[n] = current
                            heappush(discover, (f_score, index, n))
            else:
                print('seen ', current)
            # no neighbors no expansion to avoid loops
            iterations += 1


        print('ehhh what?')
        return seen # create_path(paths, current)

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
