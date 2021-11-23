from random import randint
import time

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, dot_bow_ship, ship_length, ship_direction):
        self.dot_bow_ship = dot_bow_ship
        self.ship_length = ship_length
        self.ship_direction = ship_direction
        self.lives = ship_length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.ship_length):
            cur_x = self.dot_bow_ship.x
            cur_y = self.dot_bow_ship.y

            if self.ship_direction == 0:
                cur_x += i
            elif self.ship_direction == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooted(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count_shooted_ships = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy_dots_on_board = []
        self.ships_on_board = []

    def __str__(self):
        res = '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, j in enumerate(self.field):
            res += f"\n{i + 1} | {' | '.join(j)} |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy_dots_on_board:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy_dots_on_board.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy_dots_on_board:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy_dots_on_board.append(d)
        self.ships_on_board.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy_dots_on_board:
            raise BoardUsedException()

        self.busy_dots_on_board.append(d)

        for ship in self.ships_on_board:
            if ship.shooted(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count_shooted_ships += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy_dots_on_board = []

    def defeat(self):
        return self.count_shooted_ships == len(self.ships_on_board)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        time.sleep(3)
        while True:
            d = Dot(randint(0, 5), randint(0, 5))
            if d not in self.enemy.busy_dots_on_board:
                print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
                return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты(через пробел)! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        player_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hid = False

        self.ai = AI(comp_board, player_board)
        self.us = User(player_board, comp_board)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in sorted(self.lens):
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("  Приветствуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" Формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 57)
        print("  Доска пользователя:", "Доска компьютера:", sep="          ")
        a = self.us.board.__str__()
        b = self.ai.board.__str__()
        for i, j in zip(a.split("\n"), b.split("\n")):
            print(i, j, sep="   ")
        print("-" * 57)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
