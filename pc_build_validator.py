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

# ---------- Input parsing helpers ----------
def safe_int(x):
    try:
        return int(x)
    except:
        return None

def main():
    data = []
    for line in sys.stdin:
        line = line.strip()
        if line == "":
            continue
        data.append(line)

    # If there's no input, exit gracefully
    if not data:
        print("Maximum Score: 0")
        print("Best Build: NONE")
        return

    idx = 0
    # Read budget
    try:
        budget = int(data[idx].split()[0])
    except Exception:
        # invalid budget -> no valid builds
        print("Maximum Score: 0")
        print("Best Build: NONE")
        return
    idx += 1

    # Number of components P
    if idx >= len(data):
        print("Maximum Score: 0")
        print("Best Build: NONE")
        return

    try:
        P = int(data[idx].split()[0])
    except Exception:
        print("Maximum Score: 0")
        print("Best Build: NONE")
        return
    idx += 1

    inventory = {}  # component_id -> Component

    for _ in range(P):
        if idx >= len(data):
            break
        # Each component line: component_id type performance_score cost spec_1 spec_2
        parts = data[idx].split()
        idx += 1
        # Validate minimum fields (should be 6)
        if len(parts) < 6:
            continue
        component_id = parts[0]
        ctype = parts[1]
        perf = safe_int(parts[2])
        cost = safe_int(parts[3])
        spec_1 = parts[4]
        spec_2 = parts[5]

        # If numeric fields are invalid, store but mark numbers as None -> will cause incompatibility or skip later
        if perf is None or cost is None:
            # skip invalid component lines (can't use them)
            continue

        comp = Component(component_id, ctype, perf, cost, spec_1, spec_2)
        inventory[component_id] = comp

    # Read number of kits K
    if idx >= len(data):
        K = 0
    else:
        try:
            K = int(data[idx].split()[0])
        except Exception:
            K = 0
        idx += 1

    kits = []
    for _ in range(K):
        if idx >= len(data):
            break
        parts = data[idx].split()
        idx += 1
        # Format: kit_id cpu_id motherboard_id gpu_id ram_id psu_id
        if len(parts) < 6:
            continue
        kit_id = parts[0]
        cpu_id = parts[1]
        mobo_id = parts[2]
        gpu_id = parts[3]
        ram_id = parts[4]
        psu_id = parts[5]
        kits.append((kit_id, cpu_id, mobo_id, gpu_id, ram_id, psu_id))

    # Evaluate each kit
    best_score = 0
    best_kit = "NONE"

    for kit in kits:
        kit_id, cpu_id, mobo_id, gpu_id, ram_id, psu_id = kit

        # Look up all components; if any missing -> invalid kit
        ids = [cpu_id, mobo_id, gpu_id, ram_id, psu_id]
        if not all(cid in inventory for cid in ids):
            continue

        # Build type mapping. Also check duplicates or wrong types.
        comps = {
            "CPU": inventory[cpu_id],
            "Motherboard": inventory[mobo_id],
            "GPU": inventory[gpu_id],
            "RAM": inventory[ram_id],
            "PSU": inventory[psu_id],
        }

        # Ensure each component is actually the expected type
        ok_types = True
        expected_map = {
            "CPU": "CPU",
            "Motherboard": "Motherboard",
            "GPU": "GPU",
            "RAM": "RAM",
            "PSU": "PSU",
        }
        for t, comp in comps.items():
            if comp.type != expected_map[t]:
                ok_types = False
                break
        if not ok_types:
            continue

        build = PCBuild(kit_id, comps)

        # cost check
        total_cost = build.total_cost()
        if total_cost > budget:
            continue

        # compatibility check
        if not build.is_compatible():
            continue

        # compute score
        score = build.total_performance()

        # tie-breaker: first encountered (we only replace if strictly greater)
        if score > best_score:
            best_score = score
            best_kit = kit_id

    print(f"Maximum Score: {best_score}")
    print(f"Best Build: {best_kit}")

if __name__ == "__main__":
    main()

'''
# Example Input:

1500
8
cpu_1 CPU 500 300 LGA1700 95
cpu_2 CPU 450 250 AM5 105
mobo_1 Motherboard 150 180 LGA1700 DDR5
mobo_2 Motherboard 140 160 AM5 DDR4
gpu_1 GPU 700 400 - 300
gpu_2 GPU 600 350 - 250
ram_1 RAM 100 80 DDR5 -
psu_1 PSU 50 100 750 -
3
kit_A cpu_1 mobo_1 gpu_1 ram_1 psu_1
kit_B cpu_2 mobo_2 gpu_1 ram_1 psu_1
kit_C cpu_1 mobo_1 gpu_2 ram_1 psu_1

'''