#!/usr/bin/python3

#Function code to clear the output space (screen)

from IPython.display import clear_output
import sys

#code to display just board-

def ttt_borad(board):
  cl = clear_output()
  print('Your Tic-Tac-Toe board now:\n')
  print(board[1] + "|" + board[2] + "|" + board[3])
  print("________")
  print(board[4] + "|" + board[5] + "|" + board[6])
  print("________")
  print(board[7] + "|" + board[8] + "|" + board[9])

def enter_key(key, bp, square):
  play1 = key
  ind = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
  #i = 1
  j = square
  print (j)
  #x = ind.index(j)
  #print(f"X is : {x}")
  #ind.pop(x)
  j = int(j)
  bp[j] = play1
  print (bp)
  ttt_borad(bp)

clear_output()
global entry
entry = ['M', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ttt_borad(entry)

global symbol
symbol = "Z"
square = "7"

#enter_key(symbol, entry, square)

# Python 3 program of the above approach
ROW = 3
COL = 3

# (-1, 0), (0, 1), (1, 0), (0, -1) in the up, left, down and right order.

# Initialize direction vectors
dRow = [0, 1, 0, -1]
dCol = [-1, 0, 1, 0]
vis = [[False for i in range(3)] for j in range(3)]

# Function to check if mat[row][col]
# is unvisited and lies within the
# boundary of the given matrix
def isValid(row, col):
    global ROW
    global COL
    global vis

    # If cell is out of bounds
    if (row < 0 or col < 0 or row >= ROW or col >= COL):
        return False

    # If the cell is already visited
    if (vis[row][col]):
        return False

    # Otherwise, it can be visited
    return True

# Function to perform DFS
# Traversal on the matrix grid[]
def DFS(row, col, grid):
    global dRow
    global dCol
    global vis

    # Initialize a stack of pairs and
    # push the starting cell into it
    st = []
    st.append([row, col])

    # Iterate until the
    # stack is not empty
    while (len(st) > 0):
        # Pop the top pair
        curr = st[len(st) - 1]
        st.remove(st[len(st) - 1])
        row = curr[0]
        col = curr[1]

        # Check if the current popped
        # cell is a valid cell or not
        if (isValid(row, col) == False):
            continue

        # Mark the current
        # cell as visited
        vis[row][col] = True

        # Print the element at
        # the current top cell
        print(grid[row][col], end = " ")
        enter_key(symbol, entry, grid[row][col])

        # Push all the adjacent cells
        for i in range(4):
            adjx = row + dRow[i]
            adjy = col + dCol[i]
            st.append([adjx, adjy])

# Driver Code
if __name__ == '__main__':
    grid =  [[1, 2, 3],
             [4, 5, 6],
             [7, 8, 9]]

    # Function call
    DFS(0, 0, grid)
