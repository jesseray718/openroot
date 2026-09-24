import ctypes
import os
import time

class StateNode(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("_pad", ctypes.c_uint32),
        ("energy", ctypes.c_int64),
        ("mass", ctypes.c_uint64),
        ("entropy", ctypes.c_uint64)
    ]

class FluxQuantum(ctypes.Structure):
    _fields_ = [
        ("delta_energy", ctypes.c_int64),
        ("delta_mass", ctypes.c_uint64),
        ("generated_entropy", ctypes.c_uint64)
    ]

# Load compiled shared library
lib_path = os.path.abspath("./libthermo.so")
thermo_lib = ctypes.CDLL(lib_path)

# Configure C-ABI signature
thermo_lib.openroot_execute_0d_transition.argtypes = [
    ctypes.POINTER(StateNode),
    ctypes.POINTER(StateNode),
    ctypes.POINTER(FluxQuantum)
]
thermo_lib.openroot_execute_0d_transition.restype = ctypes.c_uint8

# Setup Nodes
src = StateNode(id=1, _pad=0, energy=50_000_000_000, mass=20_000_000, entropy=0)
dst = StateNode(id=2, _pad=0, energy=0, mass=0, entropy=0)
flux = FluxQuantum(delta_energy=1_000, delta_mass=1, generated_entropy=693)

iterations = 1_000_000
print(f"Executing {iterations:,} C++ 0D transitions via Python C-FFI...")

start = time.perf_counter()
for _ in range(iterations):
    res = thermo_lib.openroot_execute_0d_transition(ctypes.byref(src), ctypes.byref(dst), ctypes.byref(flux))
    if res != 0:
        raise RuntimeError(f"Transition failed with code {res}")
end = time.perf_counter()

elapsed = end - start
ops_sec = iterations / elapsed

print("========================================================")
print("PYTHON -> C++20 NATIVE THERMO ENGINE TEST RESULT")
print("========================================================")
print(f"Total Ops:           {iterations:,}")
print(f"Elapsed Time:        {elapsed:.4f} sec")
print(f"Throughput:          {ops_sec/1e6:.2f} Million ops/sec")
print(f"Final Src Energy:    {src.energy} nJ")
print(f"Final Dst Energy:    {dst.energy} nJ")
print(f"Dst Entropy:         {dst.entropy} micro-kB")
print("========================================================")
