from __future__ import annotations

import ctypes
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "low_resource.py"
SPEC = importlib.util.spec_from_file_location("low_resource_under_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeFunction:
    def __init__(self, result=1):
        self.result = result
        self.calls = []
        self.restype = None
        self.argtypes = None

    def __call__(self, *args):
        self.calls.append(args)
        return self.result


class LowResourceTests(unittest.TestCase):
    def test_standard_cap(self):
        self.assertEqual(MODULE.resource_core_limit(16, "standard"), 4)
        self.assertEqual(MODULE.resource_core_limit(2, "standard"), 2)

    def test_two_thirds_cap(self):
        self.assertEqual(MODULE.resource_core_limit(16, "two_thirds"), 10)
        self.assertEqual(MODULE.affinity_mask(16, 10), (1 << 10) - 1)

    def test_three_quarters_cap(self):
        self.assertEqual(MODULE.resource_core_limit(16, "three_quarters"), 12)
        self.assertEqual(MODULE.affinity_mask(16, 12), (1 << 12) - 1)

    @unittest.skipUnless(os.name == "nt", "Win32 ctypes ABI")
    def test_win32_handle_uses_pointer_sized_signatures(self):
        kernel32 = type("Kernel32", (), {})()
        kernel32.GetCurrentProcess = FakeFunction(0xFFFFFFFFFFFFFFFF)
        kernel32.SetPriorityClass = FakeFunction(1)
        kernel32.SetProcessAffinityMask = FakeFunction(1)
        windll = type("Windll", (), {"kernel32": kernel32})()
        with patch.object(MODULE.ctypes, "windll", windll):
            MODULE.apply_low_resource_policy(10)
        self.assertIs(kernel32.GetCurrentProcess.restype, ctypes.c_void_p)
        self.assertEqual(kernel32.SetPriorityClass.argtypes, [ctypes.c_void_p, ctypes.c_uint32])
        self.assertEqual(kernel32.SetProcessAffinityMask.argtypes, [ctypes.c_void_p, ctypes.c_size_t])
        self.assertEqual(kernel32.SetProcessAffinityMask.calls[0][1], (1 << 10) - 1)


if __name__ == "__main__":
    unittest.main()
