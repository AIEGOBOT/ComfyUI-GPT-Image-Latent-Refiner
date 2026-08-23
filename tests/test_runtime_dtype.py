"""Unit tests for CUDA inference dtype selection."""

from __future__ import annotations

from contextlib import contextmanager, nullcontext
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

import torch


folder_paths_stub = types.ModuleType("folder_paths")
folder_paths_stub.models_dir = str(Path.cwd() / "models")
sys.modules.setdefault("folder_paths", folder_paths_stub)

model_management_stub = types.ModuleType("comfy.model_management")
comfy_stub = types.ModuleType("comfy")
comfy_stub.model_management = model_management_stub
sys.modules.setdefault("comfy", comfy_stub)
sys.modules.setdefault("comfy.model_management", model_management_stub)

from gpt_image_latent_refiner.runtime import (  # noqa: E402
    _autocast_context,
    _select_inference_dtype,
)


class DTypeSelectionTests(unittest.TestCase):
    def test_cpu_uses_fp32(self) -> None:
        self.assertIs(_select_inference_dtype(torch.device("cpu")), torch.float32)

    def test_native_bf16_is_preferred(self) -> None:
        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(torch.cuda, "is_bf16_supported", return_value=True),
            patch.object(torch.cuda, "get_device_capability", return_value=(9, 0)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.bfloat16,
            )

    def test_fp16_then_fp32_fallbacks(self) -> None:
        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(torch.cuda, "is_bf16_supported", return_value=False),
            patch.object(torch.cuda, "get_device_capability", return_value=(7, 5)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.float16,
            )

        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(torch.cuda, "is_bf16_supported", return_value=False),
            patch.object(torch.cuda, "get_device_capability", return_value=(5, 2)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.float32,
            )

    def test_legacy_bf16_signature_is_supported(self) -> None:
        def legacy_bf16_check() -> bool:
            return False

        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(
                torch.cuda,
                "is_bf16_supported",
                side_effect=legacy_bf16_check,
            ),
            patch.object(torch.cuda, "get_device_capability", return_value=(6, 1)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.float16,
            )

    def test_legacy_emulated_bf16_uses_fp16_on_pre_ampere_gpu(self) -> None:
        def legacy_bf16_check() -> bool:
            return True

        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(
                torch.cuda,
                "is_bf16_supported",
                side_effect=legacy_bf16_check,
            ),
            patch.object(torch.cuda, "get_device_capability", return_value=(7, 0)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.float16,
            )

    def test_legacy_native_bf16_is_used_on_ampere_or_newer(self) -> None:
        def legacy_bf16_check() -> bool:
            return True

        with (
            patch.object(torch.cuda, "device", return_value=nullcontext()),
            patch.object(
                torch.cuda,
                "is_bf16_supported",
                side_effect=legacy_bf16_check,
            ),
            patch.object(torch.cuda, "get_device_capability", return_value=(8, 0)),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:0")),
                torch.bfloat16,
            )

    def test_detection_failure_uses_fp32(self) -> None:
        with patch.object(
            torch.cuda,
            "device",
            side_effect=RuntimeError("device detection failed"),
        ):
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:1")),
                torch.float32,
            )

    def test_selected_device_controls_bf16_and_restores_current_device(self) -> None:
        state = {"current": 0}
        observed_devices: list[int] = []

        @contextmanager
        def selected_device_context(device: torch.device):
            previous = state["current"]
            state["current"] = device.index if device.index is not None else 0
            try:
                yield
            finally:
                state["current"] = previous

        def selected_device_supports_bf16(*, including_emulation: bool) -> bool:
            self.assertFalse(including_emulation)
            observed_devices.append(state["current"])
            return state["current"] == 1

        with (
            patch.object(
                torch.cuda,
                "device",
                side_effect=selected_device_context,
            ),
            patch.object(
                torch.cuda,
                "is_bf16_supported",
                side_effect=selected_device_supports_bf16,
            ),
            patch.object(torch.cuda, "get_device_capability", return_value=(9, 0)),
        ):
            self.assertEqual(state["current"], 0)
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:1")),
                torch.bfloat16,
            )
            self.assertEqual(observed_devices, [1])
            self.assertEqual(state["current"], 0)

    def test_selected_non_bf16_device_uses_its_fp16_capability(self) -> None:
        state = {"current": 0}
        observed_devices: list[int] = []

        @contextmanager
        def selected_device_context(device: torch.device):
            previous = state["current"]
            state["current"] = device.index if device.index is not None else 0
            try:
                yield
            finally:
                state["current"] = previous

        def original_device_only_supports_bf16(*, including_emulation: bool) -> bool:
            self.assertFalse(including_emulation)
            observed_devices.append(state["current"])
            return state["current"] == 0

        with (
            patch.object(
                torch.cuda,
                "device",
                side_effect=selected_device_context,
            ),
            patch.object(
                torch.cuda,
                "is_bf16_supported",
                side_effect=original_device_only_supports_bf16,
            ),
            patch.object(torch.cuda, "get_device_capability", return_value=(7, 5)),
        ):
            self.assertEqual(state["current"], 0)
            self.assertIs(
                _select_inference_dtype(torch.device("cuda:1")),
                torch.float16,
            )
            self.assertEqual(observed_devices, [1])
            self.assertEqual(state["current"], 0)

    def test_autocast_is_limited_to_cuda_bf16_or_fp16(self) -> None:
        cuda = torch.device("cuda:0")
        cpu = torch.device("cpu")

        with patch("torch.autocast") as autocast:
            _autocast_context(cuda, torch.bfloat16)
            autocast.assert_called_once_with(
                device_type="cuda",
                dtype=torch.bfloat16,
            )

        with patch("torch.autocast") as autocast:
            _autocast_context(cuda, torch.float16)
            autocast.assert_called_once_with(
                device_type="cuda",
                dtype=torch.float16,
            )

        with patch("torch.autocast") as autocast:
            _autocast_context(cuda, torch.float32)
            _autocast_context(cpu, torch.float32)
            autocast.assert_not_called()


if __name__ == "__main__":
    unittest.main()
