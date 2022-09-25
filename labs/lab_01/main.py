import gc
import string
import random
from time import time, thread_time, process_time
import psutil
from functools import lru_cache
import numpy as np
import streamlit
import datetime

CACHE_SIZE = 0

class DummyProfiler:
    def trace(self):
        pass
class MemoryTracker:
    def __init__(self):
        self.usage = []
        self.started = 0
        self.ended = 0
        self.process = psutil.Process()
        self.last_collected = datetime.time()

    def start(self):
        gc.collect()
        mem_usage = self.process.memory_info().rss / (1024 * 1024)
        self.started = mem_usage

    def trace(self):
        mem_usage = self.process.memory_info().rss / (1024 * 1024)
        self.usage.append(mem_usage)

    def end(self) -> float:
        gc.collect()
        mem_usage = self.process.memory_info().rss / (1024 * 1024)
        self.ended = mem_usage
        self.started = min(self.usage)
        mean = np.mean(self.usage)
        return {
            'started': self.started, 'ended': self.ended, 'mean': mean,
            'mean_relative': mean - self.started,
            'array': self.usage
        }


"""
    Функция для печати матрицы
"""
def print_matrix(str1, str2, matrix):
    print("0  0  " + "  ".join([letter for letter in str2]))

    for i in range(len(str1) + 1):
        print(str1[i - 1] if i != 0 else "0", end="")
        for j in range(len(str2) + 1):
            print("  " + str(matrix[i][j]), end="")
        print("")

"""
    Функция для создания матрицы, которая заполнена 0, 
    кроме 0 строки и 0 столбца
"""
def create_matrix(n, m):
    matrix = [[0] * m for i in range(n)]

    # заполняем 0 строку
    for j in range(m):
        matrix[0][j] = j

    # заполняем 0 столбец
    for i in range(n):
        matrix[i][0] = i

    return matrix

"""
    Функция для вычисления расстояния Левенштейна,
    рекурсивно.
"""
@lru_cache(maxsize=CACHE_SIZE)
def levenshtein_recursive(str1, str2, profiler=DummyProfiler()):
    profiler.trace()
    n = len(str1)
    m = len(str2)

    if n == 0 or m == 0:
        return abs(n - m)

    flag = 0
    if str1[-1] != str2[-1]:
        flag = 1

    min_lev_rec = min(levenshtein_recursive(str1[:-1], str2, profiler) + 1,
                      levenshtein_recursive(str1, str2[:-1], profiler) + 1,
                      levenshtein_recursive(str1[:-1], str2[:-1], profiler) + flag)
    profiler.trace()
    return min_lev_rec


"""
    Функция для вычисления расстояния Левенштейна,
    матрично.
"""
def levenshtein_matrix(str1, str2, profiler=DummyProfiler()):
    profiler.trace()
    n = len(str1)
    m = len(str2)

    matrix = create_matrix(n + 1, m + 1)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            add, delete, change = matrix[i - 1][j] + 1,\
                                  matrix[i][j - 1] + 1,\
                                  matrix[i - 1][j - 1]
            if str2[j - 1] != str1[i - 1]:
                change += 1
            else:
                change += 0

            matrix[i][j] = min(add, delete, change)

    profiler.trace()
    return matrix[n][m]


