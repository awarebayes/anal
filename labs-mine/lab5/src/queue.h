//
// Created by Mikhail on 04.11.2022.
//

#ifndef SRC_QUEUE_H
#define SRC_QUEUE_H

#include <queue>
#include <iostream>
#include <vector>

using namespace std::chrono_literals;

template<typename T>
struct Queue
{
private:
    std::queue<T> queue;
    std::mutex mutex;
    std::condition_variable cv;
public:
    void push(T item)
    {
        std::unique_lock<std::mutex> lock(mutex);
        queue.push(item);
        cv.notify_one();
    }

    std::optional<T> pop()
    {
        std::unique_lock<std::mutex> lock(mutex);
        if (cv.wait_for(lock, 10000ms, [this](){ return !queue.empty(); }))
        {
            auto item = queue.front();
            queue.pop();
            return std::move(item);
        }
        return std::nullopt;
    }
};

#endif //SRC_QUEUE_H
