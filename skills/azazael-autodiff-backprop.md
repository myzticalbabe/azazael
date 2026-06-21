# azazael-autodiff-backprop
**Category:** Algorithm / Automatic Differentiation
**Priority:** HIGH
**Dependencies:** mygrad>=2.3.0, numpy
**Created:** June 14, 2026

## Purpose
Documents reverse-mode automatic differentiation (back-propagation) using `mygrad` — the primary AD mode where gradients flow backward from outputs to inputs through the computational graph. Reverse-mode excels at functions `f: R^n -> R^m` where `n` is large and `m` is small (many inputs, few outputs — e.g., neural network loss functions).

## When To Load
- When computing gradients of scalar loss functions with respect to many parameters
- When training neural networks (the canonical backprop use case)
- When the function has more inputs than outputs (`n > m`)
- When computing full gradients of scalar-valued functions
- When implementing any gradient-based optimizer (SGD, Adam, RMSprop, etc.)

## Core Algorithm: Reverse-Mode AD via Computational Graph

mygrad's `Tensor.backward()` is the canonical reverse-mode implementation. It builds a dynamic computational graph during the forward pass, then traverses it in reverse topological order during `.backward()`, applying the chain rule at each node.

**API note (mygrad 2.3.0):** `mg.tensor()` does NOT accept `requires_grad=True` as a kwarg. Set it after construction:
```python
x = mg.tensor(2.0)
x.requires_grad = True
```

### Pattern 1: Basic Scalar Gradient
```python
import mygrad as mg
import numpy as np

# Simple scalar function: f(x) = sin(x^2)
x = mg.tensor(2.0)
x.requires_grad = True
y = mg.sin(x ** 2)          # forward pass builds graph
y.backward()                # reverse pass: df/dx = cos(x^2) * 2x
print(x.grad)               # cos(4) * 4 = -2.614...
```

### Pattern 2: Multi-Variable Gradient (Vector-Jacobian Product)
```python
# f(x, y, z) = x*y + exp(z)
x = mg.tensor(3.0); x.requires_grad = True
y = mg.tensor(4.0); y.requires_grad = True
z = mg.tensor(1.0); z.requires_grad = True

loss = x * y + mg.exp(z)
loss.backward()

print(f"df/dx = {x.grad}")  # y = 4.0
print(f"df/dy = {y.grad}")  # x = 3.0
print(f"df/dz = {z.grad}")  # exp(1) = 2.718...
```

### Pattern 3: Vector-Valued Output — Seed the Adjoint
```python
# f(x) = [x, x^2, x^3] -> vector output, need to specify seed
x = mg.tensor(2.0)
x.requires_grad = True
y = mg.tensor([x, x**2, x**3])  # [2, 4, 8]

# Seed with ones to get full Jacobian row-sum
y.backward(mg.ones(3))
print(x.grad)  # 1 + 2x + 3x^2 = 1 + 4 + 12 = 17

# Or seed with specific weights for weighted gradient
x.null_grad()
weights = mg.tensor([1.0, 0.0, 0.0])
y.backward(weights)
print(x.grad)  # df1/dx = 1.0
```

### Pattern 4: Batch Gradient Computation
```python
# Batch of 100 samples, 10 features, 1 output per sample
n_samples, n_features = 100, 10
W = mg.tensor(np.random.randn(n_features))
W.requires_grad = True
X = mg.tensor(np.random.randn(n_samples, n_features))
y_true = mg.tensor(np.random.randn(n_samples))

# Mean squared error: (1/N) * sum((X@W - y_true)^2)
y_pred = mg.matmul(X, W)
loss = mg.mean((y_pred - y_true) ** 2)
loss.backward()

print(f"Gradient shape: {W.grad.shape}")  # (10,) — one grad per weight
```

