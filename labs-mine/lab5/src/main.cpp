#include <iostream>
#include <vector>
#include <optional>
#include <thread>
#include "queue.h"

int factorial(int n)
{
    int res = 1;
    for (int i = 1; i <= n; ++i)
    {
        res *= i;
    }
    return res;
}

struct Stage
{
    std::string_view stage_name;
    std::function<void()> work;
    int stage_number{};
    std::shared_ptr<Stage> next_stage{};
};

struct StageWithCallback
{
    std::shared_ptr<Stage> stage;
    std::function<void(const Stage &result)> on_complete;
};

struct Task
{
    std::string_view task_name;
    std::vector<std::shared_ptr<Stage>> stages;
    std::chrono::time_point<std::chrono::system_clock> start_time{};
    std::chrono::time_point<std::chrono::system_clock> end_time{};

    Task &add_stage(std::string_view stage_name, std::function<void()> work)
    {
        stages.emplace_back(std::make_shared<Stage>(Stage{stage_name, work, static_cast<int>(stages.size())}));
        if (stages.size() > 1)
        {
            stages[stages.size() - 2]->next_stage = stages[stages.size() - 1];
        }
        return *this;
    }

    Task &complete_building()
    {
        auto stages_0_original_work = stages[0]->work;
        stages[0]->work = [this, stages_0_original_work](){
            this->start_time = std::chrono::system_clock::now();
            stages_0_original_work();
        };

        auto last_stages_original_work = stages[stages.size() - 1]->work;
        stages[stages.size() - 1]->work = [this, last_stages_original_work](){
            last_stages_original_work();
            this->end_time = std::chrono::system_clock::now();
            //std::cout << "Task " << task_name << " completed in " << std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count() << " ms" << std::endl;
        };
        return *this;
    }
};

struct SequentialPipeline
{
    void run(const std::vector<Task> &tasks)
    {
        for (const auto &task : tasks)
        {
            for (const auto &stage : task.stages)
            {
                stage->work();
            }
        }
    }
};

struct PiplinedPipeline
{
    std::vector<std::shared_ptr<Queue<StageWithCallback>>> queues;
    std::optional<std::reference_wrapper<Queue<StageWithCallback>>> find_queue_with_index(int index)
    {
        if (index < queues.size())
            return *queues[index];
        return std::nullopt;
    }

    void push_result_to_next_queue(const Stage& result)
    {
        auto maybe_next_queue = find_queue_with_index(result.stage_number + 1);
        if (maybe_next_queue)
        {
            auto& next_queue = maybe_next_queue.value().get();
            auto next_stage = result.next_stage;
            next_queue.push({next_stage, [this](const Stage& result_) {
                push_result_to_next_queue(result_);
            }});
        }
    }

    void run(const std::vector<Task> &tasks)
    {
        auto n_stages = tasks[0].stages.size();
        if (queues.size() != n_stages)
        {
            for (int i = 0; i < n_stages; ++i)
            {
                queues.emplace_back(std::make_shared<Queue<StageWithCallback>>());
            }
        }

        for (auto& task : tasks)
        {
            auto &stage = task.stages[0];
            auto &entry_queue = queues[0];
            assert(task.stages.size() == n_stages);
            entry_queue->push(StageWithCallback{stage,
            [this](const Stage& result) {
                push_result_to_next_queue(result);
            }});
        }

        std::vector<std::thread> thread_pool;
        int n_tasks = tasks.size();
        for (int i = 0; i < queues.size(); ++i)
        {
            auto& queue = queues[i];
            thread_pool.emplace_back([&queue, n_tasks]() {
                int tasks_completed = 0;
                while (tasks_completed < n_tasks)
                {
                    auto maybe_stage = queue->pop();
                    if (maybe_stage)
                    {
                        auto& stage = maybe_stage.value();
                        stage.stage->work();
                        stage.on_complete(*stage.stage);
                    }
                    else
                        break;
                }
            });
        }

        for (auto& thread: thread_pool)
            thread.join();

    }
};


int main() {
    std::vector<Task> tasks;

    for (int i = 0; i < 10000; i++)
    {
        const int facn = 10000;
        auto t1 = Task{"Go to work"}
                .add_stage("Wake up", []() { factorial(facn); })
                .add_stage("Get out of bed", []() { factorial(facn); })
                .add_stage("Brush teeth", []() { factorial(facn); })
                .add_stage("Eat", []() { factorial(facn); })
                .add_stage("Get out of the house", []() { factorial(facn); })
                .add_stage("Drive to work", []() { factorial(facn); })
                .add_stage("Greet everyone", []() { factorial(facn); })
                .add_stage("Sit at desk", []() { factorial(facn); })
                .complete_building();
        tasks.push_back(t1);
    }

    auto time_started = std::chrono::system_clock::now();
    PiplinedPipeline pipeline;
    pipeline.run(tasks);
    auto time_finished = std::chrono::system_clock::now();
    std::cout << "Pipeline completed in " << std::chrono::duration_cast<std::chrono::milliseconds>(time_finished - time_started).count() << " ms" << std::endl;
    return 0;
}
