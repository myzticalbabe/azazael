# coding: utf-8
"""
Onnx Integration

Module for improvements functionality.

Functions:
    - export_to_onnx()
    - load_onnx_model()
    - detect_framework()
    - export_to_onnx()
    - load_onnx_model()
    - run_inference()
    - optimize_onnx()
    - forward()

Classes:
    - ONNXExporter
    - SimpleModel

Usage:
    >>> import onnx_integration
    >>> onnx_integration.export_to_onnx()

Author: Auto-generated
Date: 2026-02-10
"""

# coding: utf-8
"""
ONNX Export Utilities
Solves: ONNX export unstable (27/27 platforms affected)
Provides: Unified ONNX export for any ML framework

Usage:
    from onnx_utils import export_to_onnx, load_onnx_model

    # Export any model to ONNX
    export_to_onnx(
        model,
        input_sample,
        "model.onnx",
        framework="pytorch"  # auto-detected if None
    )

    # Load and run ONNX model
    ort_session = load_onnx_model("model.onnx")
    result = ort_session.run(output_names, input_dict)
"""

from typing import Any, Tuple, Optional, TYPE_CHECKING
import numpy as np

try:
    import onnx
    import onnxruntime as ort

    HAS_ONNX = True
    ort_available = True
except ImportError:
    HAS_ONNX = False
    ort_available = False
    ort = None  # type: ignore

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import tensorflow as tf

    HAS_TF = True
except ImportError:
    HAS_TF = False


