from array import array
from typing import Dict, List
from itertools import chain
from py_igs.primitives.matrix import Matrix, homo_coords2_matrix_translate
import struct
import wgpu.backends.rs # type: ignore
import wgpu
from wgpu.utils import get_default_device, compute_with_buffers
from time import perf_counter, perf_counter_ns
from pathlib import Path
from functools import reduce

file = Path(__file__).parent.joinpath("./objects_transform.wgsl").resolve()
file_content = file.read_text()
device: wgpu.GPUDevice = get_default_device()
list_array: List[float] = [3, 2, 1]
mult_mat: List[List[float]] = homo_coords2_matrix_translate(10, 15).columns()
lenper = len(list_array)
lenofperf = f"I{lenper}f"
matl = len(mult_mat) * len(mult_mat[0])
matlf = f"{matl}f"
# perf = perf_counter_ns()
# multiplied_mat = Matrix([list_array]) * Matrix(mult_mat)
# print(f"Mat Mul (Python): {perf_counter_ns() - perf}ns")
print(list(chain.from_iterable(mult_mat)))
print(list_array)
mem_list_array = memoryview(struct.pack("I12xfff4x", 1, *list_array))
mem_mult_mat = memoryview(struct.pack("fff4xfff4xfff4x", *chain.from_iterable(mult_mat)))
out: Dict[int, memoryview] = compute_with_buffers({
    0: mem_list_array,
    1: mem_mult_mat,
}, {
    2: 32
}, file_content, 1)
print(out[2].nbytes)
print(mem_list_array.hex())
print(out[2].hex())

result = struct.unpack("I12xfff4x", out[2])
# result.
print(result)




# mem = memoryview(spack)
# unpacked = struct.unpack(lenofperf, mem)
# print(unpacked)

# ak2 = memoryview(array("f", [ak]))
# input_objects = memoryview(Matrix1x3(*[Array3(*[0, 0, 1])]))
# print(ak.shape)
# transformation_matrix = Matrix3x3(*[Array3(*[1,0,0]), Array3(*[0,1,0]), Array3(*[10,10,1])])

# print(transformation_matrix)