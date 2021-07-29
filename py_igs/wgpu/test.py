import wgpu.backends.rs # type: ignore
import wgpu

adapter: wgpu.GPUAdapter = wgpu.request_adapter(
    canvas=None,
    power_preference="high-performance"
) # pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false


print(adapter.features)
# device: wgpu.GPUDevice = GPU.request_adapter()

# print(device)