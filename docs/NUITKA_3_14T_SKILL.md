# Nuitka 3.14t Rebuild Skill — Complete Guide

> **Skill Name:** `nuitka-314t-rebuild`
> **Version:** 1.0.0
> **Last Updated:** June 2, 2026
> **Status:** ✅ Active — 5 C-level patches required

---

## Overview

Nuitka 4.1.2 on Python 3.14.5 free-threading build fails with C backend compilation errors. This document catalogs all known issues, their fixes, and the rebuild process. Load this skill when rebuilding any Nuitka EXE for Python 3.14t.

---

## Environment

| Component | Value |
|-----------|-------|
| Python | 3.14.5 free-threading (no-GIL) |
| Nuitka | 4.1.2 |
| Compiler | MSVC 14.5 (Visual Studio 2022) |
| Platform | Windows 11, x64 |
| Nuitka path | `C:\Users\clint\AppData\Local\Programs\Python\Python314\Lib\site-packages\nuitka\` |

---

## Bug #1 — `allocator.h`: `ob_gc_bits` Direct Access

### Error
```
error C2223: left of '->ob_gc_bits' must point to struct/union
error C2065: 'op': undeclared identifier
```

### File
`nuitka/build/include/nuitka/allocator.h`

### Root Cause
In Python 3.14t, `ob_gc_bits` is a field of `PyObject` GC headers but must be accessed via atomic operations in GIL-disabled mode. Nuitka accesses it directly:
```c
op->ob_gc_bits = 0;                                    // Line ~39
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED); // Line ~60
```

### Fix
Replace direct access with atomic accessor macros:
```c
// BEFORE
op->ob_gc_bits = 0;

// AFTER
_Py_atomic_store_uint8_relaxed(&op->ob_gc_bits, 0);

// BEFORE
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED);

// AFTER
// _Py_atomic_or_uint8 in 3.14t takes (target, value, memory_order)
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED, _Py_memory_order_relaxed);
```

### Verification
- `#include "pycore_atomic.h"` is already in scope
- Use `_Py_atomic_store_uint8_relaxed` for writes
- Use `_Py_atomic_load_uint8_relaxed` for reads
- Use `_Py_atomic_or_uint8` with 3 args (target, value, order)

---

## Bug #2 — `HelpersAllocator.c`: GC State Structure Change

### Error
```
error C2039: 'generations': is not a member of '_gc_runtime_state'
```

### File
`nuitka/build/static_src/HelpersAllocator.c`

### Root Cause
In Python 3.14t, the GC runtime state is restructured. `_gc_runtime_state` still has `generations`, but the way it's accessed changed. The struct is now nested inside the interpreter state rather than being a standalone global. Nuitka's code does:
```c
typedef struct _gc_runtime_state GCState;  // type alias
// Later:
GCState *gcstate = ...;
gcstate->generations[0].count++;
```

### Fix
The fix depends on exactly how the GCState pointer is obtained. In 3.14t, access via interpreter state:
```c
// BEFORE (direct global access)
extern struct _gc_runtime_state _PyGC_GlobalState;
#define gcstate (&_PyGC_GlobalState)

// AFTER (interpreter-based access in GIL-disabled mode)
struct _gc_runtime_state *gcstate = &_PyInterpreterState_GET()->gc;
```

### Verification
- Check `pycore_interp_structs.h` for `struct _gc_runtime_state gc;` inside interpreter state
- The `generations` array is now: `interp->gc.generations` not `_PyGC_GlobalState.generations`
- If `Py_GIL_DISABLED` is defined, always use interpreter-based access

---

## Bug #3 — `HelpersDictionaries.c`: `_Py_IMMORTAL_REFCNT` Removed

### Error
```
error C2065: '_Py_IMMORTAL_REFCNT': undeclared identifier
```

### File
`nuitka/build/static_src/HelpersDictionaries.c` (lines ~93, ~103)

### Root Cause
In Python 3.14t, `_Py_IMMORTAL_REFCNT` was replaced with `_Py_IMMORTAL_REFCNT_LOCAL` or removed in favor of a different immortal object mechanism. Nuitka's code checks:
```c
if (FT_ATOMIC_LOAD_SSIZE_RELAXED(dk->dk_refcnt) == _Py_IMMORTAL_REFCNT)
```

