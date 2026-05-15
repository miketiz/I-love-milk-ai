"""
Prevent transformers vision modules and torchvision from loading on startup.
This stops Streamlit's file watcher from scanning lazy-loaded vision modules.
"""
import sys


# List of vision model packages in transformers that require torchvision
BLOCKED_VISION_MODULES = {
    'transformers.models.zoedepth',
    'transformers.models.aria',
    'transformers.models.sam',
    'transformers.models.blip',
    'transformers.models.deta',
    'transformers.models.dino',
    'transformers.models.vit',
    'transformers.image_processing_utils',
    'transformers.image_processing',
}

BLOCKED_PACKAGES = {
    'torchvision',
    'torch',
}


class BlockVisionModules:
    """Block transformers vision models and torchvision."""

    def find_module(self, fullname, path=None):
        # Check if module should be blocked
        if fullname in BLOCKED_VISION_MODULES:
            return self
        
        # Check if it's a submodule of blocked packages
        for blocked in BLOCKED_VISION_MODULES:
            if fullname.startswith(blocked + '.'):
                return self
        
        # Block torchvision and torch entirely
        if fullname in BLOCKED_PACKAGES or fullname.startswith('torch') or fullname.startswith('torchvision'):
            return self

        return None

    def load_module(self, fullname):
        # Mock torchvision and torch with dummy modules
        if 'torchvision' in fullname or fullname == 'torch':
            import types
            module = types.ModuleType(fullname)
            sys.modules[fullname] = module
            return module
        
        # Block vision modules from loading
        raise ImportError(
            f"Module '{fullname}' requires dependencies not available in this environment"
        )


# Install the import hook at the very start
sys.meta_path.insert(0, BlockVisionModules())
