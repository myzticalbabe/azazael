"""_ocl_ctypes -- minimal stdlib-only OpenCL binding for the iGPU examples.

No pyopencl, no numpy, no third-party wheel: pure ctypes against the
system OpenCL ICD loader (OpenCL.dll on Windows, libOpenCL.so on Linux).
Device selection is explicit: door 1 = GPU device, door 2 = CPU device.
Raises OclError (never silently degrades) when the loader, a platform,
or the requested device type is absent.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import platform as _platform


class OclError(RuntimeError):
    pass


def _load():
    names = []
    if _platform.system() == "Windows":
        names = ["OpenCL.dll"]
    else:
        found = ctypes.util.find_library("OpenCL")
        names = [found] if found else ["libOpenCL.so.1", "libOpenCL.so"]
    last = None
    for n in names:
        try:
            lib = ctypes.CDLL(n)
            lib._name = n
            return lib
        except OSError as e:
            last = e
    raise OclError(f"no OpenCL ICD loader found (tried {names}): {last}")


_lib = _load()

# --- types ---
_cl_platform_id = ctypes.c_void_p
_cl_device_id = ctypes.c_void_p
_cl_context = ctypes.c_void_p
_cl_command_queue = ctypes.c_void_p
_cl_program = ctypes.c_void_p
_cl_kernel = ctypes.c_void_p
_cl_mem = ctypes.c_void_p
_cl_int = ctypes.c_int32
_cl_uint = ctypes.c_uint32
_size_t = ctypes.c_size_t

CL_SUCCESS = 0
CL_DEVICE_TYPE_GPU = 1 << 2
CL_DEVICE_TYPE_CPU = 1 << 1
CL_DEVICE_TYPE_ALL = 0xFFFFFFFF
CL_MEM_READ_WRITE = 1 << 0
CL_MEM_WRITE_ONLY = 1 << 1
CL_MEM_READ_ONLY = 1 << 2
CL_MEM_COPY_HOST_PTR = 1 << 5
CL_PROGRAM_BUILD_LOG = 0x1183


def _check(code: int, what: str) -> None:
    if code != CL_SUCCESS:
        raise OclError(f"{what} failed: cl_int={code}")


def _fn(name, restype, *argtypes):
    f = getattr(_lib, name)
    f.restype = restype
    f.argtypes = list(argtypes)
    return f


_clGetPlatformIDs = _fn("clGetPlatformIDs", _cl_int, _cl_uint,
                        ctypes.POINTER(_cl_platform_id),
                        ctypes.POINTER(_cl_uint))
_clGetDeviceIDs = _fn("clGetDeviceIDs", _cl_int, _cl_platform_id,
                      ctypes.c_uint64, _cl_uint,
                      ctypes.POINTER(_cl_device_id),
                      ctypes.POINTER(_cl_uint))
_clCreateContext = _fn("clCreateContext", _cl_context,
                       ctypes.c_void_p, _cl_uint,
                       ctypes.POINTER(_cl_device_id),
                       ctypes.c_void_p, ctypes.c_void_p,
                       ctypes.POINTER(_cl_int))
_clCreateCommandQueue = _fn("clCreateCommandQueue", _cl_command_queue,
                            _cl_context, _cl_device_id, ctypes.c_uint64,
                            ctypes.POINTER(_cl_int))
_clCreateProgramWithSource = _fn(
    "clCreateProgramWithSource", _cl_program, _cl_context, _cl_uint,
    ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(_size_t),
    ctypes.POINTER(_cl_int))
_clBuildProgram = _fn("clBuildProgram", _cl_int, _cl_program, _cl_uint,
                      ctypes.POINTER(_cl_device_id), ctypes.c_char_p,
                      ctypes.c_void_p, ctypes.c_void_p)
_clGetProgramBuildInfo = _fn(
    "clGetProgramBuildInfo", _cl_int, _cl_program, _cl_device_id, _cl_uint,
    _size_t, ctypes.c_void_p, ctypes.POINTER(_size_t))
_clCreateKernel = _fn("clCreateKernel", _cl_kernel, _cl_program,
                      ctypes.c_char_p, ctypes.POINTER(_cl_int))
_clCreateBuffer = _fn("clCreateBuffer", _cl_mem, _cl_context, ctypes.c_uint64,
                      _size_t, ctypes.c_void_p, ctypes.POINTER(_cl_int))
_clSetKernelArg = _fn("clSetKernelArg", _cl_int, _cl_kernel, _cl_uint,
                      _size_t, ctypes.c_void_p)
_clEnqueueNDRangeKernel = _fn(
    "clEnqueueNDRangeKernel", _cl_int, _cl_command_queue, _cl_kernel,
    _cl_uint, ctypes.c_void_p, ctypes.POINTER(_size_t),
    ctypes.POINTER(_size_t), _cl_uint, ctypes.c_void_p, ctypes.c_void_p)
_clEnqueueReadBuffer = _fn(
    "clEnqueueReadBuffer", _cl_int, _cl_command_queue, _cl_mem, _cl_int,
    _size_t, _size_t, ctypes.c_void_p, _cl_uint, ctypes.c_void_p,
    ctypes.c_void_p)
_clEnqueueWriteBuffer = _fn(
    "clEnqueueWriteBuffer", _cl_int, _cl_command_queue, _cl_mem, _cl_int,
    _size_t, _size_t, ctypes.c_void_p, _cl_uint, ctypes.c_void_p,
    ctypes.c_void_p)
_clFinish = _fn("clFinish", _cl_int, _cl_command_queue)
_clReleaseMemObject = _fn("clReleaseMemObject", _cl_int, _cl_mem)
_clReleaseKernel = _fn("clReleaseKernel", _cl_int, _cl_kernel)
_clReleaseProgram = _fn("clReleaseProgram", _cl_int, _cl_program)
_clReleaseCommandQueue = _fn("clReleaseCommandQueue", _cl_int,
                             _cl_command_queue)
_clReleaseContext = _fn("clReleaseContext", _cl_int, _cl_context)
_clGetPlatformInfo = _fn("clGetPlatformInfo", _cl_int, _cl_platform_id,
                         _cl_uint, _size_t, ctypes.c_void_p,
                         ctypes.POINTER(_size_t))
_clGetDeviceInfo = _fn("clGetDeviceInfo", _cl_int, _cl_device_id, _cl_uint,
                       _size_t, ctypes.c_void_p, ctypes.POINTER(_size_t))

CL_PLATFORM_NAME = 0x0902
CL_DEVICE_NAME = 0x102B


def _info_string(fn, handle, param) -> str:
    n = _size_t(0)
    _check(fn(handle, param, 0, None, ctypes.byref(n)), "info-size")
    buf = ctypes.create_string_buffer(n.value)
    _check(fn(handle, param, n, buf, None), "info-read")
    return buf.value.decode("utf-8", "replace").strip("\x00").strip()


def platforms() -> list:
    n = _cl_uint(0)
    _check(_clGetPlatformIDs(0, None, ctypes.byref(n)), "clGetPlatformIDs(count)")
    if n.value == 0:
        return []
    arr = (_cl_platform_id * n.value)()
    _check(_clGetPlatformIDs(n, arr, None), "clGetPlatformIDs")
    return list(arr)


def platform_name(p) -> str:
    return _info_string(_clGetPlatformInfo, p, CL_PLATFORM_NAME)


def devices(platform, dtype=CL_DEVICE_TYPE_ALL) -> list:
    n = _cl_uint(0)
    rc = _clGetDeviceIDs(platform, dtype, 0, None, ctypes.byref(n))
    if rc != CL_SUCCESS or n.value == 0:
        return []
    arr = (_cl_device_id * n.value)()
    _check(_clGetDeviceIDs(platform, dtype, n, arr, None), "clGetDeviceIDs")
    return list(arr)


def device_name(d) -> str:
    return _info_string(_clGetDeviceInfo, d, CL_DEVICE_NAME)


class Context:
    """One device + context + queue + built program. Explicit close()."""

    def __init__(self, source: str, dtype=CL_DEVICE_TYPE_GPU):
        plats = platforms()
        if not plats:
            raise OclError("no OpenCL platforms")
        self.device = None
        self.platform = None
        for p in plats:
            ds = devices(p, dtype)
            if ds:
                self.platform, self.device = p, ds[0]
                break
        if self.device is None:
            want = "GPU" if dtype == CL_DEVICE_TYPE_GPU else "CPU"
            raise OclError(f"no {want} OpenCL device on any platform")
        err = _cl_int(0)
        devs = (_cl_device_id * 1)(self.device)
        self.ctx = _clCreateContext(None, 1, devs, None, None,
                                    ctypes.byref(err))
        _check(err.value, "clCreateContext")
        self.queue = _clCreateCommandQueue(self.ctx, self.device, 0,
                                           ctypes.byref(err))
        _check(err.value, "clCreateCommandQueue")
        src = ctypes.c_char_p(source.encode("utf-8"))
        srclen = _size_t(len(source.encode("utf-8")))
        self.program = _clCreateProgramWithSource(
            self.ctx, 1, ctypes.byref(src), ctypes.byref(srclen),
            ctypes.byref(err))
        _check(err.value, "clCreateProgramWithSource")
        rc = _clBuildProgram(self.program, 1, devs, None, None, None)
        if rc != CL_SUCCESS:
            log = self._build_log()
            raise OclError(f"clBuildProgram failed: cl_int={rc}\n{log}")
        self._bufs: list = []
        self._kernels: list = []

    def _build_log(self) -> str:
        n = _size_t(0)
        _clGetProgramBuildInfo(self.program, self.device,
                               CL_PROGRAM_BUILD_LOG, 0, None, ctypes.byref(n))
        if not n.value:
            return "<empty build log>"
        buf = ctypes.create_string_buffer(n.value)
        _clGetProgramBuildInfo(self.program, self.device,
                               CL_PROGRAM_BUILD_LOG, n, buf, None)
        return buf.value.decode("utf-8", "replace")

    def kernel(self, name: str):
        err = _cl_int(0)
        k = _clCreateKernel(self.program, name.encode("utf-8"),
                            ctypes.byref(err))
        _check(err.value, f"clCreateKernel({name})")
        self._kernels.append(k)
        return k

    def buffer(self, nfloats: int, host: list | None = None,
               flags=CL_MEM_READ_WRITE):
        nbytes = nfloats * 4
        err = _cl_int(0)
        if host is not None:
            arr = (ctypes.c_float * nfloats)(*host)
            buf = _clCreateBuffer(self.ctx, flags | CL_MEM_COPY_HOST_PTR,
                                  nbytes, arr, ctypes.byref(err))
        else:
            buf = _clCreateBuffer(self.ctx, flags, nbytes, None,
                                  ctypes.byref(err))
        _check(err.value, "clCreateBuffer")
        # Wrap in c_void_p so set_arg() can tell a buffer handle apart
        # from a plain int kernel argument (both are Python ints raw).
        wrapped = ctypes.c_void_p(buf)
        self._bufs.append(wrapped)
        return wrapped

    def set_arg(self, kernel, idx: int, value) -> None:
        if isinstance(value, ctypes.c_void_p):
            # Buffer handle: pass a pointer to the cl_mem-sized storage.
            _check(_clSetKernelArg(kernel, idx, ctypes.sizeof(value),
                                   ctypes.byref(value)),
                   f"clSetKernelArg({idx})")
        elif isinstance(value, float):
            c = ctypes.c_float(value)
            _check(_clSetKernelArg(kernel, idx, ctypes.sizeof(c),
                                   ctypes.byref(c)),
                   f"clSetKernelArg({idx})")
        else:  # plain int kernel argument
            c = _cl_int(int(value))
            _check(_clSetKernelArg(kernel, idx, ctypes.sizeof(c),
                                   ctypes.byref(c)),
                   f"clSetKernelArg({idx})")

    def launch(self, kernel, global_size: tuple) -> None:
        g = (_size_t * len(global_size))(*global_size)
        _check(_clEnqueueNDRangeKernel(self.queue, kernel, len(global_size),
                                       None, g, None, 0, None, None),
               "clEnqueueNDRangeKernel")
        _check(_clFinish(self.queue), "clFinish")

    def read_floats(self, buf, n: int) -> list:
        arr = (ctypes.c_float * n)()
        _check(_clEnqueueReadBuffer(self.queue, buf, 1, 0, n * 4, arr, 0,
                                    None, None),
               "clEnqueueReadBuffer")
        _check(_clFinish(self.queue), "clFinish(read)")
        return list(arr)

    def write_floats(self, buf, data: list) -> None:
        arr = (ctypes.c_float * len(data))(*data)
        _check(_clEnqueueWriteBuffer(self.queue, buf, 1, 0, len(data) * 4,
                                     arr, 0, None, None),
               "clEnqueueWriteBuffer")
        _check(_clFinish(self.queue), "clFinish(write)")

    def close(self) -> None:
        for k in self._kernels:
            _clReleaseKernel(k)
        for b in self._bufs:
            _clReleaseMemObject(b)
        _clReleaseProgram(self.program)
        _clReleaseCommandQueue(self.queue)
        _clReleaseContext(self.ctx)
        self._kernels.clear()
        self._bufs.clear()
