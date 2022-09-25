#include <iostream>
#include <cstdlib>
#include <chrono>
#include <fplus/fplus.hpp>

using matrix_t = std::vector<std::vector<int>>;

matrix_t get_matrix(std::size_t l1, std::size_t l2) {
    matrix_t mat;
    for (int i = 0; i < l1 + 1; i++) {
        mat.emplace_back(std::vector<int>(l2 + 1));
        for (int j = 0; j < l2 + 1; j++) {
            mat[i][j] = i + j;
        }
    }
    return mat;
}

int lev_recursion(std::string_view s1, std::string_view s2) {
    std::size_t l1 = s1.length();
    std::size_t l2 = s2.length();

    if (l1 == 0 or l2 == 0)
        return abs(static_cast<int>(l1 - l2));

    int m = 1;
    if (s1.back() == s2.back())
        m = 0;
    return fplus::minimum(std::array<int, 3>({
                                                     lev_recursion(s1, s2.substr(0, s2.length() - 2)) + 1,
                                                     lev_recursion(s1.substr(0, s1.length() - 2), s2) + 1,
                                                     lev_recursion(s1.substr(0, s1.length() - 2),
                                                                   s2.substr(0, s2.length() - 2)) + m
                                             }));
}

int lev_table(std::string_view s1, std::string_view s2) {
    std::size_t l1 = s1.length();
    std::size_t l2 = s2.length();
    matrix_t mat = get_matrix(l1, l2);

    for (int i = 1; i < l1 + 1; i++) {
        for (int j = 1; j < l2 + 1; j++) {
            int m = 1;
            if (s1[i - 1] == s2[j - 1])
                m = 0;
            mat[i][j] = fplus::minimum(
                    std::array<int, 3>{
                            mat[i - 1][j] + 1,
                            mat[i][j - 1] + 1,
                            mat[i - 1][j - 1] + m
                    });
        }
    }

    return mat[l1][l2];
}

int dam_lev_recursion(std::string_view s1, std::string_view s2) {

    std::size_t l1 = s1.length();
    std::size_t l2 = s2.length();

    if (l1 == 0 or l2 == 0) {
        return abs(static_cast<int>(l1 - l2));
    }

    int m = 1;
    if (s1.back() == s2.back())
        m = 0;

    int result = fplus::minimum(std::array<int, 3>({
                                                           dam_lev_recursion(s1, s2.substr(0, s2.length() - 2)) + 1,
                                                           dam_lev_recursion(s1.substr(0, s1.length() - 2), s2) + 1,
                                                           dam_lev_recursion(s1.substr(0, s1.length() - 2),
                                                                             s2.substr(0, s2.length() - 2)) + m
                                                   }));

    if (l1 > 1 and l2 > 1 and s1[s1.length() - 1] == s2[s2.length() - 2] and s1[s1.length() - 2] == s2[s2.length() - 1])
        result = std::min(result, dam_lev_recursion(s1.substr(0, s1.length() - 2), s2.substr(0, s2.length() - 2)) + 1);

    return result;
}

int dam_lev_table(std::string_view s1, std::string_view s2) {

    std::size_t l1 = s1.length();
    std::size_t l2 = s2.length();

    matrix_t mat = get_matrix(l1, l2);

    for (int i = 1; i < l1 + 1; i++) {
        for (int j = 1; j < l2 + 1; j++) {
            int m = 1;
            if (s1[i - 1] == s2[j - 1])
                m = 0;
            mat[i][j] = fplus::minimum(
                    std::array<int, 3>{
                            mat[i - 1][j] + 1,
                            mat[i][j - 1] + 1,
                            mat[i - 1][j - 1] + m
                    });
            if (i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1])
                mat[i][j] = std::min(mat[i][j], mat[i - 2][j - 2] + 1);
        }
    }

    return mat[l1][l2];
}

std::string permute(std::string str, std::size_t n)
{
    std::size_t pos = 0;
    for (std::size_t i = 0; i < n; i++)
    {
        pos = rand() % str.length();
        str[pos] = '0' + rand() % 32;
    }
    return str;
}

std::string rand_string(std::size_t n)
{
    std::string result;
    result.resize(n);
    for (std::size_t i = 0; i < n; i++)
    {
        result[i] = '0' + rand() % 32;
    }
    return result;
}

using string_distance_fn_t = std::function<int(std::string_view, std::string_view)>;

float benchmark(string_distance_fn_t fn)
{
    const float percent_permute = 0.5;
    const std::size_t str_length = 10;
    const std::size_t n_trials = 10;
    const auto n_permute = static_cast<std::size_t>(str_length * percent_permute);

    float sum = 0;
    for (int i = 0; i <= n_trials; i++)
    {
        std::string initial_str = rand_string(str_length);
        std::string permuted_str = permute(initial_str, n_permute);
        auto begin = std::chrono::high_resolution_clock::now();

        auto res = fn(initial_str, permuted_str);

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<float> time_taken = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
        sum += time_taken.count();

        auto target_res = lev_table(initial_str, permuted_str);
        assert(res == target_res);
    }
    return sum / (float)n_trials;
}

int main() {
    std::cout << "Hello, World!" << std::endl;
    std::cout << dam_lev_recursion("lock", "lick") << std::endl;
    std::cout << benchmark(lev_recursion) << std::endl;

    return 0;
}
