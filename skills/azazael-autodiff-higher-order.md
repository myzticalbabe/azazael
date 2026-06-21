# azazael-autodiff-higher-order
**Category:** Algorithm / Automatic Differentiation
**Priority:** HIGH
**Dependencies:** mygrad>=2.3.0, numpy, azazael-autodiff-backprop, azazael-autodiff-forward
**Created:** June 14, 2026
**Updated:** June 14, 2026 (fixed HVP via finite-diff, dead code removal, O(n^2) Hessian, corrected .grad-is-numpy limitation)

## Purpose
Documents techniques for computing higher-order derivatives — Jacobians, Hessians, and beyond — using `mygrad` automatic differentiation.

## When To Load
- When computing Hessians for second-order optimization (Newton's method)
- When analyzing curvature of loss landscapes
- When computing Jacobians for implicit differentiation
- When sensitivity analysis requires second-order terms
- When computing Hessian-vector products for conjugate gradient methods

## ⚠️ Critical mygrad 2.3.0 Limitation

After calling `tensor.backward()`, the `.grad` attribute is populated as a **plain numpy array** — it is DETACHED from the computational graph. This means you **cannot** differentiate through `.grad` directly:

```python
# This DOES NOT WORK for second-order:
y.backward()
d2 = mg.sum(x.grad * seed)  # x.grad is numpy — no gradient path back to x
d2.backward()  # computes d(constant)/dx = 0, not the HVP!
```

**Workaround:** Use finite differences on the gradient for second-order derivatives, or express the gradient as an explicit mygrad expression (not via `.backward()`).

### 1. Hessian-Vector Product (HVP) — Working Implementation

For large n, materializing O(n²) Hessian is infeasible. HVP computes `H @ v` in O(n):

```python
import mygrad as mg
import numpy as np

def hvp(f, x, v, h=1e-6):
    """Hessian-vector product via central finite differences on gradient.

    H(x) @ v = (grad_f(x + h*v) - grad_f(x - h*v)) / (2*h)

    This is the reliable approach for mygrad 2.3.0 because .grad
    is numpy (detached) after .backward(), preventing direct
    second-order AD through the gradient.

    Args:
        f: scalar function f: R^n -> R
        x: point to evaluate at (numpy array)
        v: tangent vector (numpy array)
        h: finite difference step size

    Returns:
        Hv: Hessian-vector product (numpy array, same shape as x)
    """
    x = np.asarray(x).astype(float)
    v = np.asarray(v).astype(float)

    def grad_fn(x_vals):
        xt = mg.tensor(x_vals)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        return np.array(xt.grad)

    return (grad_fn(x + h * v) - grad_fn(x - h * v)) / (2 * h)
```

### 2. Hessian Diagonal (Element-wise Second Derivatives)

```python
def hessian_diagonal(f, x, h=1e-6):
    """Diagonal of Hessian: H[i,i] = d^2f/dx_i^2.

    Uses central finite differences on each gradient component.
    """
    x = np.asarray(x).astype(float)
    n = len(x)
    H_diag = np.zeros(n)

    def ith_grad(x_vals, i):
        xt = mg.tensor(x_vals)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        return float(xt.grad[i])

    for i in range(n):
        e_i = np.zeros(n)
        e_i[i] = h
        H_diag[i] = (ith_grad(x + e_i, i) - ith_grad(x - e_i, i)) / (2 * h)

    return H_diag
```

### 3. Full Hessian — Finite Difference on Gradient

For scalar `f: R^n -> R`, the Hessian can't be computed directly via mygrad's `.backward()` because `.grad` is detached numpy. Use central finite differences on each gradient component:

```python
def hessian(f, x, h=1e-6):
    """Full Hessian via finite differences on gradient.

    H[i,j] = d^2f/(dx_i dx_j) = d(df/dx_i)/dx_j

    Computes df/dx_i at x + h*e_j and x - h*e_j for each (i,j),
    using central finite differences. O(n^2) gradient evaluations.

    For small n (< 100), this is practical. For large n, use hvp() instead.
    """
    x = np.asarray(x).astype(float)
    n = len(x)
    H = np.zeros((n, n))

    def ith_grad(x_vals, i):
        """Compute df/dx_i at x_vals."""
        xt = mg.tensor(x_vals)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        return float(xt.grad[i])

    for i in range(n):
        for j in range(n):
            e_j = np.zeros(n)
            e_j[j] = h
            H[i, j] = (ith_grad(x + e_j, i) - ith_grad(x - e_j, i)) / (2 * h)

    return H
```

**Why not seeded passes?** In mygrad 2.3.0, `y.backward(seed)` on a scalar `y` doesn't accept vector `seed` — the seed must match output shape (scalar). And even for vector-valued `f`, `.grad` is detached numpy after backward. Finite differences are the reliable approach.

### 4. Full Jacobian (Vector-Valued Functions)

For `f: R^n -> R^m`, compute J with m seeded backward passes:

```python
def jacobian(f, x):
    """Full Jacobian via seeded backward, with finite-diff fallback.

    Fast path: m seeded backward passes (O(m) evaluations).
    Fallback: central finite differences on f directly (O(2n) evaluations)
    when mygrad 2.3.0 seeded backward returns None.grad on vector outputs.
    """
    x = np.asarray(x).astype(float)

    # Determine output dimension
    y0 = f(mg.tensor(x))
    m = len(y0.data) if hasattr(y0.data, '__len__') else 1
    n = len(x)
    J = np.zeros((m, n))

    # Try seeded backward first (fast path)
    for i in range(m):
        xt = mg.tensor(x)
        xt.requires_grad = True
        y = f(xt)

        seed = np.zeros(m)
        seed[i] = 1.0
        y.backward(mg.tensor(seed))

        if xt.grad is None:
            # Fallback to finite differences — always works
            h = 1e-6
            for j in range(n):
                e_j = np.zeros(n); e_j[j] = h
                y_plus = np.array(f(mg.tensor(x + e_j)).data)
                y_minus = np.array(f(mg.tensor(x - e_j)).data)
                J[:, j] = (y_plus - y_minus) / (2 * h)
            return J

        J[i, :] = np.array(xt.grad)
    return J
```

### 5. Gauss-Newton Step (Second-Order for Least Squares)

For `f(x) = (1/2)||r(x)||^2`: approximate Hessian as `J_r^T @ J_r`:

```python
def gauss_newton_step(r, x, damping=1e-6):
    """Gauss-Newton step for min_x (1/2)||r(x)||^2.

    H_GN = J^T @ J   (no second derivatives of r needed)
    delta = -H_GN^{-1} @ grad

    Args:
        r: residual function r: R^n -> R^m
        x: current point
        damping: Levenberg-Marquardt damping for stability
    """
    x = np.asarray(x).astype(float)
    J = jacobian(r, x)
    residuals = np.array(r(mg.tensor(x)).data)
    grad = J.T @ residuals
    H_gn = J.T @ J + damping * np.eye(len(x))
    delta = np.linalg.solve(H_gn, -grad)
    return delta
```

### 6. Higher-Order Derivatives (Scalar f: R -> R)

For higher-order derivatives, the best approach in mygrad is to express each derivative explicitly as a mygrad computation (when the derivative form is known), or use finite differences with awareness of error accumulation:

```python
def derivative(f, x, order=1, h=1e-5):
    """Nth derivative of scalar f: R -> R.

    Order 0: direct evaluation.
    Order 1: exact gradient via mygrad .backward().
    Order 2: central finite diff on gradient.
    Order 3+: use larger h to combat error accumulation. NOT reliable
             beyond order 3 — use explicit derivative formulas instead.

    Example:
        derivative(lambda x: x**5, 2.0, order=2) -> 160.0  (f''(2) = 20*8)
        derivative(lambda x: x**5, 2.0, order=3) -> ~240.0  (f'''(2) = 60*4)
    """
    x = float(x)

    if order == 0:
        return float(f(mg.tensor(x)).data)

    if order == 1:
        xt = mg.tensor(x)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        return float(xt.grad)

    if order == 2:
        # Central finite diff on gradient: (f'(x+h) - f'(x-h)) / (2h)
        def grad_at(t):
            xt = mg.tensor(float(t))
            xt.requires_grad = True
            y = f(xt)
            y.backward()
            return float(xt.grad)
        return (grad_at(x + h) - grad_at(x - h)) / (2 * h)

    # Order 3: central diff on second derivative (error compounds quickly)
    # Use larger h to reduce numerical noise
    h3 = h * 10  # wider step for higher orders
    def d2_at(t):
        return derivative(f, t, order=2, h=h / 2)  # tighter h for inner
    return (d2_at(x + h3) - d2_at(x - h3)) / (2 * h3)
```

**For order >= 4, use explicit formulas:** instead of recursive AD, compute the derivative analytically and express it as a mygrad computation:

```python
# Example: f(x) = x^4, compute f''''(x)
# Analytically: f''''(x) = 24 for all x
# In mygrad, differentiate the 3rd-derivative expression:
x = mg.tensor(2.0)
x.requires_grad = True
g3 = 24 * x  # third derivative: f'''(x) = 24x
g3.backward()  # fourth derivative: f''''(x) = 24
print(x.grad)  # 24.0
```

### 7. Newton Step via Conjugate Gradient (No Explicit Hessian)

For large n, use CG with HVP oracle to solve `H @ delta = -grad`:

```python
def newton_step_cg(f, x, max_cg_iters=50, tol=1e-6, h=1e-6):
    """Newton step via conjugate gradient — no explicit Hessian.

    Solves H(x) @ delta = -grad(x) using CG with finite-diff HVP oracle.
    Memory: O(n). Works for any n.
    """
    x = np.asarray(x).astype(float)
    n = len(x)

    # Compute gradient
    xt = mg.tensor(x)
    xt.requires_grad = True
    y = f(xt)
    y.backward()
    grad = np.array(xt.grad)

    # Conjugate gradient: solve H @ d = -grad using HVP oracle
    d = np.zeros(n)
    r = -grad.copy()
    p = r.copy()
    r_dot_r = np.dot(r, r)

    for _ in range(max_cg_iters):
        Hp = hvp(f, x, p, h=h)
        p_Hp = np.dot(p, Hp)

        if abs(p_Hp) < 1e-12:
            break

        alpha = r_dot_r / p_Hp
        d += alpha * p
        r -= alpha * Hp
        new_r_dot_r = np.dot(r, r)

        if np.sqrt(new_r_dot_r) < tol:
            break

        beta = new_r_dot_r / r_dot_r
        p = r + beta * p
        r_dot_r = new_r_dot_r

    return d
```

### 8. Newton's Method (Full Optimization Loop)

```python
def newton_optimize(f, x0, max_iter=100, tol=1e-6, method='cg'):
    """Newton's method for min_x f(x) with line search.

    Args:
        f: scalar function f: R^n -> R
        x0: initial point
        method: 'cg' (conjugate gradient, O(n) memory) or 'full' (explicit Hessian)

    Returns:
        x_opt, history
    """
    x = np.asarray(x0).astype(float)
    history = [x.copy()]

    for iteration in range(max_iter):
        # Gradient
        xt = mg.tensor(x)
        xt.requires_grad = True
        y = f(xt)
        y.backward()
        grad = np.array(xt.grad)

        if np.max(np.abs(grad)) < tol:
            break

        # Newton direction
        if method == 'cg':
            delta = newton_step_cg(f, x, h=1e-6)
        else:
            H = hessian(f, x)
            delta = np.linalg.solve(H, -grad)

        # Backtracking line search
        alpha = 1.0
        fx = float(f(mg.tensor(x)).data)
        for _ in range(20):
            x_new = x + alpha * delta
            f_new = float(f(mg.tensor(x_new)).data)
            if f_new < fx:
                break
            alpha *= 0.5

        x = x + alpha * delta
        history.append(x.copy())

    return x, history
```

## Complexity Comparison

| Operation | Time | Memory | mygrad Feasible? |
|-----------|------|--------|-----------------|
| Gradient (reverse) | O(n) | O(n) | ✅ .backward() |
| **HVP** (finite diff on grad) | **O(n)** | **O(n)** | ✅ |
| Full Hessian (seeded passes) | O(n²) | O(n²) | ✅ |
| Hessian diagonal (finite diff) | O(n) | O(n) | ✅ |
| Gauss-Newton Hessian | O(mn) | O(n²) | ✅ |
| Jacobian (seeded passes) | O(mn) | O(mn) | ✅ |
| nth derivative (scalar R->R) | O(n) recursive | O(n) | ✅ |

## Key mygrad Functions
- `mg.tensor(x)` then `.requires_grad = True` — differentiable input
- `tensor.backward(seed)` — seed with basis vector for partial derivatives
- `tensor.grad` — **numpy array** (detached from graph) after backward
- `tensor.data` — raw numpy values (break gradient tracking)
- `mg.tensor(seed)` — create seed/tangent vectors
- `mg.linalg.solve()` — solve linear systems

## Reference
- Pearlmutter, "Fast Exact Multiplication by the Hessian" (1994) — HVP via R-operator
- Martens, "Deep learning via Hessian-free optimization" (2010) — CG + HVP
- Nocedal & Wright, "Numerical Optimization" — Newton, Gauss-Newton, quasi-Newton
