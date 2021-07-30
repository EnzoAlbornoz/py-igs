from array import array
from typing import Dict, List
from itertools import chain
from py_igs.primitives.matrix import Matrix, homo_coords2_matrix_translate
import struct
import wgpu.backends.rs # type: ignore
import wgpu
from wgpu.utils import get_default_device, compute_with_buffers
from time import perf_counter
from pathlib import Path
from functools import reduce

file = Path(__file__).parent.joinpath("./objects_transform.wgsl").resolve()
file_content = file.read_text()

adapter: wgpu.GPUAdapter = wgpu.request_adapter(canvas=None, power_preference="high-performance")
print(adapter.properties)


device: wgpu.GPUDevice = get_default_device()
list_array: List[float] = [3, 2, 1]
list_arrays = list_array * 100000
mult_mat: List[List[float]] = homo_coords2_matrix_translate(10, 15).columns()
lenper = len(list_array)
lenofperf = f"I{lenper}f"
matl = len(mult_mat) * len(mult_mat[0])
matlf = f"{matl}f"
perf = perf_counter()
for i in range(100000):
    multiplied_mat = Matrix([list_array]) * Matrix(mult_mat)
print(f"Mat Mul (Python): {1000 * (perf_counter() - perf)}ms")
mem_list_array = memoryview(struct.pack("I12x" + ("fff4x" * 100000), 100000, *list_arrays))
mem_mult_mat = memoryview(struct.pack("fff4xfff4xfff4x", *chain.from_iterable(mult_mat)))
perf = perf_counter()
out: Dict[int, memoryview] = compute_with_buffers({
    0: mem_list_array,
    1: mem_mult_mat,
}, {
    2: mem_list_array.nbytes
}, file_content, 1)
print(f"Mat Mul (GPU): {1000 * (perf_counter() - perf)}ms")
result = struct.unpack("I12x" + ("fff4x" * 100000), out[2])
# print(out[2].nbytes)
# print(mem_list_array.hex())
# print(out[2].hex())

# result.
# print(result)




# mem = memoryview(spack)
# unpacked = struct.unpack(lenofperf, mem)
# print(unpacked)

# ak2 = memoryview(array("f", [ak]))
# input_objects = memoryview(Matrix1x3(*[Array3(*[0, 0, 1])]))
# print(ak.shape)
# transformation_matrix = Matrix3x3(*[Array3(*[1,0,0]), Array3(*[0,1,0]), Array3(*[10,10,1])])

# print(transformation_matrix)