"""
    Функция для вычисления расстояния Левенштейна,
    матрица заполянется рекурсивно.
"""
@lru_cache(maxsize=CACHE_SIZE)
def levenshtein_matrix_recursive(str1, str2, profiler=DummyProfiler()):
    profiler.trace()
    n = len(str1)
    m = len(str2)

    def recursive(str1, str2, n, m, matrix):
        profiler.trace()
        if (matrix[n][m] != -1):
            # print("if (matrix[n][m] != -1):")
            return matrix[n][m]

        if (n == 0):
            # print("if (n == 0):")
            matrix[n][m] = m
            return matrix[n][m]

        if (n > 0 and m == 0):
            # print("if (n > 0 and m == 0):")
            matrix[n][m] = n
            return matrix[n][m]

        delete = recursive(str1, str2, n - 1, m, matrix) + 1
        add = recursive(str1, str2, n, m - 1, matrix) + 1

        flag = 0

        if (str1[n - 1] != str2[m - 1]):
            flag = 1

        change = recursive(str1, str2, n - 1, m - 1, matrix) + flag
        # print("Рекурсия с матрицей), n, m, str1, str2", n, m, str1, str2)
        # print_matrix(str1, str2, matrix)

        matrix[n][m] = min(add, delete, change)

        # print()
        # print_matrix(str1, str2, matrix)
        profiler.trace()

        return matrix[n][m]

    matrix =  create_matrix(n + 1, m + 1)
    # print("begin")
    # print_matrix(str1, str2, matrix)

    for i in range(n + 1):
        for j in range(m + 1):
            matrix[i][j] = -1

    # print("begin2")
    # print_matrix(str1, str2, matrix)

    recursive(str1, str2, n, m, matrix)

    #if out_put:
        #print("Расстояние, вычисленное с помощью матрицы Левенштейна (рекурсивно)")
        #print_matrix(str1, str2, matrix)
        #print("Расстояние равно ", matrix[n][m])
    profiler.trace()

    return matrix[n][m]


# """
#     Функция для вычисления расстояния Дфмерау - Левенштейна,
#     матрица.
# """
def damerau_levenshtein_matrix(str1, str2, profiler=DummyProfiler()):
     profiler.trace()
     n = len(str1)
     m = len(str2)

     matrix = create_matrix(n + 1, m + 1)
     
     for i in range(1, n + 1):
         for j in range(1, m + 1):
             add, delete, change = matrix[i - 1][j] + 1, \
                                   matrix[i][j - 1] + 1, \
                                   matrix[i - 1][j - 1]
             if str2[j - 1] != str1[i - 1]:
                 change += 1
             else:
                 change += 0

             matrix[i][j] = min(add, delete, change)

             if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] \
                     and str1[i - 2] == str2[j - 1]:
                 matrix[i][j] = min(matrix[i][j], matrix[i - 2][j - 2] + 1)

     profiler.trace
     return matrix[n][m]

"""
    Функция для вычисления расстояния Дфмерау - Левенштейна,
    рекурсивно.
"""
@lru_cache(maxsize=CACHE_SIZE)
def damerau_levenshtein_recursive(str1, str2, profiler=DummyProfiler()):
    profiler.trace()
    n = len(str1)
    m = len(str2)

    if n == 0 or m == 0:
        if n != 0:
            return n
        if m != 0:
            return m
        return 0

    change = 0
    if str1[-1] != str2[-1]:
        change += 1

    if n > 1 and m > 1 and str1[-1] == str2[-2] \
        and str1[-2] == str2[-1]:
        min_ret = min(damerau_levenshtein_recursive(str1[:n - 1], str2) + 1,
                      damerau_levenshtein_recursive(str1, str2[:m - 1]) + 1,
                      damerau_levenshtein_recursive(str1[:n - 1], str2[:m - 1]) + change,
                      damerau_levenshtein_recursive(str1[:n - 2], str2[:m - 2]) + 1)
    else:
        min_ret = min(damerau_levenshtein_recursive(str1[:n - 1], str2) + 1,
                      damerau_levenshtein_recursive(str1, str2[:m - 1]) + 1,
                      damerau_levenshtein_recursive(str1[:n - 1], str2[:m - 1]) + change)
    profiler.trace()
    return min_ret

