from utils.problem import Problem

import random
class LocalSearch:
    def __init__(self, problem: Problem, max_iterations: int = 500, restarts: int = 10, seed: int = 42):
        self.problem = problem
        self.max_iterations = max_iterations
        self.restarts = restarts
        self.seed = seed
        random.seed(seed)
        self.visited: int = 0
        self.best_makespan: int = float("inf")
        self.best_sequence: tuple[int, ...] = ()
        
    def _sequence_makespan(self, sequence: tuple[int, ...]) -> int:
        state = self.problem.initial_state()
        try:
            for job in sequence:
                state = self.problem.dispatch(state, job)
            if self.problem.is_complete(state):
                return state.makespan()
        except Exception:
            pass
        return float("inf")
    
    def _generate_random_sequence(self) -> tuple[int, ...]:
        seq = []
        for job in range(self.problem.n_jobs):
            seq.extend([job] * self.problem.n_operations_per_job)
        random.shuffle(seq)
        return tuple(seq)

    def search(self) -> None:
        for _ in range(self.restarts):
            current_sequence = self._generate_random_sequence()
            current_makespan = self._sequence_makespan(current_sequence)
            self.visited += 1

            if current_makespan < self.best_makespan:
                self.best_makespan = current_makespan
                self.best_sequence = current_sequence

            improved = True
            iter_count = 0

            while improved and iter_count < self.max_iterations:
                improved = False
                iter_count += 1

                seq_list = list(current_sequence)
                n = len(seq_list)
                if n < 2:
                    break
                
                for _ in range(min(25, n * (n - 1) // 2)):
                    i, j = random.sample(range(n), 2)
                    seq_list[i], seq_list[j] = seq_list[j], seq_list[i]
                    neighbor_sequence = tuple(seq_list)
                    seq_list[i], seq_list[j] = seq_list[j], seq_list[i]

                    makespan = self._sequence_makespan(neighbor_sequence)
                    self.visited += 1

                    if makespan < current_makespan:
                        current_sequence = neighbor_sequence
                        current_makespan = makespan
                        improved = True

                        if current_makespan < self.best_makespan:
                            self.best_makespan = current_makespan
                            self.best_sequence = neighbor_sequence                            
                        break