"""mcml_backend: flag default, selection, and opencl exactness."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed import mcml_backend as mb
from eve_unleashed.mcml import Dense


@pytest.fixture(autouse=True)
def _restore_flag():
    before = os.environ.get(mb.BACKEND_ENV)
    yield
    if before is None:
        os.environ.pop(mb.BACKEND_ENV, None)
    else:
        os.environ[mb.BACKEND_ENV] = before


def test_default_backend_is_cpu():
    os.environ.pop(mb.BACKEND_ENV, None)
    assert mb.backend_name() == "cpu"
    assert isinstance(mb.make_dense(4, 3, seed=1), Dense)


def test_unknown_backend_is_named_not_silent():
    os.environ[mb.BACKEND_ENV] = "cuda"
    with pytest.raises(ValueError, match="cpu\\|opencl"):
        mb.make_dense(4, 3, seed=1)


def test_opencl_without_pyopencl_raises_rather_than_falling_back():
    os.environ[mb.BACKEND_ENV] = "opencl"
    gpu = pytest.importorskip("eve_unleashed.mcml_gpu")
    if gpu.PYOPENCL_AVAILABLE:
        pytest.skip("pyopencl present; the refusal path is moot here")
    with pytest.raises(RuntimeError, match="pyopencl"):
        mb.make_dense(4, 3, seed=1)


def test_train_batch_learns_on_cpu():
    os.environ[mb.BACKEND_ENV] = "cpu"
    layer = mb.make_dense(3, 2, seed=9)
    xs = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.5, -0.5, 0.5]]
    ts = [[1.0, -1.0], [-1.0, 1.0], [0.0, 0.0]]
    first = mb.train_batch(layer, xs, ts, 0.05, steps=1)
    later = mb.train_batch(layer, xs, ts, 0.05, steps=80)
    assert later < first


def test_opencl_backend_matches_cpu_within_tolerance():
    os.environ[mb.BACKEND_ENV] = "opencl"
    try:
        mb.make_dense(8, 4, seed=2)
    except RuntimeError as e:
        pytest.skip(f"no opencl backend here: {e}")
    os.environ[mb.BACKEND_ENV] = "cpu"
    cpu = mb.make_dense(8, 4, seed=2)
    os.environ[mb.BACKEND_ENV] = "opencl"
    gpu = mb.make_dense(8, 4, seed=2)
    x = [0.1 * i for i in range(8)]
    a, b = cpu.forward(x), gpu.forward(x)
    assert max(abs(p - q) for p, q in zip(a, b)) <= 2e-5
