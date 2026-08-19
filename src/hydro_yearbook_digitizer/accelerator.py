"""Portable OpenVINO device selection for registered-cell recognition."""

from __future__ import annotations

from collections.abc import Iterable


def choose_openvino_device(
    available_devices: Iterable[str],
    policy: str = "throughput",
) -> str:
    """Choose an available device without encoding a specific hardware model.

    The caller should benchmark candidate devices on the same registered cell
    batch before release.  This function only provides a deterministic default
    and a CPU fallback when accelerator plugins are absent.
    """

    devices = [str(device) for device in available_devices]
    if not devices:
        return "CPU"
    roots = {device.split(".", 1)[0].upper(): device for device in devices}
    priorities = {
        "throughput": ("GPU", "NPU", "CPU"),
        "energy": ("NPU", "GPU", "CPU"),
        "compatibility": ("CPU", "GPU", "NPU"),
    }
    if policy not in priorities:
        raise ValueError(f"unknown OpenVINO device policy: {policy}")
    for device_type in priorities[policy]:
        if device_type in roots:
            return roots[device_type]
    return devices[0]


def discover_openvino_devices() -> tuple[str, ...]:
    """Return OpenVINO devices, or an empty tuple when it is not installed."""

    try:
        from openvino import Core
    except ImportError:
        return ()
    return tuple(Core().available_devices)
