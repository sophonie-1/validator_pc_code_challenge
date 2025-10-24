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

# ---------- PCBuild for compatibility checks ----------
class PCBuild:
    REQUIRED_TYPES = {"CPU", "Motherboard", "GPU", "RAM", "PSU"}

    def __init__(self, kit_id, components):
        """
        components: dict mapping type->Component
        """
        self.kit_id = kit_id
        self.components_by_type = components

    def all_types_present(self):
        return set(self.components_by_type.keys()) == self.REQUIRED_TYPES

    def total_cost(self):
        return sum(comp.cost for comp in self.components_by_type.values())

    def total_performance(self):
        return sum(comp.performance for comp in self.components_by_type.values())

    def is_compatible(self):
        # Requires all types present
        if not self.all_types_present():
            return False

        cpu = self.components_by_type["CPU"]
        mobo = self.components_by_type["Motherboard"]
        ram = self.components_by_type["RAM"]
        gpu = self.components_by_type["GPU"]
        psu = self.components_by_type["PSU"]

        # 1) CPU-Motherboard socket match (case-sensitive)
        cpu_socket = cpu.spec1  # CPU spec_1 is socket
        mobo_socket = mobo.spec1  # Motherboard spec_1 is socket
        if cpu_socket != mobo_socket:
            return False

        # 2) RAM-Motherboard type match (case-sensitive)
        ram_type = ram.spec1  # RAM spec_1 is RAM type
        mobo_ram_type = mobo.spec2  # Motherboard spec_2 is RAM type
        if ram_type != mobo_ram_type:
            return False

        # 3) PSU wattage sufficient: psu.wattage >= cpu.TDP + gpu.TDP + 50
        # Interpret CPU.spec2 as TDP, GPU.spec2 as TDP, PSU.spec1 as wattage
        try:
            cpu_tdp = int(cpu.spec2)
            gpu_tdp = int(gpu.spec2)
            psu_watt = int(psu.spec1)
        except Exception:
            # invalid (non-integer) numeric spec -> incompatible
            return False

        if psu_watt < (cpu_tdp + gpu_tdp + 50):
            return False

        return True