### Fix
Replace with 3.14t's equivalent:
```c
// Option A: Use the new constant name (if available)
#include "pycore_object.h"  // For _Py_IsImmortal
if (_Py_IsImmortal(dk)) ...

// Option B: Use the local immortal refcount
if (FT_ATOMIC_LOAD_SSIZE_RELAXED(dk->dk_refcnt) == _Py_IMMORTAL_REFCNT_LOCAL)

// Option C: Check Python version and use appropriate constant
#if PYTHON_VERSION >= 0x30E00  // Python 3.14
    #ifdef _Py_IMMORTAL_REFCNT_LOCAL
        #define NUITKA_IMMORTAL_REFCNT _Py_IMMORTAL_REFCNT_LOCAL
    #else
        #define NUITKA_IMMORTAL_REFCNT ((Py_ssize_t)-1000)  // Known value
    #endif
#else
    #define NUITKA_IMMORTAL_REFCNT _Py_IMMORTAL_REFCNT
#endif
```

### Verification
- Search Python include headers for `_Py_IMMORTAL_REFCNT` — may be in `pycore_object.h` or `cpython/object.h`
- In 3.14t, immortal objects use `_Py_IsImmortal()` macro
- For dict keys specifically, check `PyDictKeysObject` internals in `cpython/dictobject.h`

---

## Bug #4 — `CompiledFrameType.c`: `_PyStackRef` Type Change

### Error
```
error C2440: '=': cannot convert from 'int' to '_PyStackRef'
```

### File
`nuitka/build/static_src/CompiledFrameType.c` (line ~859)

### Root Cause
In Python 3.14t, `_PyStackRef` changed from a simple integer type (`intptr_t` or similar) to a struct. Nuitka tries:
```c
locals_owner->f_executable = _PyStackRef_FromPyObjectNew((PyObject *)code);
```
The RHS returns a `_PyStackRef` struct but the assignment context might expect an integer.

### Fix
Ensure the type is handled correctly:
```c
// BEFORE
locals_owner->f_executable = _PyStackRef_FromPyObjectNew((PyObject *)code);

// AFTER - ensure f_executable is _PyStackRef type
// _PyStackRef_FromPyObjectNew returns _PyStackRef, which is correct
// The error may be in how the struct is used afterward
// Check if field access needs .ref or .object suffix:
// locals_owner->f_executable = _PyStackRef_FromPyObjectNew((PyObject *)code);
```

### Verification
- Check Python 3.14t `cpython/frameobject.h` for `_PyStackRef` definition
- In 3.14t, `_PyStackRef` is: `typedef struct { PyObject *ref; } _PyStackRef;`
- The `_PyStackRef_FromPyObjectNew` function returns this struct correctly
- If code expects an integer, wrap with: `_PyStackRef_AsPyObject(locals_owner->f_executable)` for access

---

## Bug #5 — `_Py_atomic_or_uint8`: Wrong Number of Arguments

### Error
```
error C2198: 'uint8_t _Py_atomic_or_uint8(uint8_t *,uint8_t)': too few arguments for call
```

### Files Affected
Multiple: `allocator.h`, `HelpersAllocator.c`, `HelpersDictionaries.c`

### Root Cause
In Python 3.14t, `_Py_atomic_or_uint8` takes **3 arguments** (pointer, value, memory_order), but Nuitka passes **2**:
```c
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED);
```

### Fix
Add the memory order parameter:
```c
// BEFORE
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED);

// AFTER (3.14t)
_Py_atomic_or_uint8(&op->ob_gc_bits, _PyGC_BITS_DEFERRED, _Py_memory_order_relaxed);
```

### Global Find & Replace Scope
Search Nuitka's `build/` directory for ALL instances:
```bash
grep -rn "_Py_atomic_or_uint8" nuitka/build/ --include="*.c" --include="*.h"
```
Every instance needs the 3rd argument added.

---

## Bug #6 (Optional) — `_Py_atomic_*` Function Signatures

### Context
Multiple `_Py_atomic_*` functions may have changed signatures in 3.14t. Always check:
- `_Py_atomic_load_*` — usually still 2 args (ptr, order)
- `_Py_atomic_store_*` — usually still 3 args (ptr, val, order)  
- `_Py_atomic_add_*` — may be 3 args (ptr, val, order)
- `_Py_atomic_or_*` — **3 args in 3.14t** (ptr, val, order) — this changed!

