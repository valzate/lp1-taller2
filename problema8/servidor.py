import socket
import threading

HOST = "localhost"
PORT = 7000
BUFFER = 1024

lock = threading.Lock()

waiting_players = []
spectators = []
game = None


class Game:
    def __init__(self, player_x, player_o):
        self.board = [[" "]*3 for _ in range(3)]
        self.players = {"X": player_x, "O": player_o}
        self.current_turn = "X"
        self.finished = False

    def board_string(self):
        rows = [" | ".join(row) for row in self.board]
        return "\n---------\n".join(rows)

    def validate_move(self, row, col):
        return 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == " "

    def make_move(self, row, col):
        if not self.validate_move(row, col):
            return False

        self.board[row][col] = self.current_turn
        return True

    def check_winner(self):
        lines = []

        # Filas y columnas
        lines.extend(self.board)
        lines.extend([[self.board[r][c] for r in range(3)] for c in range(3)])

        # Diagonales
        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2-i] for i in range(3)])

        for line in lines:
            if line[0] != " " and line.count(line[0]) == 3:
                return line[0]

        return None

    def is_draw(self):
        return all(cell != " " for row in self.board for cell in row)


def broadcast(message):
    for player in game.players.values():
        player.send(message.encode())
    for spec in spectators:
        spec.send(message.encode())


def handle_client(conn):
    global game

    conn.send(b"Tipo (PLAY / WATCH): ")
    role = conn.recv(BUFFER).decode().strip().upper()

    if role == "WATCH":
        with lock:
            spectators.append(conn)
        conn.send(b"Modo espectador activado.\n")
        return

    elif role == "PLAY":
        with lock:
            waiting_players.append(conn)

            if len(waiting_players) >= 2:
                p1 = waiting_players.pop(0)
                p2 = waiting_players.pop(0)
                game = Game(p1, p2)

                p1.send(b"Eres X\n")
                p2.send(b"Eres O\n")

                broadcast("Partida iniciada!\n")
                broadcast(game.board_string() + "\n")

    else:
        conn.close()
        return

    while not game.finished:
        try:
            conn.send(f"Turno de {game.current_turn}\n".encode())
            move = conn.recv(BUFFER).decode().strip()

            if conn != game.players[game.current_turn]:
                conn.send(b"No es tu turno\n")
                continue

            row, col = map(int, move.split())

            with lock:
                if not game.make_move(row, col):
                    conn.send(b"Movimiento invalido\n")
                    continue

                winner = game.check_winner()
                draw = game.is_draw()

                broadcast(game.board_string() + "\n")

                if winner:
                    broadcast(f"Gana {winner}!\n")
                    game.finished = True
                elif draw:
                    broadcast("Empate!\n")
                    game.finished = True
                else:
                    game.current_turn = "O" if game.current_turn == "X" else "X"

        except:
            break

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Servidor Tic-Tac-Toe iniciado...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()


if __name__ == "__main__":
    start_server()
