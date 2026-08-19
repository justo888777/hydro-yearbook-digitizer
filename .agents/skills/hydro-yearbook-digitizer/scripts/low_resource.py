"""Conservative process settings for long local OCR jobs on Windows."""
from __future__ import annotations

import ctypes
import os


def affinity_mask(cpu_count: int, max_cores: int = 2) -> int:
    cores = max(1, min(int(max_cores), int(cpu_count)))
    return (1 << cores) - 1


def resource_core_limit(cpu_count: int, mode: str = "low") -> int:
    """Return the logical-core cap for a named local OCR profile."""

    count = max(1, int(cpu_count))
    if mode == "low":
        return min(2, count)
    if mode == "medium":
        return min(4, max(1, count // 2))
    if mode == "standard":
        return min(4, count)
    if mode == "two_thirds":
        return max(1, (count * 2) // 3)
    if mode == "three_quarters":
        return max(1, (count * 3) // 4)
    raise ValueError(
        "mode must be 'low', 'medium', 'standard', 'two_thirds' or 'three_quarters'"
    )


def apply_low_resource_policy(max_cores: int = 2) -> None:
    """Use below-normal priority and at most ``max_cores`` logical CPUs."""

    os.environ.setdefault("OMP_NUM_THREADS", str(max_cores))
    os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
    os.environ.setdefault("MKL_NUM_THREADS", str(max_cores))
    if os.name != "nt":
        return
    kernel32 = ctypes.windll.kernel32
    # Declare the Win32 ABI explicitly. On 64-bit Python 3.10 a process
    # pseudo-handle can overflow ctypes' default c_int conversion, which used
    # to make PaddleOCR jobs fail before recognition started.
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel32.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    handle = kernel32.GetCurrentProcess()
    kernel32.SetPriorityClass(handle, 0x00004000)
    kernel32.SetProcessAffinityMask(handle, affinity_mask(os.cpu_count() or 1, max_cores))


def apply_resource_policy(mode: str = "low") -> None:
    """Apply the requested capped policy without occupying the full machine."""

    apply_low_resource_policy(resource_core_limit(os.cpu_count() or 1, mode))
