import os
import sys
import pygame
import copy
import random


def terminate():
    pygame.quit()
    sys.exit()

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image

def start_screen():
    intro_text = ["COLOR LINES","",
                  'Классическая игра', "",
                  "Активный шарик отмечен", "серой точкой в его центре"]
    screen_first = pygame.display.set_mode((380, 400))
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(load_image('color_pencils.jpg'), (380, 400))
    screen_first.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen_first.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(50)


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 20
        self.top = 20
        self.cell_size = 30

        # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # диспетчер, который получает событие нажатия и вызывает другие методы
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    # возврат координат клетки в виде кортежа
    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if 0 <= cell_x <= self.width and 0 <= cell_y <= self.height:
            return cell_x, cell_y
        else:
            return None

    def on_click(self, cell_coords):
        pass


class Lines(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.red = False  # наличие активного шарика
        self.go = False  # флаг влючает перемещение шарика
        self.red_coords = (-1, -1)  # координаты активного шарика
        self.ticks = 0
        self.path = []
        # self.now_point = None
        self.new_balls()
        self.current_color = 0
        self.score = 0
        self.ch_score = self.get_ch_score()

    # Возвращается путь для активного шарика в заданную ячейку или None
    def return_path(self, x1, y1, x2, y2):
        # формируем матрицу для обработки волновым алгоритмом (отрицательные числа - несвободные ячейки, 1 - старт)
        lab = copy.deepcopy(self.board)
        for i in range(self.height):
            for j in range(self.width):
                if lab[i][j] != 0:
                    lab[i][j] = 1

        print("*", *lab)
        to_wave_board(x1, y1, lab)
        print('-', *lab)
        print(lab[y2][x2], y2, x2)
        if lab[y2][x2] > 0:
            # Из матрицы, которую вернул волновой алгоритм, собираем путь шарика
            self.path = way(x1, y1, x2, y2, lab)
            self.current_color = abs(self.board[y1][x1])
            self.red = False
            print('w', self.path)
            return self.path[1:]
        else:
            return None

    def new_balls(self):
        # формируем список пустых ячеек
        free_cells = list()
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 0:
                    free_cells.append((i, j))
        random.shuffle(free_cells)
        # рандомно выбираем три ячейки и цвета для новых шариков
        count = 3
        while count and len(free_cells) > 0:
            new_cell = free_cells.pop()
            new_color = random.randint(2, 5)
            self.board[new_cell[0]][new_cell[1]] = new_color
            count -= 1
    def get_ch_score(self):
        fullname = os.path.join('data', 'score.txt')
        with open(fullname) as fin:
            lst = fin.readlines()
        ch_score = max([int(x) for x in lst])
        return ch_score

    def save_score(self):
        fullname = os.path.join('data', 'score.txt')
        with open(fullname, "a") as fout:
            fout.write(str(self.score) + '\n')

    def chek_lines(self):
        h = self.height
        w = self.width
        flag = False
        # горизонтали
        for i in range(h):
            c, mc = 1, 1
            end = 0
            for j in range(w - 1):
                if self.board[i][j] == self.board[i][j + 1] != 0:
                    c += 1
                    end = j + 1
                    mc = max(mc, c)
                    if c >= 5:
                        flag = True
                else:
                    c = 1
            if flag:
                self.win(mc)
                for j in range(end, end - mc, -1):
                    self.board[i][j] = 0
                flag = False
        # вертикали
        for j in range(w):
            c, mc = 1, 1
            end = 0
            for i in range(h - 1):
                if self.board[i][j] == self.board[i + 1][j] != 0:
                    c += 1
                    end = i + 1
                    mc = max(mc, c)
                    if c >= 5:
                        flag = True
                else:
                    c = 1
            if flag:
                self.win(mc)
                for i in range(end, end - mc, -1):
                    self.board[i][j] = 0
                flag = False
        # главная диагональ
        flag = False
        for k in range(-4, 5):
            c, mc = 1, 1
            end = 0
            for i in range(h - abs(k) - 1):
                if self.board[i - k][i] == self.board[i - k + 1][i + 1] != 0:
                    c += 1
                    end = i + 1
                    mc = max(mc, c)
                    if c >= 5:
                        flag = True
                else:
                    c = 1
            if flag:
                self.win(mc)
                for i in range(end, end - mc, -1):
                    self.board[i - k][i] = 0
                flag = False
        # побочная диагональ
        flag = False
        for k in range(3, 8):
            c, mc = 1, 1
            end = 0
            for i in range(k + 1):

                if self.board[k - i][i] == self.board[k - i - 1][i + 1] != 0:
                    c += 1
                    end = i + 1
                    mc = max(mc, c)
                    if c >= 5:
                        flag = True
                else:
                    c = 1
            if flag:
                self.win(mc)
                for i in range(end, end - mc, -1):
                    self.board[k - i][i] = 0
                flag = False
        # продолжение побочной диагонали
        for k in range(1, 5):
            c, mc = 1, 1
            end = 0
            for i in range(8, k - 1, -1):
                try:
                    if self.board[i][8 + k - i] == self.board[i - 1][8 + k - i + 1] != 0:
                        c += 1
                        end = 8 + k - i + 1
                        mc = max(mc, c)
                        if c >= 5:
                            flag = True
                    else:
                        c = 1
                except Exception:
                    pass
            if flag:
                self.win(mc)
                for i in range(end, end - mc, -1):
                    self.board[8 + k - i][i] = 0
                flag = False

    def win(self, mc):
        self.score += mc * 10
        print(self.score)
    # изменение поля (опираясь на координаты клетки)
    def on_click(self, cell_coords):
        try:
            #if cell_coords:
            cell_x, cell_y = cell_coords
            # если нет активного шарика и в ячейке хранится 0, то в ячейке нет шарика, не реагируем на клик
            if not self.red and self.board[cell_y][cell_x] == 0:
                # print('клик по пустой ячейке', cell_coords)
                #print(self.board)
                pass
            # если шарик в ячейке есть и никакой не был активным, делаем текущий активным
            elif not self.red and self.board[cell_y][cell_x] != 0:
                self.board[cell_y][cell_x] *= -1
                self.red = True
                self.red_coords = cell_coords
                # print('стала активнной ячейка', cell_coords,  self.board[cell_y][cell_x])
                print(self.board)
            # если кликнули по активному шарику, снимаем с него активность
            elif self.red and cell_coords == self.red_coords:
                self.board[cell_y][cell_x] *= -1
                self.red = False
                self.red_coords = (-1, -1)
                # print('перестала быть активной ячейка', cell_coords, self.board[cell_y][cell_x])
                print(self.board)
            elif self.red and self.board[cell_y][cell_x] == 0:
                # то есть щёлкнули по пустой ячейке и надо переместить активный шарик
                self.path = self.return_path(self.red_coords[0], self.red_coords[1],
                                        cell_coords[0], cell_coords[1])
                if len(self.path) > 0:
                    self.go = True
                    #self.board[cell_coords[1]][cell_coords[0]] = self.current_color
                    self.board[self.red_coords[1]][self.red_coords[0]] = 0
                    self.red = False
                    self.red_coords = (-1, -1)
                print(self.board)
            # если есть активный шарик, а кликнули по другому шарику, активность присваивается новому шарику
            elif self.red and self.board[cell_y][cell_x] != 0:
                self.board[self.red_coords[1]][self.red_coords[0]] *= -1
                # print(self.board[self.red_coords[0]][self.red_coords[1]], 'перестала быть активной', )
                self.board[cell_y][cell_x] *= -1
                # print(self.board[cell_y][cell_x],'стала активной')
                self.red_coords = cell_coords
                print(self.board)
        except Exception as e:
            print(e, self.red, self.red_coords)

    def update(self):
        try:
            if self.ticks == 20:
                # print(self.board)
                if self.go and len(self.path) > 0:
                    # print(self.path)
                    x, y = self.path.pop(0)
                    self.board[y][x] = self.current_color
                    self.board[self.red_coords[1]][self.red_coords[0]] = 0
                    self.red_coords = x, y
                    if len(self.path) == 0:
                        #self.board[y][x] = self.current_color
                        self.red_coords = (-1, -1)
                        # print("можно продолжать")
                        self.chek_lines()
                        self.new_balls()
                        self.chek_lines()
                        self.go = False

                self.ticks = 0
            self.ticks += 1
        except Exception as e:
            print('ошибка', e)
    def render(self, screen):
        colors = {0: 'gray', 1: 'white', 2: 'blue', 3: 'orange',
                  4: 'yellow', 5: 'green', 6: 'violet', 7: 'indigo', 8: 'red'}
        try:
            for y in range(self.height):
                for x in range(self.width):
                    pygame.draw.rect(screen, pygame.Color(255, 255, 255), (
                        x * self.cell_size + self.left, y * self.cell_size + self.top,
                        self.cell_size, self.cell_size), 1)
                    if self.board[y][x] != 0:
                        pygame.draw.circle(screen, colors[abs(self.board[y][x])], (
                            x * self.cell_size + self.left + self.cell_size // 2,
                            y * self.cell_size + self.top + self.cell_size // 2), self.cell_size // 2 - 2)
                    if self.board[y][x] < 0:
                        pygame.draw.circle(screen, colors[0], (
                            x * self.cell_size + self.left + self.cell_size // 2,
                            y * self.cell_size + self.top + self.cell_size // 2), 5)
            line = f"Игрок: {self.score}   Чемпион:{self.ch_score}"
            font = pygame.font.Font(None, 30)
            string_rendered = font.render(line, 1, pygame.Color('white'))
            screen.blit(string_rendered, (5, 5) )

        except Exception as e:
            print('ошибка', e)


def to_wave_board(x, y, lab):
    sp = [(x, y)]
    cur = 0
    lab[y][x] = 0
    while len(sp) > 0:
        cur += 1
        sp1 = []
        for el in sp:
            point = lab[el[1]][el[0]]
            if point == 0:
                lab[el[1]][el[0]] = cur
            try:
                if lab[el[1] + 1][el[0]] == 0:
                    sp1.append((el[0], el[1] + 1))
            except Exception:
                pass
            try:
                if el[1] - 1 > -1 and lab[el[1] - 1][el[0]] == 0:
                    sp1.append((el[0], el[1] - 1))
            except Exception:
                pass
            try:
                if lab[el[1]][el[0] + 1] == 0:
                    sp1.append((el[0] + 1, el[1]))
            except Exception:
                pass
            try:
                if el[0] - 1 > -1 and lab[el[1]][el[0] - 1] == 0:
                    sp1.append((el[0] - 1, el[1]))
            except Exception:
                pass
        sp = list(set(sp1))
    return lab


def way(x1, y1, x2, y2, lab):
    try:
        path = [(x2, y2)]
        next_elem = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while x1 != x2 or y1 != y2:
            for elem in next_elem:
                try:
                    next_point = lab[y2 + elem[0]][x2 + elem[1]]
                    if next_point == lab[y2][x2] - 1:
                        x2 += elem[1]
                        y2 += elem[0]
                        path.append((x2, y2))
                except Exception:
                    pass
        return path[:: -1]
    except Exception as e:
        print(e)

def main():
    random.seed()
    # random.choice()
    # random.shuffle()
    pygame.init()
    size = 380, 400
    #screen_first = pygame.display.set_mode((500, 500))
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('COLOR LINES')
    clock = pygame.time.Clock()

    # поле 9 на 9
    board = Lines(9, 9)
    board.set_view(10, 30, 40)

    start_screen()

    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    board.save_score()
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board.get_click(event.pos)

            screen.fill((0, 0, 0))
            board.render(screen)
            board.update()
            pygame.display.flip()
            clock.tick(50)
    except Exception as e:
        print('running ошибка', e)
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