@lru_cache(maxsize=CACHE_SIZE)
def damerau_levenshtein_cached(str1, str2, profiler=DummyProfiler()):
    profiler.trace()
    n = len(str1)
    m = len(str2)

    def recursive(str1, str2, n, m, matrix):
        profiler.trace()
        if (matrix[n][m] != -1):
            # print("if (matrix[n][m] != -1):")
            return matrix[n][m]

        if (n == 0):
            # print("if (n == 0):")
            matrix[n][m] = m
            return matrix[n][m]

        if (n > 0 and m == 0):
            # print("if (n > 0 and m == 0):")
            matrix[n][m] = n
            return matrix[n][m]

        delete = recursive(str1, str2, n - 1, m, matrix) + 1
        add = recursive(str1, str2, n, m - 1, matrix) + 1

        flag = 0

        if (str1[n - 1] != str2[m - 1]):
            flag = 1

        change = recursive(str1, str2, n - 1, m - 1, matrix) + flag

        matrix[n][m] = min(add, delete, change)

        if n > 1 and m > 1 and str1[n - 1] == str2[m - 2] \
                     and str1[n - 2] == str2[m - 1]:
                 matrix[n][m] = min(matrix[n][m], matrix[n - 2][m - 2] + 1)



        # print()
        # print_matrix(str1, str2, matrix)
        profiler.trace()

        return matrix[n][m]

    matrix =  create_matrix(n + 1, m + 1)
    # print("begin")
    # print_matrix(str1, str2, matrix)

    for i in range(n + 1):
        for j in range(m + 1):
            matrix[i][j] = -1

    # print("begin2")
    # print_matrix(str1, str2, matrix)

    recursive(str1, str2, n, m, matrix)

    #if out_put:
        #print("Расстояние, вычисленное с помощью матрицы Левенштейна (рекурсивно)")
        #print_matrix(str1, str2, matrix)
        #print("Расстояние равно ", matrix[n][m])
    profiler.trace()

    return matrix[n][m]


def words_algoritm(func):
    str1 = input("Введите первую строку 1: ")
    str2 = input("Введите первую строку 2: ")

    res = func(str1, str2, True)
    print("Distanse = ", res)
    print("DONE!")


def random_string(str_len):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_len))

def time_analysis(func, count = 100, str_len = 8):
    duration = 0
    for i in range(count):
        str1 = random_string(str_len)
        str2 = random_string(str_len)
        start = process_time()
        func(str1, str2, False)
        end = process_time()
        duration += end - start
    return duration / count


def memory_analysis(func, count=1, str_len=8):
    summa = 0
    for i in range(count):

        profiler = MemoryTracker()
        profiler.start()
        str1 = random_string(str_len)
        str2 = random_string(str_len)
        func(str1, str2, profiler)
        statistics = profiler.end()

        summa += statistics['mean_relative']

    return summa / count

def main():
    do_start = True

    while(do_start):
        command = input("\n\nМЕНЮ: \n"
                        "\t 0. Выход\n"
                        "\t 1. Расстояние Левенштейна рекурсивно\n"
                        "\t 2. Расстояние Левенштейна матрица\n"
                        "\t 3. Расстояние Левенштейна рекурсивно (кеш)\n"
                        "\t 4. Расстояние Дамерау-Левенштейна рекурсивно\n"
                        "\t 5. Все алгоритмы вместе\n"
                        "\t 6. Замер времени (длина слов от 1 до 10)\n"
                        "\t Выбор: ")
        if (command == "1"):
            words_algoritm(levenshtein_recursive)
        elif (command == "2"):
            words_algoritm(levenshtein_matrix)
        elif (command == "3"):
            words_algoritm(levenshtein_matrix_recursive)
        elif (command == "4"):
            words_algoritm(damerau_levenshtein_recursive)
        elif (command == "5"):
            y = []
            str1 = input("Введите первую строку 1: ")
            str2 = input("Введите первую строку 2: ")

            res = levenshtein_recursive(str1, str2)
            print("\nРасстрояние Левенштейна, полученное с использованием рекурсии: ", res)
            levenshtein_matrix(str1, str2)
            levenshtein_matrix_recursive(str1, str2)

            res = damerau_levenshtein_recursive(str1, str2)
            print("\nРасстрояние Дамерау-Левенштейна, полученное с использованием рекурсии: ", res)
        elif (command == "6"):
            count = 100
            for i in range(1, 5, 1):
                print("String len: ", i)
                print("   Lev recursion   : ", "{0:.15f}".format(time_analysis(levenshtein_recursive, count, i)))
                print("   Lev table       : ", "{0:.15f}".format(time_analysis(levenshtein_matrix, count, i)))
                print("   Lev table recurs: ", "{0:.15f}".format(time_analysis(levenshtein_matrix_recursive, count, i)))
                print("   DamLev recursion: ", "{0:.15f}".format(time_analysis(damerau_levenshtein_recursive, count, i)))
        else:
            do_start = False

if __name__ == "__main__":
    main()