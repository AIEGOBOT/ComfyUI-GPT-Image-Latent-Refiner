"""ComfyUI V3 node definitions."""

from __future__ import annotations

from typing_extensions import override

from comfy_api.v0_0_2 import ComfyExtension, io

from .gpt_image_latent_refiner.runtime import refine_images


class GPTImageLatentRefiner(io.ComfyNode):
    """Remove recurring GPT Image texture artifacts in VAE latent space."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="indii.GPTImageLatentRefiner",
            display_name="GPT Image Latent Refiner",
            description=(
                "Reduces dot noise, stippling, grime, and repeating micro-textures with "
                "an independently trained latent residual model. Qwen is the recommended "
                "default; Flux2 preserves more source detail; SDXL is experimental."
            ),
            category="GPT Image/refinement",
            inputs=[
                io.Image.Input("image"),
                io.Combo.Input(
                    "profile",
                    options=["qwen", "flux2", "sdxl"],
                    default="qwen",
                    tooltip=(
                        "qwen: recommended balance; flux2: stronger source preservation; "
                        "sdxl: experimental and more likely to reshape detail."
                    ),
                ),
                io.Float.Input(
                    "strength",
                    default=1.0,
                    min=0.0,
                    max=2.0,
                    step=0.05,
                    tooltip="0 bypasses the learned correction; 1 is the trained strength.",
                ),
                io.Combo.Input(
                    "device",
                    options=["auto", "cuda", "cpu"],
                    default="auto",
                    advanced=True,
                ),
                io.Boolean.Input(
                    "tile_vae",
                    default=True,
                    advanced=True,
                    tooltip="Use VAE tiling to reduce peak VRAM on large images.",
                ),
            ],
            outputs=[io.Image.Output("image")],
        )

    @classmethod
    def execute(
        cls,
        image,
        profile: str,
        strength: float,
        device: str,
        tile_vae: bool,
    ) -> io.NodeOutput:
        return io.NodeOutput(
            refine_images(
                image=image,
                profile_name=profile,
                strength=strength,
                device_mode=device,
                tile_vae=tile_vae,
            )
        )


class GPTImageLatentRefinerExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [GPTImageLatentRefiner]


async def comfy_entrypoint() -> GPTImageLatentRefinerExtension:
    return GPTImageLatentRefinerExtension()
