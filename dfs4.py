#!/usr/bin/python3

import sys

global symbol
symbol = "Z"
global entry
entry = ['M', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def countIslands(matrix):
    #rows = len(matrix)
    #cols = len(matrix[0])
    # X is columns
    # Y is rows
    COLS = len(matrix[0]) # X
    ROWS = len(matrix) # Y
    print (COLS)
    print (ROWS)
    totalIslands = 0

    for c in range(COLS):
        for r in range(ROWS):
            print (c)
            print (r)
            input ("Cordinates")
            if (matrix[r][c] == 1):  # only if the cell is a land
                print ("Found Land!")
                # we have found an island
                totalIslands += 1
                visit_is_land_DFS(matrix, r, c)
    return totalIslands

def visit_is_land_DFS(matrix,  y,  x):
    #enter_key(symbol, matrix, matrix[x][y])
    print ("---- visit island")
    ###############if (matrix[y][x] == 1):
    print ("X is %d" % x)
    print ("Y is %d" % y)
    input ("press space")
    print ("----")
    if (y < 0 or y >= len(matrix) or x < 0 or x >= len(matrix[0])):
        print ("outside boundary")
        return  # return, if it is not a valid cell
    if (matrix[y][x] == 1):
        print ("Found another 1!")
    if (matrix[y][x] == 0):
        return  # return, if it is a water cell

    matrix[y][x] = 0  # mark the cell visited by making it a water cell

    # recursively visit all neighboring cells (horizontally & vertically)
    # row is x, column is y
    #print ("lower cell")
    #visit_is_land_DFS(matrix, x + 1, y)  # lower cell
    visit_is_land_DFS(matrix, y, x + 1)  # lower cell
    #print ("upper cell")
    #visit_is_land_DFS(matrix, x - 1, y)  # upper cell
    visit_is_land_DFS(matrix, y, x - 1)  # upper cell
    #print ("right cell")
    #visit_is_land_DFS(matrix, x, y + 1)  # right cell
    visit_is_land_DFS(matrix, y + 1, x)  # right cell
    #print ("left cell")
    #visit_is_land_DFS(matrix, x, y - 1)  # left cell
    visit_is_land_DFS(matrix, y - 1, x)  # left cell
    # Add here for diagonals
    #print ("lower left cell")
    #visit_is_land_DFS(matrix, x + 1, y - 1 )  # lower left cell
    visit_is_land_DFS(matrix, y - 1, x + 1 )  # lower left cell
    #print ("upper left cell")
    #visit_is_land_DFS(matrix, x - 1, y - 1 )  # upper left cell
    visit_is_land_DFS(matrix, y - 1, x - 1 )  # upper left cell
    #print ("upper right cell")
    visit_is_land_DFS(matrix, y + 1, x - 1 )  # upper right cell
    #print ("lower right cell")
    visit_is_land_DFS(matrix, y + 1, x + 1 )  # lower right cell



def main():
  sol = Solution()
  print(sol.countIslands([[1, 1, 1, 0, 0], [0, 1, 0, 0, 1], [
        0, 0, 1, 1, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]))
  print(sol.countIslands([[0, 1, 1, 1, 0], [0, 0, 0, 1, 1], [
        0, 1, 1, 1, 0], [0, 1, 1, 0, 0], [0, 0, 0, 0, 0]]))

print(countIslands([[0, 1, 0, 0],
                    [1, 0, 1, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 1]]))
sys.exit(0)

print(countIslands([[0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1]]))
sys.exit(0)
# should be 2?
print(countIslands([[1, 1, 1, 0, 0],
                    [0, 1, 0, 0, 1],
                    [0, 0, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 1]]))
sys.exit(0)


# should be 3?
print(countIslands([ [1,0,1,1,1],
                     [0,0,1,1,0],
                     [0,1,0,0,0],
                     [0,0,0,1,1] ]))

# is 1
print(countIslands([ [0,0,1,1,0],
                     [1,1,1,1,0],
                     [0,1,0,0,0],
                     [0,0,0,0,0] ]))

# is 1
print(countIslands([[0, 1, 1, 1, 0],
                    [0, 0, 0, 1, 1],
                    [0, 1, 1, 1, 0],
                    [0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0]]))

#main()
