# Building Custom TensorFlow C++ Ops for Python 3.14t

## Overview
While TensorFlow itself cannot run on Python 3.14t (free-threaded), you CAN 
compile custom C++ ops against the TF headers and link them for use on 3.14t.
This requires the tf-nightly cp314 wheel to be installed on non-t Python 3.14.

## Prerequisites
- tf-nightly installed on Python 3.14 (non-t): `/usr/local/bin/python3.14 -m pip install tf-nightly`
- GCC 15.2.0 (or compatible C++ compiler)
- Python 3.14t development headers

## Get Compile and Link Flags from TF
```bash
export LD_LIBRARY_PATH=/usr/local/python314t-native/lib:$LD_LIBRARY_PATH
/usr/local/bin/python3.14 -c "
import tensorflow as tf
print('Include flags:', ' '.join(tf.sysconfig.get_compile_flags()))
print('Link flags:', ' '.join(tf.sysconfig.get_link_flags()))
print('Library dir:', tf.sysconfig.get_lib())
print('Include dir:', tf.sysconfig.get_include())
"
```

## Sample Makefile for Custom Op
```makefile
# Makefile for building TF custom ops
TF_CFLAGS := $(shell /usr/local/bin/python3.14 -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_compile_flags()))')
TF_LFLAGS := $(shell /usr/local/bin/python3.14 -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_link_flags()))')
PY_CFLAGS := $(shell /usr/local/python314t-native/bin/python3.14-config --includes)
PY_LFLAGS := $(shell /usr/local/python314t-native/bin/python3.14-config --ldflags 2>/dev/null)

all: zero_out.so zero_out_314t.so

# For Python 3.14t free-threaded
zero_out_314t.so: zero_out.cc
	g++ -std=c++17 -shared -fPIC \\
	  $(PY_CFLAGS) $(TF_CFLAGS) \\
	  -L/usr/local/python314t-native/lib \\
	  -o $@ $< $(TF_LFLAGS)

# For Python 3.14 non-free-threaded  
zero_out.so: zero_out.cc
	g++ -std=c++17 -shared -fPIC \\
	  $(shell /usr/local/bin/python3.14-config --includes) $(TF_CFLAGS) \\
	  -o $@ $< $(TF_LFLAGS)

clean:
	rm -f *.so
```

## Sample Custom Op (zero_out.cc)
```cpp
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/framework/shape_inference.h"

using namespace tensorflow;

REGISTER_OP("ZeroOut")
    .Input("to_zero: int32")
    .Output("zeroed: int32")
    .SetShapeFn([](shape_inference::InferenceContext* c) {
        c->set_output(0, c->input(0));
        return absl::Status::OK();
    });

class ZeroOutOp : public OpKernel {
 public:
    explicit ZeroOutOp(OpKernelConstruction* context) : OpKernel(context) {}

    void Compute(OpKernelContext* context) override {
        const Tensor& input_tensor = context->input(0);
        auto input = input_tensor.flat<int32>();
        Tensor* output_tensor = nullptr;
        OP_REQUIRES_OK(context, context->allocate_output(0, input_tensor.shape(), &output_tensor));
        auto output = output_tensor->flat<int32>();
        const int N = input.size();
        for (int i = 0; i < N; i++) {
            output(i) = (i == 0) ? input(0) : 0;
        }
    }
};

REGISTER_KERNEL_BUILDER(Name("ZeroOut").Device(DEVICE_CPU), ZeroOutOp);
```

## Python Usage
```python
import tensorflow as tf
zero_out_module = tf.load_op_library('./zero_out.so')
result = zero_out_module.zero_out([1, 2, 3, 4, 5])
print(result.numpy())  # Output: [1, 0, 0, 0, 0]
```

## Build Verification
```bash
# On non-t Python 3.14
cd /root/tf_custom_op_example
make zero_out.so
/usr/local/bin/python3.14 -c "
import tensorflow as tf
mod = tf.load_op_library('./zero_out.so')
print(mod.zero_out([1, 2, 3, 4, 5]).numpy())
"
```

## Key Limitations for 3.14t
- **⚠️ WARNING: This approach is THEORETICAL and likely won't work until TF itself is recompiled for cp314t.**
- TF Python extension modules (`_pywrap_tensorflow_internal.so`) still won't load on 3.14t
- `libtensorflow_framework.so` (from the cp314 install) depends on `libpython3.14.so.1.0`, not `libpython3.14t.so.1.0`. Loading into Python 3.14t will fail with missing symbol errors or ABI conflicts.
- Custom ops compiled for 3.14t link their Python parts against 3.14t's headers (different PyObject layout) but the TF runtime depends on non-t Python — these are fundamentally incompatible.
- Until TF provides official cp314t wheels, **prefer PyTorch which has native cp314t support** for all ML workloads on Python 3.14t.

## Reference: What Changed in Python 3.14t ABI
- PyObject struct gained `ob_tid` field (thread ID for free-threading)
- `ob_refcnt` became `ob_refcnt_shared` with different semantics
- `ob_type` moved to a different offset in the struct
- These cannot be fixed via LD_PRELOAD or binary patching — only a recompile with 3.14t headers works
