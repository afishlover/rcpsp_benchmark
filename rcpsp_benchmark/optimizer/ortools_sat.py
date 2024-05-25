from ortools.sat.python import cp_model
from utils.data_model import DataModel


class CPOrtools:
    def __init__(self, data_model: DataModel) -> None:
        # data model
        self.data_model = data_model

        # ortools
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # decision var
        self.task_worker = {}
        self.day_task = {}
        self.task_start = {}
        self.task_end = {}

        # objective

    def setup_problem(self):
        self.solver.parameters.num_search_workers = 2
        self.solver.parameters.enumerate_all_solutions = False
        self.solver.parameters.log_search_progress = True
        self.solver.parameters.cp_model_presolve = True
        self.solver.parameters.max_time_in_seconds = 300000
        self.solver.parameters.linearization_level = 0
        self.solver.parameters.subsolvers.append('no_lp')

        self.init_decision_var()
        self.one_worker_task_constraint()
        self.one_task_at_time_constraint()
        self.day_in_task_constraint()
        self.task_dependency_constraint()
        self.task_effort_constraint()
        self.init_objective_holders()

    def solve_problem(self):
        print("----Begin solving----")
        status = self.solver.solve(self.model)
        if status is cp_model.FEASIBLE or status is cp_model.OPTIMAL:
            for t in range(self.data_model.num_of_tasks):
                task_workers = self.data_model.suitable_workers[t]
                for w in task_workers:
                    if self.solver.value(self.task_worker[(t, w)]) == 1:
                        print(f"Task {t} is assign to worker {w}")

                print("Task" + str(t) + "start at" + str(self.solver.value(self.task_start[t])))
                print("Task" + str(t) + "end at" + str(self.solver.value(self.task_end[t])))

                days = []
                for d in range(self.data_model.deadline):
                    if self.solver.value(self.day_task[(t, d)]) == 1:
                        days.append(str(d))

                print("Task" + str(t) + "has days" + ", ".join(days))

    def init_objective_holders(self):
        # TotalTime
        total_time = self.model.NewIntVar(0, self.data_model.deadline, "TotalTime")
        time_list = [self.task_end[t] for t in range(self.data_model.num_of_tasks)]
        self.model.AddMaxEquality(total_time, time_list)
        self.model.Minimize(total_time)

    def init_decision_var(self):
        # Task assignee
        for t in range(self.data_model.num_of_tasks):
            task_workers = self.data_model.suitable_workers[t]
            for w in task_workers:
                self.task_worker[(t, w)] = self.model.NewBoolVar(f'A[{t}|{w}]')

        # Task start - end
        for t in range(self.data_model.num_of_tasks):
            self.task_start[t] = self.model.NewIntVar(0, self.data_model.deadline, f'TS[{t}]')
            self.task_end[t] = self.model.NewIntVar(0, self.data_model.deadline, f'TE[{t}]')

        # Day in task
        for t in range(self.data_model.num_of_tasks):
            for d in range(self.data_model.deadline):
                self.day_task[(t, d)] = self.model.NewBoolVar(f'K[{t}|{d}]')

    def one_worker_task_constraint(self):
        one_worker_task = []
        for t in range(self.data_model.num_of_tasks):
            task_workers = self.data_model.suitable_workers[t]
            for w in task_workers:
                one_worker_task.append(self.task_worker[(t, w)])
            self.model.AddExactlyOne(one_worker_task)
            one_worker_task.clear()

    def day_in_task_constraint(self):
        for t in range(self.data_model.num_of_tasks):
            list_days = []
            for d in range(self.data_model.deadline):
                self.model.Add(d >= self.task_start[t] - self.data_model.deadline * (1 - self.day_task[(t, d)]))
                self.model.Add(d <= self.task_end[t] + self.data_model.deadline * (1 - self.day_task[(t, d)]))
                list_days.append(self.day_task[(t, d)])

            self.model.Add(self.task_start[t] + cp_model.LinearExpr.sum(list_days) - 1 == self.task_end[t])

    def task_dependency_constraint(self):
        for t in range(self.data_model.num_of_tasks - 1):
            for t1 in range(t + 1, self.data_model.num_of_tasks):
                self.model.Add(
                    self.data_model.task_adjacency[t][t1] * (self.task_start[t1] - self.task_end[t] - 1) >= 0)

    def one_task_at_time_constraint(self):
        for w in range(self.data_model.num_of_workers):
            for t in range(self.data_model.num_of_tasks - 1):
                first_pool = self.data_model.suitable_workers[t]
                for t1 in range(t + 1, self.data_model.num_of_tasks):
                    second_pool = self.data_model.suitable_workers[t1]
                    if w in first_pool and w in second_pool:
                        first_part = self.model.NewIntVar(1, self.data_model.deadline, f'firstPart[{w}|{t}|{t1}]')
                        second_part = self.model.NewIntVar(1, self.data_model.deadline, f'secondPart[{w}|{t}|{t1}]')

                        self.model.AddMinEquality(first_part, [self.task_end[t], self.task_end[t1]])
                        self.model.AddMaxEquality(second_part, [self.task_start[t1], self.task_start[t]])

                        ind = self.model.NewBoolVar(f'both_indicator[{w}|{t}|{t1}]')

                        self.model.Add(self.task_worker[(t, w)] + self.task_worker[(t1, w)] == 2).OnlyEnforceIf(ind)
                        self.model.Add(self.task_worker[(t, w)] + self.task_worker[(t1, w)] < 2).OnlyEnforceIf(
                            ind.Not())
                        self.model.Add(first_part - second_part <= 0).OnlyEnforceIf(ind)

    def task_effort_constraint(self):
        for t in range(self.data_model.num_of_tasks):
            task_workers = self.data_model.suitable_workers[t]
            for w in task_workers:
                total_task_effort = []
                for d in range(self.data_model.deadline):
                    worker_task_effort = self.model.NewIntVar(0, self.data_model.day_effort,
                                                              f'workerTaskEffort[{t}|{w}|{d}]')
                    self.model.Add(
                        worker_task_effort == self.day_task[(t, d)] * self.data_model.worker_daily_effort[w][d])
                    total_task_effort.append(worker_task_effort)

                self.model.AddLinearConstraint(
                    cp_model.LinearExpr.sum(total_task_effort),
                    lb=self.data_model.task_effort[t],
                    ub=self.data_model.task_effort[t] + self.data_model.day_effort
                ).OnlyEnforceIf(self.task_worker[(t, w)])
