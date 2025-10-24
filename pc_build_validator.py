import sys

# ---------- Component classes ----------
class Component:
    def __init__(self, component_id, ctype, performance_score, cost, spec_1, spec_2):
        self.id = component_id
        self.type = ctype  # CPU, Motherboard, GPU, RAM, PSU
        self.performance = performance_score
        self.cost = cost
        self.spec1 = spec_1
        self.spec2 = spec_2

    def __repr__(self):
        return f"<{self.type} {self.id} perf={self.performance} cost={self.cost} s1={self.spec1} s2={self.spec2}>"
