from collections import defaultdict
from typing import DefaultDict, List

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
y_time_dlev_matrix: List[float] = []
y_time_dlev_cache: List[float] = []

N = 10
len_arr = []

def test(length):
    time_lev_rec = 0
    time_lev_matrix_rec = 0
    time_lev_matrix = 0
    time_dlev = 0
    time_dlev_matrix = 0
    time_dlev_cache = 0

    cum_times = [time_lev_rec, time_lev_matrix_rec, time_lev_matrix, time_dlev, time_dlev_matrix, time_dlev_cache]

    # warmup
    for i in range(100):
        main.levenshtein_matrix("biba", "boba")

    for i in range(N):
        s1 = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=length))
        s2 = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=length))

        start = time.process_time()
        main.levenshtein_matrix(s1, s2)
        stop = time.process_time()

        time_lev_matrix += stop - start

        start = time.process_time()
        main.levenshtein_matrix_recursive(s1, s2)
        stop = time.process_time()

        time_lev_matrix_rec += stop - start

        start = time.process_time()
        main.levenshtein_recursive(s1, s2)
        stop = time.process_time()

        time_lev_rec += stop - start

        start = time.process_time()
        main.damerau_levenshtein_recursive(s1, s2)
        stop = time.process_time()

        time_dlev += stop - start

        start = time.process_time()
        main.damerau_levenshtein_matrix(s1, s2)
        stop = time.process_time()

        time_dlev_matrix += stop - start

        start = time.process_time()
        main.damerau_levenshtein_cached(s1, s2)
        stop = time.process_time()

        time_dlev_cache += stop - start

        times = [time_lev_rec, time_lev_matrix_rec, time_lev_matrix, time_dlev, time_dlev_matrix, time_dlev_cache]
        for i in range(len(times)):
            cum_times[i] += times[i]


    len_arr.append(length)
    y_time_lev_rec.append((time_lev_rec / N) * 1000000)
    y_time_lev_matrix_rec.append((time_lev_matrix_rec / N) * 1000000)
    y_time_lev_matrix.append((time_lev_matrix / N) * 1000000)
    y_time_dlev.append((time_dlev / N) * 1000000)
    y_time_dlev_matrix.append((time_dlev_matrix / N) * 1000000)
    y_time_dlev_cache.append((time_dlev_cache / N) * 1000000)

    times = [time_lev_rec, time_lev_matrix_rec, time_lev_matrix, time_dlev, time_dlev_matrix, time_dlev_cache]
    return cum_times

def get_memory_usage(str_len: int):
    memory_usage = defaultdict(float)
    for key, fn in {
        "Levenstein recursive": main.levenshtein_recursive,
        "Leventein matrix recursive": main.levenshtein_matrix_recursive,
        "Levenstein matrix": main.levenshtein_matrix,
        "Dameau-Levenstein recursive": main.damerau_levenshtein_recursive,
    }.items():
        print("mem usage for", key)
        memory_usage[key] = main.memory_analysis(fn, str_len)
        print("completed")
    return memory_usage


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
          "3. Расстояние Левенштейна матрицей рекурсивно": main.levenshtein_matrix_recursive,
          "4. Расстояние Дамерау-Левенштейна рекурсивно" : main.damerau_levenshtein_recursive,
          "5. Расстояние Дамерау-Левенштейна матрицей" : main.damerau_levenshtein_matrix,
          "5. Расстояние Дамерау-Левенштейна матрицей рекурсивно" : main.damerau_levenshtein_cached,
    }

    choice = st.radio("Algorithm", list(alg_choices.keys()))
    result = alg_choices[choice](s1, s2)
    st.write("Result:", result)

    st.header("Statistics")

    st.button("reset statistics", reset)

    N = st.slider("String length", 1, 100, 50)

    cols = [
        "n",
        "Левенштейн рекурсивно",
        "Левенштейн рекурсивно матрицей",
        "Левенштейн матрицей",
        "Левенштейн-Дамерау рекурсивно",
        "Левенштейн-Дамерау матрицей",
        "Левенштейн-Дамерау рекурсивно матрицей",
    ]

    d = defaultdict(list)

    for i in range(1, 7):
       for cn, rs in zip(cols, print_results(i)):
           d[cn].append(rs)

    df = pd.DataFrame(d)
    df.round(3).to_csv("time_measure.csv", index=False)
    st.table(df)

    fig = plt.figure(figsize = (10, 7))
    plot = fig.add_subplot()

    if st.checkbox("Р-левенштейна(рек)", True):
        plot.plot(len_arr, y_time_lev_rec, label = "Р-Левенштейна(рек)")
    if st.checkbox("Р-левенштейна(матрица)", True):
        plot.plot(len_arr, y_time_lev_matrix, label = "Р-Левенштейна(мат)")
    if st.checkbox("Р-левенштейна(рек матрица)", True):
        plot.plot(len_arr, y_time_lev_matrix_rec, label = "Р-Левенштейна(рек+мат)")
    if st.checkbox("Р-левенштейна-Дамерау(рек)", True):
        plot.plot(len_arr, y_time_dlev, label = "Р-Дамерау-Левенштейна")
    if st.checkbox("Р-левенштейна-Дамерау(матрица)", True):
        plot.plot(len_arr, y_time_dlev_matrix, label = "Р-Дамерау-Левенштейна(мат)")
    if st.checkbox("Р-левенштейна-Дамерау(рек матрица)", True):
        plot.plot(len_arr, y_time_dlev_cache, label = "Р-Дамерау-Левенштейна(рек+мат)")
    plt.legend()
    plt.grid()
    plt.title("Временные характеристики алгоритмов вычисления расстояния")
    plt.ylabel("Затраченное время (мск)")
    plt.xlabel("Длина (симболы")

    st.pyplot(fig)

    fig = plt.figure(figsize=(10, 7))

    """
    df = defaultdict(list)
    bar = st.progress(0)
    
    
    for strlen in range(2, 8):
        for key, usage in get_memory_usage(strlen).items():
            df[key].append(usage)
        bar.progress(int(strlen / 7 * 100))

    print(df)
    df = pd.DataFrame(df)
    st.dataframe(df)

    """


