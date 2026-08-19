from hydro_yearbook_digitizer.accelerator import choose_openvino_device


def test_throughput_policy_prefers_gpu_without_hardware_model_names() -> None:
    assert choose_openvino_device(["CPU", "GPU", "NPU"], "throughput") == "GPU"


def test_energy_policy_prefers_npu_and_preserves_device_suffix() -> None:
    assert choose_openvino_device(["CPU", "NPU.0"], "energy") == "NPU.0"


def test_cpu_and_empty_device_fallbacks_are_deterministic() -> None:
    assert choose_openvino_device(["CPU"], "throughput") == "CPU"
    assert choose_openvino_device([], "throughput") == "CPU"


def test_unknown_policy_is_rejected() -> None:
    try:
        choose_openvino_device(["CPU"], "fastest")
    except ValueError as exc:
        assert "unknown OpenVINO device policy" in str(exc)
    else:
        raise AssertionError("unknown policy must fail")
