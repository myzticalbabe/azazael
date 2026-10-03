---
name: azazael-autodiff-gradient
description: Gradient descent and variants (SGD, Momentum, Adam and more) implemented from first principles with mygrad.
metadata:
  category: algorithm
  project: azazael
  priority: high
  auto_load: false
---

# azazael-autodiff-gradient
**Category:** Algorithm / Optimization
**Priority:** HIGH
**Dependencies:** mygrad>=2.3.0, numpy, azazael-autodiff-backprop
**Created:** June 14, 2026

## Purpose
Documents gradient descent and its variants for optimization using `mygrad` automatic differentiation. Covers SGD, Momentum, Nesterov, AdaGrad, RMSprop, Adam, and learning rate schedules — all implemented from first principles using mygrad's computational graph rather than relying on external optimizer libraries.

## When To Load
- When implementing any gradient-based optimizer
- When training models and needing custom learning rate schedules
- When debugging convergence issues in optimization
- When comparing optimizer performance (SGD vs Adam vs RMSprop)
- When the function landscape requires adaptive step sizes

## Core Implementations

**API note (mygrad 2.3.0):** `mg.tensor()` does NOT accept `requires_grad=True` as a kwarg. Set it after construction: `p = mg.tensor(val); p.requires_grad = True`

### 1. Vanilla SGD (Stochastic Gradient Descent)
```python
import mygrad as mg
import numpy as np

class SGD:
    """Vanilla SGD: theta = theta - lr * grad"""
    def __init__(self, params, lr=0.01):
        self.params = list(params)
        self.lr = lr

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        for p in self.params:
            if p.grad is not None:
                p.data -= self.lr * p.grad
```

### 2. SGD with Momentum
```python
class SGDMomentum:
    """SGD with momentum: v = beta*v + grad; theta = theta - lr*v"""
    def __init__(self, params, lr=0.01, momentum=0.9):
        self.params = list(params)
        self.lr = lr
        self.beta = momentum
        self.velocities = [np.zeros_like(p.data) for p in params]

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is not None:
                self.velocities[i] = self.beta * self.velocities[i] + p.grad
                p.data -= self.lr * self.velocities[i]
```

### 3. Nesterov Accelerated Gradient (NAG)
```python
class NesterovSGD:
    """Nesterov: look ahead before computing gradient.

    Standard Nesterov update (Sutskever 2013):
        v_prev = v
        v = momentum * v - lr * grad(loss(theta + momentum * v))
        theta = theta + v

    For mygrad: compute loss at look-ahead position, backprop, then update.
    """
    def __init__(self, params, lr=0.01, momentum=0.9):
        self.params = list(params)
        self.lr = lr
        self.momentum = momentum
        self.velocities = [np.zeros_like(p.data) for p in params]

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        # Nesterov: look-ahead update
        # 1. Save current params
        # 2. Move to look-ahead: theta_look = theta + momentum * v
        # 3. Compute gradient at look-ahead
        # 4. Update velocity and params
        #
        # Simplified for standard loss = f(theta) pattern:
        # We compute grad at current position, then apply Nesterov update
        for i, p in enumerate(self.params):
            if p.grad is not None:
                v_prev = self.velocities[i].copy()
                self.velocities[i] = self.momentum * v_prev - self.lr * p.grad
                # Standard Nesterov: theta += -momentum*v_prev + (1+momentum)*v_new
                p.data += -self.momentum * v_prev + (1 + self.momentum) * self.velocities[i]
```

### 4. AdaGrad (Adaptive Gradient)
```python
class AdaGrad:
    """AdaGrad: adaptive per-parameter learning rates.

    cache += grad^2
    theta -= lr * grad / sqrt(cache + eps)
    """
    def __init__(self, params, lr=0.01, eps=1e-8):
        self.params = list(params)
        self.lr = lr
        self.eps = eps
        self.cache = [np.zeros_like(p.data) for p in params]

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is not None:
                grad = np.array(p.grad)
                self.cache[i] += grad ** 2
                p.data -= self.lr * grad / (np.sqrt(self.cache[i]) + self.eps)
```

### 5. RMSprop
```python
class RMSprop:
    """RMSprop: moving average of squared gradients.

    cache = decay*cache + (1-decay)*grad^2
    theta -= lr * grad / sqrt(cache + eps)
    """
    def __init__(self, params, lr=0.001, decay=0.9, eps=1e-8):
        self.params = list(params)
        self.lr = lr
        self.decay = decay
        self.eps = eps
        self.cache = [np.zeros_like(p.data) for p in params]

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is not None:
                self.cache[i] = self.decay * self.cache[i] + (1 - self.decay) * p.grad ** 2
                p.data -= self.lr * p.grad / (np.sqrt(self.cache[i]) + self.eps)
```

