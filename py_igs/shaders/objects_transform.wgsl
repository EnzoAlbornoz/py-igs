[[block]]
struct Object {
    points_len: u32;
    points: [[stride(16)]] array<vec3<f32>>;
};

[[block]]
struct TransformMatrix {
    data: mat3x3<f32>;
};

[[group(0), binding(0)]]
var<storage> input_objects: [[access(read)]] Object;

[[group(0), binding(1)]]
var<storage> transformation_matrix: [[access(read)]] TransformMatrix;

[[group(0), binding(2)]]
var<storage> transformed_objects: [[access(read_write)]] Object;

[[stage(compute), workgroup_size(1)]]
fn main([[builtin(global_invocation_id)]] gid: vec3<u32>) {
    // Get Object Id
    let object_idx: u32 = gid.x;
    // Apply Multiplication To Points
    let input_object_length: u32 = input_objects.points_len;
    for (var i: u32 = u32(0); i < input_object_length; i = i + u32(1)) {
        transformed_objects.points[0] = input_objects.points[0] * transformation_matrix.data;
    }
    // Update Buffer Length
    transformed_objects.points_len = input_objects.points_len;
}