from collections import defaultdict
from typing import DefaultDict

import main
import string
import random
import time

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

y_time_lev_rec = []
y_time_lev_matrix_rec = []
y_time_lev_matrix = []
y_time_dlev = []
N = 0
len_arr = []


def test(len):
    time_lev_rec = 0
    time_lev_matrix_rec = 0
    time_lev_matrix = 0
    time_dlev = 0

    for i in range(N):
        s1 = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=len))
        s2 = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=len))

        start = time.process_time()
        main.levenshtein_matrix(s1, s2, False)
        stop = time.process_time()

        time_lev_matrix += stop - start

        start = time.process_time()
        main.levenshtein_matrix_recursive(s1, s2, False)
        stop = time.process_time()

        time_lev_matrix_rec += stop - start

        start = time.process_time()
        main.levenshtein_recursive(s1, s2, False)
        stop = time.process_time()

        time_lev_rec += stop - start

        start = time.process_time()
        main.damerau_levenshtein_recursive(s1, s2, False)
        stop = time.process_time()

        time_dlev += stop - start

    len_arr.append(len)
    y_time_lev_rec.append((time_lev_rec / N) * 1000000)
    y_time_lev_matrix_rec.append((time_lev_matrix_rec / N) * 1000000)
    y_time_lev_matrix.append((time_lev_matrix / N) * 1000000)
    y_time_dlev.append((time_dlev / N) * 1000000)


    return (time_lev_matrix / N) * 1000000, (time_lev_matrix_rec / N) * 1000000, (time_lev_rec / N) * 1000000, (time_dlev / N) * 1000000


def print_results(count):
    return count, *test(count)


def reset():
    global y_time_lev_rec
    global y_time_lev_matrix_rec
    global y_time_lev_matrix
    global y_time_dlev
    global len_arr

    y_time_dlev.clear()
    y_time_lev_rec.clear()
    y_time_lev_matrix.clear()
    y_time_lev_matrix_rec.clear()
    len_arr.clear()


if __name__ == "__main__":


    st.header("Algo demo")
    
    s1 = st.text_input("String 1 to calc distance on", "abcd")
    s2 = st.text_input("String 2 to calc distance on", "abed")

    alg_choices = {
          "1. Расстояние Левенштейна рекурсивно" : main.levenshtein_recursive,
          "2. Расстояние Левенштейна матрица": main.levenshtein_matrix,
          "3. Расстояние Левенштейна рекурсивно (кеш)": main.levenshtein_matrix_recursive,
          "4. Расстояние Дамерау-Левенштейна рекурсивно" : main.damerau_levenshtein_recursive,
    }

    choice = st.radio("Algorithm", list(alg_choices.keys()))
    result = alg_choices[choice](s1, s2)
    st.write("Result:", result)


    st.header("Statistics")

    st.button("reset statistics", reset)

    N = st.slider("String length", 1, 100, 50)

    cols = [
        "n",
        "Матричный способ нахождения расстояния Левенштейна:",
        "Матричный способ нахождения расстояния Левенштейна с использованием рекурсии:",
        "Нахождение расстояния Левенштейна с использованием рекурсии:",
        "Нахождение расстояния Дамерау-Левенштейна c использования рекурсии:",
    ]

    d = defaultdict(list)

    for i in range(1, 7):
       for cn, rs in zip(cols, print_results(i)):
           d[cn].append(rs)

    st.table(pd.DataFrame(d))

    fig = plt.figure(figsize = (10, 7))
    plot = fig.add_subplot()
    plot.plot(len_arr, y_time_lev_rec, label = "Р-Левенштейна(рек)")
    # plot.plot(len_arr, y_time_lev_matrix_rec, label = "Р-Левенштейна(рек+кеш)")
    # plot.plot(len_arr, y_time_lev_matrix, label = "Р-Левенштейна(мат)")
    plot.plot(len_arr, y_time_dlev, label = "Р-Дамерау-Левенштейна")
    plt.legend()
    plt.grid()
    plt.title("Временные характеристики алгоритмов вычисления расстояния")
    plt.ylabel("Затраченное время (мск)")
    plt.xlabel("Длина (симболы")


    fig1 = plt.figure(figsize = (10, 7))
    plot = fig1.add_subplot()
    # plot.plot(len_arr, y_time_lev_rec, label = "Р-Левенштейна(рек)")
    plot.plot(len_arr, y_time_lev_matrix_rec, label = "Р-Левенштейна(рек+кеш)")
    plot.plot(len_arr, y_time_lev_matrix, label = "Р-Левенштейна(мат)")
    # plot.plot(len_arr, y_time_dlev, label = "Р-Дамерау-Левенштейна")
    plt.legend()
    plt.grid()
    plt.title("Временные характеристики алгоритмов вычисления расстояния")
    plt.ylabel("Затраченное время (мск)")
    plt.xlabel("Длина (симболы")

    fig1 = plt.figure(figsize=(10, 7))
    plot = fig1.add_subplot()
    plot.plot(len_arr, y_time_lev_rec, label = "Р-Левенштейна(рек)")
    plot.plot(len_arr, y_time_lev_matrix_rec, label="Р-Левенштейна(рек+кеш)")
    plot.plot(len_arr, y_time_lev_matrix, label="Р-Левенштейна(мат)")
    plot.plot(len_arr, y_time_dlev, label = "Р-Дамерау-Левенштейна")
    plt.legend()
    plt.grid()
    plt.title("Временные характеристики алгоритмов вычисления расстояния")
    plt.ylabel("Затраченное время (мск)")
    plt.xlabel("Длина (симболы)")

    st.pyplot(fig)
    st.pyplot(fig1)
