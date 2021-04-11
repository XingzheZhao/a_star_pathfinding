import pygame
import math
from queue import PriorityQueue

WIDTH = 1000
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Path Finding')

COLOR = {
    'RED' : (255, 0, 0),
    'GREEN' : (0, 255, 0),
    'BLUE' : (0, 255, 0),
    'YELLOW' : (255, 255, 0),
    'WHITE' : (255, 255, 255),
    'BLACK' : (0, 0, 0),
    'PURPLE' : (128, 0, 128),
    'ORANGE' : (255, 165, 0),
    'GREY' : (128, 128, 128),
    'TURQUOISE' : (64, 224, 208)
}

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = COLOR['WHITE']
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == COLOR['RED']

    def is_open(self):
        return self.color == COLOR['GREEN']

    def is_barrier(self):
        return self.color == COLOR['BLACK']

    def is_start(self):
        return self.color == COLOR['ORANGE']

    def is_end(self):
        return self.color == COLOR['TURQUOISE']

    def reset(self):
        self.color = COLOR['WHITE']

    def set_start(self):
        self.color = COLOR['ORANGE']
    def set_closed(self):
        self.color = COLOR['RED']

    def set_open(self):
        self.color = COLOR['GREEN']

    def set_barrier(self):
        self.color = COLOR['BLACK']

    def set_end(self):
        self.color = COLOR['TURQUOISE']

    def set_path(self):
        self.color = COLOR['PURPLE']

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

def get_heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2 - x1) + abs(y2 - y1)

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, COLOR['GREY'], (0, i * gap), (width, i * gap))
        pygame.draw.line(window, COLOR['GREY'], (i * gap, 0), (i * gap, width))

def display(window, grid, rows, width):
    # window.fill(COLOR['WHITE'])
    for row in grid:
        for node in row:
            node.draw(window)
    
    draw_grid(window, rows, width)
    pygame.display.update()

def get_clicked_position(position, rows, width):
    gap = width // rows
    y, x = position

    row = y // gap
    col = x // gap

    return row, col

def build_path(came_from, current, display):
    while current in came_from:
        current = came_from[current]
        current.set_path()
        display()


def pathfinding_algorithm(display, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from_node = {}
    g_cost = {node: float("inf") for row in grid for node in row}
    g_cost[start] = 0
    f_cost = {node: float("inf") for row in grid for node in row}
    f_cost[start] = get_heuristic(start.get_position(), end.get_position())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        # ! found the target
        if current == end:
            build_path(came_from_node, end, display)
            end.set_end()
            return True

        for neighbor in current.neighbors:
            temp_g_cost = g_cost[current] + 1
            if temp_g_cost < g_cost[neighbor]:
                came_from_node[neighbor] = current
                g_cost[neighbor] = temp_g_cost
                f_cost[neighbor] = temp_g_cost + get_heuristic(neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_cost[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_open()
        
        display()
        if current !=  start:
            current.set_closed()


def main(window, width):
    
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        display(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # left mouse
            if pygame.mouse.get_pressed()[0]:
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.set_start()
                elif not end and node != start:
                    end = node
                    end.set_end()
                elif node != start and node != end:
                    node.set_barrier()

            # right mouse
            elif pygame.mouse.get_pressed()[2]:
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    pathfinding_algorithm(lambda: display(window, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_g:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()

main(WINDOW, WIDTH)