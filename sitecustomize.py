"""
Prevent transformers image processing modules from loading on startup.
This stops Streamlit's file watcher from scanning lazy-loaded vision modules.
"""
import sys


class BlockTransformersImageModules:
    """Block import of transformers vision modules."""

    def find_module(self, fullname, path=None):
        # Block all transformers image_processing modules
        if "transformers" in fullname and "image_processing" in fullname:
            return self

        # Block torchvision entirely (not installed, causes noise)
        if "torchvision" in fullname:
            return self

        return None

    def load_module(self, fullname):
        # Raise ImportError to prevent loading
        raise ImportError(
            f"Module '{fullname}' is blocked to prevent import errors in Streamlit."
        )


# Install the import hook at the very start
sys.meta_path.insert(0, BlockTransformersImageModules())