### 6. Adam (Adaptive Moment Estimation)
```python
class Adam:
    """Adam: combines momentum and RMSprop with bias correction.

    m = beta1*m + (1-beta1)*grad        (first moment)
    v = beta2*v + (1-beta2)*grad^2      (second moment)
    m_hat = m / (1-beta1^t)              (bias correction)
    v_hat = v / (1-beta2^t)              (bias correction)
    theta -= lr * m_hat / (sqrt(v_hat) + eps)
    """
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8):
        self.params = list(params)
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.t = 0
        self.m = [np.zeros_like(p.data) for p in params]   # first moment
        self.v = [np.zeros_like(p.data) for p in params]   # second moment

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            if p.grad is not None:
                grad = np.array(p.grad)
                self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
                self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2

                # Bias correction
                m_hat = self.m[i] / (1 - self.beta1 ** self.t)
                v_hat = self.v[i] / (1 - self.beta2 ** self.t)

                p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

### 7. AdamW (Adam with Decoupled Weight Decay)
```python
class AdamW:
    """AdamW: Adam with decoupled weight decay.

    Standard Adam applies L2 regularization through the gradient,
    which interacts poorly with adaptive learning rates.
    AdamW applies weight decay directly: theta -= lr * wd * theta
    """
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01):
        self.params = list(params)
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.t = 0
        self.m = [np.zeros_like(p.data) for p in params]
        self.v = [np.zeros_like(p.data) for p in params]

    def zero_grad(self):
        for p in self.params:
            p.null_grad()

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            if p.grad is not None:
                grad = np.array(p.grad)
                self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
                self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2

                m_hat = self.m[i] / (1 - self.beta1 ** self.t)
                v_hat = self.v[i] / (1 - self.beta2 ** self.t)

                # Decoupled weight decay
                p.data -= self.lr * self.weight_decay * p.data
                p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

## Learning Rate Schedules

```python
class LRScheduler:
    """Base class for learning rate schedules."""

    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.base_lr = optimizer.lr

    def step(self, epoch=None, loss=None):
        raise NotImplementedError

class StepLR(LRScheduler):
    """Decay lr by gamma every step_size epochs."""
    def __init__(self, optimizer, step_size=30, gamma=0.1):
        super().__init__(optimizer)
        self.step_size = step_size
        self.gamma = gamma

    def step(self, epoch):
        self.optimizer.lr = self.base_lr * (self.gamma ** (epoch // self.step_size))

class CosineAnnealingLR(LRScheduler):
    """Cosine annealing: lr = min_lr + 0.5*(base_lr-min_lr)*(1+cos(pi*epoch/max_epochs))"""
    def __init__(self, optimizer, max_epochs=100, min_lr=0.0):
        super().__init__(optimizer)
        self.max_epochs = max_epochs
        self.min_lr = min_lr

    def step(self, epoch):
        progress = epoch / self.max_epochs
        self.optimizer.lr = self.min_lr + 0.5 * (self.base_lr - self.min_lr) * (1 + np.cos(np.pi * progress))

class ReduceLROnPlateau(LRScheduler):
    """Reduce lr when loss plateaus."""
    def __init__(self, optimizer, factor=0.1, patience=10, min_lr=1e-7):
        super().__init__(optimizer)
        self.factor = factor
        self.patience = patience
        self.min_lr = min_lr
        self.best_loss = float('inf')
        self.wait = 0

    def step(self, loss):
        if loss < self.best_loss:
            self.best_loss = loss
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.optimizer.lr = max(self.optimizer.lr * self.factor, self.min_lr)
                self.wait = 0
```

## Complete Training Loop Example
```python
def train(f, params, X, y, optimizer, epochs=100):
    """Generic training loop with mygrad.

    Args:
        f: function(params, X) -> prediction
        params: list of mygrad tensors
        X, y: training data
        optimizer: any optimizer from above
    """
    losses = []
    for epoch in range(epochs):
        optimizer.zero_grad()

        # Forward pass
        pred = f(params, mg.tensor(X))
        loss = mg.mean((pred - mg.tensor(y)) ** 2)

        # Backward pass
        loss.backward()

        # Gradient step
        optimizer.step()

        losses.append(float(loss.data))
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: loss = {losses[-1]:.6f}")

    return losses
```

## Optimizer Selection Guide

| Optimizer | Best For | Watch Out For |
|-----------|----------|---------------|
| SGD | Convex problems, well-conditioned landscapes | Slow on ill-conditioned problems |
| SGD + Momentum | Deep networks, escaping local minima | Hyperparameter tuning (beta) |
| Nesterov | When momentum helps but overshoots | More compute per step |
| AdaGrad | Sparse features, NLP | Learning rate monotonic decay |
| RMSprop | RNNs, non-stationary objectives | Sensitive to decay rate |
| Adam | Default choice, most problems | Can diverge, needs warmup sometimes |
| AdamW | When using weight decay (L2 reg) | Slightly more compute than Adam |

## Key mygrad Functions Used
- `mg.tensor()` — differentiable parameters
- `tensor.backward()` — compute gradients
- `tensor.grad` — access computed gradients
- `tensor.null_grad()` — zero gradients
- `tensor.data` — raw parameter values
- `mg.mean()`, `mg.sum()` — loss reductions
- `mg.matmul()` — linear layer forward pass

## Reference
- Kingma & Ba, "Adam: A Method for Stochastic Optimization" (2014)
- Loshchilov & Hutter, "Decoupled Weight Decay Regularization" (2017) — AdamW
- Sutskever et al., "On the importance of initialization and momentum" (2013)
