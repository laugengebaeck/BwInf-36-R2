#!/usr/bin/env python3

import numpy as np
import matplotlib.pylab as plt
from matplotlib import colors
import os


def possible_paths(n):
    path = n
    matrix = np.loadtxt(path, skiprows=1)

    N = len(matrix)

    # top -> bot
    top_to_bot_float = np.matrix([[0.0] * N] * N)
    top_to_bot_bool = np.matrix([[True] * N] * N)
    # bot -> top
    bot_to_top_float = np.matrix([[0.0] * N] * N)
    bot_to_top_bool = np.matrix([[True] * N] * N)
    # left -> right
    left_to_right_float = np.matrix([[0.0] * N] * N)
    left_to_right_bool = np.matrix([[True] * N] * N)
    # right -> left
    right_to_left_float = np.matrix([[0.0] * N] * N)
    right_to_left_bool = np.matrix([[True] * N] * N)

    for i in range(N):
        for j in range(N):
            # top -> bot
            if i != N - 1:
                top_to_bot_bool[i, j] = abs(matrix[i, j] - matrix[i+1, j]) < 1
            # bot -> top
            if i != 0:
                bot_to_top_bool[i, j] = abs(matrix[i, j] - matrix[i-1, j]) < 1
            # left -> right
            if j != N - 1:
                left_to_right_bool[i, j] = abs(matrix[i, j] - matrix[i, j+1]) < 1
            # right -> left
            if j != 0:
                right_to_left_bool[i, j] = abs(matrix[i, j] - matrix[i, j-1]) < 1
    

    for i in range(N):
        for j in range(N):
            top_to_bot_bool[i, j] = not(top_to_bot_bool[i, j]) or not(left_to_right_bool[i, j])
    
    n = n.split(".")[0]

    # overview
    plt.imshow(matrix, interpolation='nearest', cmap='hot')
    plt.savefig("extras/"+n+"-heatmap.png", bbox_inches='tight')

    # bool
    # top -> bot
    plt.imshow(top_to_bot_bool, interpolation='nearest', cmap='Greys_r', vmin=0, vmax=1)
    plt.savefig("extras/"+n+"-top_to_bot_bool.png", bbox_inches='tight')

if __name__ == '__main__':
    name = input("Datei visualisieren: ")
    possible_paths(name)
