cmake_minimum_required(VERSION 3.23)
project(lab1_cpp_frfr)

set(CMAKE_CXX_STANDARD 20)

add_executable(lab1_cpp_frfr main.cpp)

find_package(FunctionalPlus)
target_link_libraries(lab1_cpp_frfr FunctionalPlus::fplus)