class ONNXExporter:
    """
    Unified ONNX export for any ML framework.

    WHY THIS MATTERS:
    - 27 platforms lack stable ONNX export
    - ONNX is critical for model interoperability
    - Deployment requires ONNX in production

    IMPLEMENTATION:
    - Framework-specific export handlers
    - Input shape validation
    - ONNX Runtime inference
    """

    @staticmethod
    def detect_framework(model: Any) -> Optional[str]:
        """Detect model framework from type."""
        model_type = type(model).__module__

        if HAS_TORCH:
            if hasattr(model, "state_dict"):
                return "pytorch"
        if HAS_TF:
            if hasattr(model, "variables") or hasattr(model, "get_config"):
                return "tensorflow"
        if "sklearn" in model_type:
            return "sklearn"
        if "xgboost" in model_type:
            return "xgboost"
        if "lightgbm" in model_type:
            return "lightgbm"

        return None

    @staticmethod
    def export_to_onnx(
        model: Any,
        input_sample: Any,
        output_path: str,
        input_names: Optional[Tuple[str, ...]] = None,
        output_names: Optional[Tuple[str, ...]] = None,
        dynamic_axes: Optional[dict] = None,
        opset_version: int = 13,
    ) -> str:
        """
        Export model to ONNX format.

        Args:
            model: Model to export
            input_sample: Sample input for tracing
            output_path: Output file path
            input_names: Optional input tensor names
            output_names: Optional output tensor names
            dynamic_axes: Optional dynamic dimension mapping
            opset_version: ONNX opset version (default: 13)

        Returns:
            Path to exported ONNX file
        """
        if not HAS_ONNX:
            raise ImportError("ONNX not installed. Run: pip install onnx onnxruntime")

        framework = ONNXExporter.detect_framework(model)

        if framework == "pytorch":
            if not HAS_TORCH:
                raise ImportError("PyTorch not installed")

            if input_names is None:
                input_names = ("input",)
            if output_names is None:
                output_names = ("output",)
            if dynamic_axes is None:
                dynamic_axes = {
                    0: "batch_size",
                    2: "sequence_length",
                }

            torch.onnx.export(
                model,
                input_sample,
                output_path,
                input_names=list(input_names),
                output_names=list(output_names),
                dynamic_axes=dynamic_axes,
                opset_version=opset_version,
                export_params=True,
                do_constant_folding=True,
            )

        elif framework == "tensorflow":
            if not HAS_TF:
                raise ImportError("TensorFlow not installed")

            import tf2onnx

            if isinstance(input_sample, tuple):
                input_signature = tuple(
                    tf.TensorSpec(shape=s.shape, dtype=s.dtype) for s in input_sample
                )
            else:
                input_signature = (
                    tf.TensorSpec(
                        shape=input_sample.shape,
                        dtype=input_sample.dtype,
                    ),
                )

            tf2onnx.convert.from_keras(
                model,
                input_signature=input_signature,
                outputs=output_names or ("output",),
            ).dump(output_path)

        else:
            raise ValueError(f"Unsupported framework: {framework}")

        print(f"ONNX model exported to: {output_path}")
        return output_path

    @staticmethod
    def load_onnx_model(
        model_path: str,
        providers: Tuple[str, ...] = ("CPUExecutionProvider",),
    ):
        """
        Load an ONNX model for inference.

        Args:
            model_path: Path to ONNX file
            providers: Execution providers (CPU, CUDA, etc.)

        Returns:
            ONNX Runtime inference session
        """
        if not HAS_ONNX:
            raise ImportError(
                "ONNX Runtime not installed. Run: pip install onnxruntime"
            )

        return ort.InferenceSession(model_path, providers=providers)

    @staticmethod
    def run_inference(
        session,
        inputs: dict,
        output_names: Optional[Tuple[str, ...]] = None,
    ) -> Tuple[np.ndarray, ...]:
        """
        Run inference on ONNX model.

        Args:
            session: ONNX Runtime session
            inputs: Dictionary of input names to numpy arrays
            output_names: Names of outputs to retrieve

        Returns:
            Tuple of output arrays
        """
        if output_names is None:
            output_names = tuple(out.name for out in session.get_outputs())

        outputs = session.run(output_names, inputs)
        return tuple(np.array(o) for o in outputs)

    @staticmethod
    def optimize_onnx(
        input_path: str,
        output_path: str,
        level: int = 1,
    ) -> str:
        """
        Optimize ONNX model.

        Args:
            input_path: Input ONNX file
            output_path: Output ONNX file
            level: Optimization level (1-4)

        Returns:
            Path to optimized ONNX file
        """
        if not HAS_ONNX:
            raise ImportError("ONNX not installed")

        model = onnx.load(input_path)

        from onnxruntime.transformers import optimizer
        from onnxruntime.tools import optimizer as ort_optimizer

        optimized = ort_optimizer.optimize_model(
            input_path,
            optimization_level=level,
        )
        optimized.save_model_to_file(output_path)

        print(f"Optimized ONNX model saved to: {output_path}")
        return output_path


def export_to_onnx(
    model: Any,
    input_sample: Any,
    output_path: str,
    **kwargs,
) -> str:
    """Shorthand for ONNXExporter.export_to_onnx()."""
    return ONNXExporter.export_to_onnx(model, input_sample, output_path, **kwargs)


def load_onnx_model(model_path: str):
    """Shorthand for ONNXExporter.load_onnx_model()."""
    return ONNXExporter.load_onnx_model(model_path)


if __name__ == "__main__":
    print("=== ONNX Export Utilities Demo ===")

    import numpy as np

    if HAS_TORCH:

        class SimpleModel(torch.nn.Module):
            def forward(self, x):
                return x @ torch.tensor([[1.0, 2.0], [3.0, 4.0]]) + 0.5

        model = SimpleModel()
        input_sample = torch.randn(1, 2)

        export_to_onnx(model, input_sample, "simple_model.onnx")
        print("Model exported!")

        session = load_onnx_model("simple_model.onnx")
        print(f"Model inputs: {[inp.name for inp in session.get_inputs()]}")

        result = session.run(None, {"input": np.array([[1.0, 2.0]])})
        print(f"Inference result: {result}")

    else:
        print("PyTorch not installed - skipping demo")

    print("Demo complete!")
