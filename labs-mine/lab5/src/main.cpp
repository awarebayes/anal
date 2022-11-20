#include <iostream>
#include <vector>
#include <optional>
#include <thread>
#include "queue.h"


// guess number by hash.
// number is in range [0, n)
int find_key_by_hash(size_t target_hash, int max_n)
{
    while (true)
    {
        int number = rand() % max_n;
        size_t hash = std::hash<int>{}(number);
        if (hash == target_hash)
        {
            return number;
        }
    }
}

int work(int n)
{
    auto guess = rand() % n;
    size_t target_hash = std::hash<int>{}(guess);
    return find_key_by_hash(target_hash, n);
}

struct Stage
{
    std::string_view stage_name;
    std::function<void()> work_;
    int stage_number{};
    std::shared_ptr<Stage> next_stage{};

    void work()
    {
        // std::cout << "Stage: " << stage_number << " " << stage_name << " started" << std::endl;
        work_();
        // std::cout << "Stage: " << stage_number << " " << stage_name << " ended" << std::endl;
    }
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
    std::chrono::time_point<std::chrono::steady_clock> start_time{};
    std::chrono::time_point<std::chrono::steady_clock> end_time{};

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
        auto stages_0_original_work = stages[0]->work_;
        stages[0]->work_ = [this, stages_0_original_work](){
            this->start_time = std::chrono::steady_clock::now();
            // std::cout << "Task " << task_name << "started!" << std::endl;
            stages_0_original_work();
        };

        auto last_stages_original_work = stages[stages.size() - 1]->work_;
        stages[stages.size() - 1]->work_ = [this, last_stages_original_work](){
            last_stages_original_work();
            this->end_time = std::chrono::steady_clock::now();
            // std::cout << "Task " << task_name << " completed in " << std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count() << " ms" << std::endl;
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
        for (auto &queue : queues)
        {
            thread_pool.emplace_back([&queue, n_tasks]() {
                int tasks_completed = 0;
                while (tasks_completed < n_tasks)
                {
                    auto maybe_stage = queue->pop();
                    if (maybe_stage)
                    {
                        tasks_completed += 1;
                        auto& stage_with_cb = maybe_stage.value();
                        stage_with_cb.stage->work();
                        stage_with_cb.on_complete(*stage_with_cb.stage);
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

template<typename PipelineT>
void run_pipeline(const std::vector<Task> &tasks)
{
    PipelineT().run(tasks);
}

int main() {

    std::vector<size_t> sizes = {100, 200, 300, 500, 1000, 5000, 10'000, 20'000};
    std::vector<std::string> pipeline_type = {"Sequential", "Parallel"};

    std::cout << "Size,Sequential,Parallel" << std::endl;

    for (const auto &size: sizes)
    {
        std::vector<Task> tasks;
        for (int i = 0; i < size; i++)
        {
            const int job_difficulty = 50;
            auto t1 = Task{"Go to work"}
                    .add_stage("Wake up", [=]() { work(job_difficulty); })
                    .add_stage("Get out of bed", [=]() { work(job_difficulty); })
                    .add_stage("Brush teeth", [=]() { work(job_difficulty); })
                    .add_stage("Eat", [=]() { work(job_difficulty); })
                    .add_stage("Get out of the house", [=]() { work(job_difficulty); })
                    .add_stage("Drive to work", [=]() { work(job_difficulty); })
                    .add_stage("Greet everyone", [=]() { work(job_difficulty); })
                    .add_stage("Sit at desk", [=]() { work(job_difficulty); })
                    .complete_building();
            tasks.push_back(t1);
        }

        std::cout << tasks.size();
        for (const auto &pipe_t: pipeline_type)
        {
            auto time_started = std::chrono::steady_clock::now();
            if (pipe_t == "Sequential")
                run_pipeline<SequentialPipeline>(tasks);
            else
                run_pipeline<PiplinedPipeline>(tasks);
            auto time_finished = std::chrono::steady_clock::now();

            std::cout << "," << std::chrono::duration_cast<std::chrono::milliseconds>(time_finished - time_started).count();
        }
        std::cout << std::endl;
    }

    return 0;
}
