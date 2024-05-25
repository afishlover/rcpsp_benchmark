class Helper:
    @staticmethod
    def suitable_worker(worker_skill, task_skill, num_of_tasks, num_of_workers, num_of_skills):
        suitable_workers = []
        for t in range(num_of_tasks):
            task_workers = []
            for w in range(num_of_workers):
                ok = True
                for s in range(num_of_skills):
                    if task_skill[t][s] > worker_skill[w][s]:
                        ok = False
                        break
                if ok:
                    task_workers.append(w)
            if len(task_workers) == 0:
                raise Exception("No Suitable Worker Was Found!")
            suitable_workers.append(task_workers)
        return suitable_workers

    @staticmethod
    def task_skill_by_worker(self, worker_skill, task_skill, num_of_tasks, num_of_workers, num_of_skills):
        task_skill = [[0] * num_of_workers for _ in range(num_of_tasks)]
        for t in range(num_of_tasks):
            for w in range(num_of_workers):
                ok = True
                skill_val = 0
                for s in range(num_of_skills):
                    if task_skill[t][s] > worker_skill[w][s]:
                        ok = False
                        break
                    elif task_skill[t][s] > 0:
                        skill_val += worker_skill[w][s]
                if ok:
                    task_skill[t][w] = skill_val
        return task_skill
