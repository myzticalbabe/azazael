# azazael-autodiff-forward
**Category:** Algorithm / Automatic Differentiation
**Priority:** HIGH
**Dependencies:** mygrad>=2.3.0, numpy
**Created:** June 14, 2026
**Updated:** June 14, 2026 (fixed requires_grad API, dead code removal, jvp fallback)

## Purpose
Documents forward-mode automatic differentiation (AD) using `mygrad` — computing derivatives by propagating tangent values forward alongside primal values. Forward-mode excels at `f: R^n -> R^m` where `n` is small and `m` is large.

## When To Load
- Computing Jacobian-vector products (JVPs)
- When the function has more outputs than inputs (`m > n`)
- Directional derivatives along specific tangent vectors
- Newton's method requiring Hessian-vector products
- Sensitivity analysis of outputs to specific input perturbations

## mygrad 2.3.0 API Note
mygrad does NOT accept `requires_grad=True` as a kwarg to `mg.tensor()`. Set it after construction:
```python
x = mg.tensor(2.0)
x.requires_grad = True
```

## Core Patterns

### Pattern 1: Jacobian-Vector Product (JVP) via Directional Derivative
```python
import mygrad as mg
import numpy as np

def jvp(f, x, v):
    """Forward-mode Jacobian-vector product: J_f(x) @ v.

    For scalar f: JVP = grad · v (dot product of gradient and tangent).
    For vector f: compute each output's directional derivative.
    """
    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    v = np.asarray(v)

    # Determine output dimension
    x0 = mg.tensor(x)
    y0 = f(x0)
    m = len(y0.data) if hasattr(y0.data, '__len__') else 1

    if m == 1:
        # Scalar: JVP = df/dx · v
        xt = mg.tensor(x)
        xt.requires_grad = True
        yt = f(xt)
        yt.backward()
        return float(np.dot(xt.grad, v))

    # Vector-valued f: compute each output's sensitivity to v
    # NOTE: mygrad 2.3.0 limitation — .backward(seed) on vector outputs
    # may leave .grad as None. If so, fall back to finite differences.
    result = np.zeros(m)
    for i in range(m):
        xt = mg.tensor(x)
        xt.requires_grad = True
        yt = f(xt)
        seed = np.zeros(m)
        seed[i] = 1.0
        yt.backward(mg.tensor(seed))
        if xt.grad is None:
            # Fallback: finite-diff directional derivative for output i
            h = 1e-6
            y_plus = float(f(mg.tensor(x + h * v)).data[i])
            y_minus = float(f(mg.tensor(x - h * v)).data[i])
            result[i] = (y_plus - y_minus) / (2 * h)
        else:
            result[i] = float(np.dot(xt.grad, v))

    return result
```

### Pattern 2: Full Jacobian via Forward-Mode (efficient when n < m)
```python
def jacobian_forward(f, x):
    """Full Jacobian via forward-mode: seed each input with basis vector.

    For f: R^n -> R^m, runs n passes. Efficient when n < m.
    """
    x = np.asarray(x)
    n = len(x)

    # Determine output dimension
    y0 = f(mg.tensor(x))
    m = len(y0.data) if hasattr(y0.data, '__len__') else 1
    J = np.zeros((m, n))

    for j in range(n):
        e_j = np.zeros(n)
        e_j[j] = 1.0
        J[:, j] = jvp(f, x, e_j)

    return J
```

### Pattern 3: HVP via Finite Differences (Recommended for mygrad 2.3.0)

**IMPORTANT mygrad limitation:** After `.backward()`, `.grad` is a plain numpy array — it is DETACHED from the computational graph. You cannot call `.backward()` on an expression involving `.grad` to get second derivatives. Use finite differences on the gradient instead:

```python
def hvp(f, x, v, h=1e-6):
    """Hessian-vector product via central finite differences on gradient.

    H(x) @ v = (grad(x + h*v) - grad(x - h*v)) / (2*h)

    This is the reliable approach for mygrad 2.3.0 because .grad
    is numpy (detached) after backward(), preventing direct
    second-order AD.
    """
    x = np.asarray(x).astype(float)
    v = np.asarray(v).astype(float)

    def grad_fn(xv):
        xt = mg.tensor(xv)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        return np.array(xt.grad)

    return (grad_fn(x + h * v) - grad_fn(x - h * v)) / (2 * h)
```

## When Forward-Mode Beats Reverse-Mode

| Scenario | Forward | Reverse |
|----------|---------|---------|
| f: R^1 -> R^1000 | **O(1) pass** | O(1000) passes |
| f: R^1000 -> R^1 | O(1000) passes | **O(1) pass** |
| Directional derivative | **O(1)** | O(1) |
| Full Jacobian (n < m) | **O(n)** | O(m) |
| Full Jacobian (n > m) | O(n) | **O(m)** |

## Key mygrad Functions
- `mg.tensor(x)` then `.requires_grad = True` — differentiable tensor (NO kwarg)
- `tensor.backward(seed)` — backpropagate with optional seed vector
- `tensor.grad` — accumulated gradient as **numpy array** (detached from graph!)
- `tensor.null_grad()` — reset gradients between passes
- `mg.sum()`, `mg.dot()` — differentiable reductions
- `tensor.data` — raw numpy array value

## Reference
- Griewank & Walther, "Evaluating Derivatives" (2008) — forward-mode theory
- mygrad documentation: https://mygrad.readthedocs.io/