### Pattern 5: Multi-Layer Neural Network Backprop
```python
def mlp_forward(X, W1, b1, W2, b2):
    """Two-layer MLP with ReLU activation."""
    h = mg.matmul(X, W1) + b1
    h_relu = mg.nnet.relu(h)
    out = mg.matmul(h_relu, W2) + b2
    return out

# Initialize parameters
W1 = mg.tensor(np.random.randn(784, 256) * 0.01); W1.requires_grad = True
b1 = mg.tensor(np.zeros(256)); b1.requires_grad = True
W2 = mg.tensor(np.random.randn(256, 10) * 0.01); W2.requires_grad = True
b2 = mg.tensor(np.zeros(10)); b2.requires_grad = True

# Forward pass
X_batch = mg.tensor(np.random.randn(32, 784))
logits = mlp_forward(X_batch, W1, b1, W2, b2)

# Cross-entropy loss
loss = mg.nnet.softmax_crossentropy(logits, mg.tensor(np.eye(10)[np.random.randint(0, 10, 32)]))

# Backward pass — gradients flow through entire graph
loss.backward()
print(f"W1 grad shape: {W1.grad.shape}")   # (784, 256)
print(f"W2 grad shape: {W2.grad.shape}")   # (256, 10)
```

### Pattern 6: Gradient Accumulation (Large Effective Batch)
```python
def train_with_accumulation(params, data_loader, accumulation_steps=4):
    """Accumulate gradients over multiple micro-batches.

    IMPORTANT: Do NOT use mg.no_autodiff during training — it disables
    gradient tracking entirely. Only use no_autodiff for inference/eval.
    """
    for param in params:
        param.null_grad()

    for step, (X_micro, y_micro) in enumerate(data_loader):
        # Forward + backward (gradients accumulate in .grad)
        loss = compute_loss(X_micro, y_micro, params)
        loss.backward()

        if (step + 1) % accumulation_steps == 0:
            # Step optimizer with accumulated gradients
            for param in params:
                param.data -= 0.01 * param.grad / accumulation_steps
                param.null_grad()
```

### Pattern 7: Gradient Clipping
```python
def clip_gradients(params, max_norm=1.0):
    """Clip gradients to prevent exploding gradients."""
    total_norm = 0.0
    for p in params:
        if p.grad is not None:
            total_norm += float(mg.sum(p.grad ** 2))

    total_norm = np.sqrt(total_norm)
    clip_coef = max_norm / (total_norm + 1e-6)

    if clip_coef < 1.0:
        for p in params:
            if p.grad is not None:
                # Use slice assignment to modify in-place (mygrad 2.3.0 .grad has no setter)
                p.grad[:] *= clip_coef
```

## Common Pitfalls & Debugging

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Forgot `requires_grad=True` | `.grad` is None after backward | Set `requires_grad=True` on tensor creation |
| Gradient accumulation | `.grad` grows each step | Call `.null_grad()` before each backward |
| In-place mutation | Graph broken, wrong gradients | Use `tensor.data = new_data` not `tensor = new_tensor` |
| `constant=True` tensors | No gradient flows through | Set `constant=False` or omit |
| Scalar loss on vector output | Wrong gradient shape | Use `mg.sum()` or `mg.mean()` to reduce to scalar |

## Key mygrad Functions Used
- `mg.tensor(x, requires_grad=True)` — differentiable tensor
- `tensor.backward(grad=None)` — reverse-mode backprop (the core API)
- `tensor.grad` — accumulated gradient after backward
- `tensor.null_grad()` — zero gradients between steps
- `tensor.data` — raw numpy array (no gradient tracking)
- `mg.no_autodiff` — context manager to disable tracking (inference mode)
- `mg.nnet.relu()`, `mg.nnet.softmax()`, `mg.nnet.softmax_crossentropy()` — differentiable NN ops
- `mg.matmul()`, `mg.sum()`, `mg.mean()`, `mg.exp()` — differentiable math ops

## Reference
- Rumelhart, Hinton & Williams, "Learning representations by back-propagating errors" (1986)
- mygrad documentation: https://mygrad.readthedocs.io/
