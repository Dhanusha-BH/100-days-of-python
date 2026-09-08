board = [" " for _ in range(9)]

win_combinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]

def display_board(board):
    print(board[0] + "|" + board[1] + "|" + board[2] )
    print("-" *5)
    print(board[3] + "|" + board[4] + "|" + board[5])
    print("-" *5)
    print(board[6] + "|" + board[7] + "|" + board[8])


display_board(board)


player1_symbol = input("Choose X or O:").upper()
if player1_symbol == "X":
    player2_symbol = "O"
else:
    player2_symbol = "X"

current_player = player1_symbol if player1_symbol == "X" else player2_symbol

game_over = False
while not game_over:
    position = int(input(f"{current_player}, choose a position (0-8): "))
    if board[position] == " ":
        board[position] = current_player
        display_board(board)

        for combo in win_combinations:
            a, b, c = combo
            if board[a] == board[b] == board[c] != " ":
                print(f"{board[a]} wins!")
                game_over = True

        if " " not in board:
            print("It's a tie!")
            game_over = True

        if not game_over:
            if current_player == "X":
                current_player = "O"
            else:
                current_player = "X"

    else:
        print("That position is taken, try again.")