### Safety Check
For every `_Py_atomic_*` call in Nuitka's source, verify against the Python 3.14t header:
```
Python314/Include/internal/pycore_atomic.h
```

---

## Rebuild Procedure

### Step 1: Apply all patches

```bash
# Set working directory
cd C:/Users/clint/AppData/Local/Programs/Python/Python314/Lib/site-packages/nuitka

# Patch 1: allocator.h - Fix ob_gc_bits access
# Edit build/include/nuitka/allocator.h
#   Line ~39: op->ob_gc_bits = 0              → _Py_atomic_store_uint8_relaxed(&op->ob_gc_bits, 0)
#   Line ~60: _Py_atomic_or_uint8(a, b)         → _Py_atomic_or_uint8(a, b, _Py_memory_order_relaxed)

# Patch 2: HelpersAllocator.c - Fix GC state access
# Edit build/static_src/HelpersAllocator.c
#   Replace _PyGC_GlobalState.generations with _PyInterpreterState_GET()->gc.generations

# Patch 3: HelpersDictionaries.c - Fix immortal refcount
# Edit build/static_src/HelpersDictionaries.c  
#   Replace _Py_IMMORTAL_REFCNT with appropriate 3.14t equivalent

# Patch 4: CompiledFrameType.c - Fix _PyStackRef type
# Edit build/static_src/CompiledFrameType.c
#   Verify _PyStackRef_FromPyObjectNew is correctly typed

# Patch 5: Global _Py_atomic_or_uint8 - Fix all 2-arg calls to 3-arg
# Find all: grep -rn \"_Py_atomic_or_uint8\" in build/
# Fix each to add _Py_memory_order_relaxed as 3rd arg
```

### Step 2: Test compilation of a minimal file

```bash
cd ~/Desktop/AZAZAEL_Vault
python -m nuitka --onefile --verbose test_minimal.py 2>&1 | tee build_log.txt
```

### Step 3: Test with actual vault server

```bash
python -m nuitka --onefile --verbose vault_server.py 2>&1 | tee vault_build_log.txt
```

### Step 4: Verify EXE functionality

```bash
# Test the compiled EXE
./vault_server.exe &
# Verify it starts and responds
curl http://localhost:6000/api/home
```

---

## Testing Checklist

- [ ] `test_minimal.py` compiles to EXE successfully
- [ ] EXE runs and produces correct output
- [ ] `vault_server.py` compiles to EXE successfully
- [ ] Vault EXE starts on port 6000
- [ ] Vault EXE responds to API calls
- [ ] Graph rendering works (vis-network loads in browser)
- [ ] Search/timeline/diff endpoints respond
- [ ] File editing returns results correctly
- [ ] GIL is confirmed disabled inside EXE: `sys._is_gil_enabled() == False`
- [ ] Free-threading features work (ThreadPoolExecutor, parallel ops)

---

## Rollback Procedure

If patches break something, restore Nuitka's original files:

```bash
pip install nuitka==4.1.2 --force-reinstall
```

Or restore from backup:
```bash
cp -r /path/to/nuitka_backup /path/to/nuitka
```

---

## Error Recovery Template

```markdown
## Error #NN — Nuitka 3.14t Build Failure
**Timestamp:** YYYY-MM-DD HH:MM
**Severity:** 🔴 Critical
**File(s):** nuitka/build/.../filename.c:LINE
**Error:** CXXXX: Description

**Root Cause:** ...  
**Fix Applied:** ...  
**Verification:** [Pass/Fail]  
**Prevention:** Document in NUITKA_3_14T_SKILL.md
```

---

## Related Skills & Docs

- `azazael-nuitka-314t` — This skill (load with `skill("nuitka-314t-rebuild")`)
- `nuitka-packaging` — Nuitka build strategy for production
- `azazael-standalone` — Standalone EXE build pipeline
- `azazael-parallel` — 3.14t parallel execution patterns
- `azazael-freethreading` — Free-threading-specific code patterns

---

*Generated by AZAZAEL Codebuff — Nuitka 3.14t compatibility engineering*
