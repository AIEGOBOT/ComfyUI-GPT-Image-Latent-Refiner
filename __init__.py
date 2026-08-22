"""ComfyUI entry point for GPT Image Latent Refiner."""

# ComfyUI imports this directory as a package. Pytest also inspects the root file
# as a top-level ``__init__`` module because the repository name contains hyphens;
# skip the package-only import in that collection-only case.
if __package__:
    from .nodes import GPTImageLatentRefinerExtension, comfy_entrypoint

    __all__ = ["GPTImageLatentRefinerExtension", "comfy_entrypoint"]
else:
    __all__: list[str] = []
