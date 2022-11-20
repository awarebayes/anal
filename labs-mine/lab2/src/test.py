from time import process_time_ns
import matplotlib.pyplot as plt
from algs import classic, vinograd, optvinograd
from random import randint
import numpy as np
import pandas as pd
import matplotlib
from tqdm import tqdm
matplotlib.use("tkAgg")


def measure_func(matrix_1, matrix_2, func, N):
    tm = process_time_ns()
    for i in range(N):
        func(matrix_1, matrix_2)
    return int((process_time_ns() - tm) / N)

def measure_time():
    classic_time = []
    vinograd_time = []
    optvinograd_time = []
    # N = [1, 3, 5, 9, 15, 31, 51, 75, 101, 201, 401, 501, 601, 701, 801, 901, 1001]
    N = [2, 4, 6, 10, 16, 30, 50, 76, 100, 200, 400, 500, 600, 700, 800, 900, 1000]
    for n_elem in tqdm(N):
        matrix_1 = np.array([[randint(-50, 50) for i in range(n_elem)] for j in range(n_elem)])
        matrix_2 = np.array([[randint(-50, 50) for i in range(n_elem)] for j in range(n_elem)])

        k = 500
        if (n_elem > 20):
            k = 15
        if (n_elem > 100):
            k = 5
        if (n_elem > 150):
            k = 1

        classic_time.append(measure_func(matrix_1, matrix_2, classic, k))
        vinograd_time.append(measure_func(matrix_1, matrix_2, vinograd, k))
        optvinograd_time.append(measure_func(matrix_1, matrix_2, optvinograd, k))
    
    plt.title("Измерение времени для чётных N")
    plt.xlabel("Размер квадратной матрицы")
    plt.ylabel("Время работы в нс")
    plt.plot(N, classic_time, label = "classic")
    plt.plot(N, vinograd_time, label = "vinograd")
    plt.plot(N, optvinograd_time, label = "opt_vinograd")

    plt.legend()
    plt.show()
    return classic_time, vinograd_time, optvinograd_time, N

classic_time, vinograd_time, optvinograd_time, N = measure_time()

df = pd.DataFrame({'N': N, 'classic': classic_time, 'vinograd': vinograd_time, 'opt_vinograd': optvinograd_time})
print(df.to_latex(index=False))

#print("LLVM:")
#llvm = vinograd.inspect_llvm()
#print(list(llvm.values())[0])
