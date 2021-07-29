[[block]]
struct DataContainer {
    data: [[stride(4)]] array<i32>;
};

[[group(0), binding(0)]]
var<storage> data1: [[access(read)]] DataContainer;

[[group(0), binding(1)]]
var<storage> data2: [[access(write)]] DataContainer;

[[stage(compute), workgroup_size(1)]]
fn main([[builtin(global_invocation_id)]] index: vec3<u32>) {
    let i: u32 = index.x;
    data2.data[i] = data1.data[i];
}