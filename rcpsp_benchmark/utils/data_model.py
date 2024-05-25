from utils.helper import Helper


class DataModel:
    def __init__(self):
        self.max_salary = 0
        self.max_deadline = 0
        self.max_skill = 0
        self.skill_level = 10
        self.base_working_hour = 0
        self.num_of_tasks = 0
        self.num_of_workers = 0
        self.num_of_skills = 0
        self.deadline = 0
        self.budget = 0
        self.day_effort = 0
        self.max_skill = 0
        self.worker_salary = []
        self.task_duration = []
        self.worker_skill = []
        self.task_skill = []
        self.task_effort = []
        self.worker_daily_effort_float = []
        self.worker_daily_effort = []
        self.task_adjacency = []
        self.suitable_workers = []
        self.task_skill_by_worker = []
        self.weight1 = 0
        self.weight2 = 0
        self.weight3 = 0

    def populate_data(self, path):
        with open(path, 'r') as file:
            lines = file.readlines()
            
            self.day_effort = int(lines.pop(0).strip())
            self.num_of_tasks = int(lines.pop(0).strip())
            
            self.task_duration = []
            self.task_effort = []
            for t in range(self.num_of_tasks):
                duration = int(lines.pop(0).strip())
                self.task_duration.append(duration)
                self.task_effort.append(duration * self.day_effort)
            
            self.num_of_workers = int(lines.pop(0).strip())
            self.num_of_skills = int(lines.pop(0).strip())
            
            self.task_adjacency = [[0] * self.num_of_tasks for _ in range(self.num_of_tasks)]
            for t in range(self.num_of_tasks):
                self.task_adjacency[t] = list(map(int, lines.pop(0).strip().split()))
            
            self.worker_skill = [[0] * self.num_of_skills for _ in range(self.num_of_workers)]
            for w in range(self.num_of_workers):
                self.worker_skill[w] = list(map(int, lines.pop(0).strip().split()))
            
            self.task_skill = [[0] * self.num_of_skills for _ in range(self.num_of_tasks)]
            for t in range(self.num_of_tasks):
                self.task_skill[t] = list(map(int, lines.pop(0).strip().split()))
            
            self.worker_salary = list(map(int, lines.pop(0).strip().split()))
            self.deadline = int(lines.pop(0).strip())
            
            self.worker_daily_effort = [[0] * self.deadline for _ in range(self.num_of_workers)]
            self.worker_daily_effort_float = [[0.0] * self.deadline for _ in range(self.num_of_workers)]
            for w in range(self.num_of_workers):
                self.worker_daily_effort_float[w] = list(map(float, lines.pop(0).strip().split()))
                self.worker_daily_effort[w] = [int(effort * self.day_effort) for effort in self.worker_daily_effort_float[w]]
            
            self.budget = int(lines.pop(0).strip())
            
            self.suitable_workers = Helper.suitable_worker(self.task_skill, self.num_of_tasks, self.num_of_workers, self.num_of_skills)
            self.task_skill_by_worker = Helper.task_skill_by_worker(self.worker_skill, self.task_skill, self.num_of_tasks, self.num_of_workers, self.num_of_skills)
            
            self.max_skill = self.num_of_skills * self.num_of_tasks * self.skill_level
