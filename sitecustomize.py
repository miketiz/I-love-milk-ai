"""
Prevent transformers vision modules and torchvision from loading on startup.
This stops Streamlit's file watcher from scanning lazy-loaded vision modules.
"""
import sys
import types
from importlib.machinery import ModuleSpec


def _create_dummy_module(name):
    """Create a dummy module with proper __spec__ attribute."""
    module = types.ModuleType(name)
    # Set __spec__ to None to satisfy importlib.util.find_spec checks
    module.__spec__ = None
    module.__loader__ = None
    return module


# Pre-create dummy torch and torchvision modules BEFORE any imports
dummy_torch = _create_dummy_module('torch')
dummy_torchvision = _create_dummy_module('torchvision')
dummy_torchvision_transforms = _create_dummy_module('torchvision.transforms')
dummy_torchvision_transforms_v2 = _create_dummy_module('torchvision.transforms.v2')
dummy_torchvision_transforms_v2.functional = _create_dummy_module('torchvision.transforms.v2.functional')
dummy_torchvision_io = _create_dummy_module('torchvision.io')
dummy_torchvision_ops = _create_dummy_module('torchvision.ops')
dummy_torchvision_ops.boxes = _create_dummy_module('torchvision.ops.boxes')

# Add dummy functions
def dummy_read_image(*args, **kwargs):
    raise ImportError("torchvision not available")

def dummy_batched_nms(*args, **kwargs):
    raise ImportError("torchvision not available")

dummy_torchvision_io.read_image = dummy_read_image
dummy_torchvision_ops.boxes.batched_nms = dummy_batched_nms

# Register dummy modules in sys.modules
sys.modules['torch'] = dummy_torch
sys.modules['torchvision'] = dummy_torchvision
sys.modules['torchvision.transforms'] = dummy_torchvision_transforms
sys.modules['torchvision.transforms.v2'] = dummy_torchvision_transforms_v2
sys.modules['torchvision.transforms.v2.functional'] = dummy_torchvision_transforms_v2.functional
sys.modules['torchvision.io'] = dummy_torchvision_io
sys.modules['torchvision.ops'] = dummy_torchvision_ops
sys.modules['torchvision.ops.boxes'] = dummy_torchvision_ops.boxes


class BlockVisionModules:
    """Block transformers vision models and torchvision."""

    def find_module(self, fullname, path=None):
        # Block torchvision and torch entirely
        if fullname.startswith('torch'):
            return self
        return None

    def load_module(self, fullname):
        # Return pre-made dummy modules
        if fullname in sys.modules:
            return sys.modules[fullname]
        import types
        module = types.ModuleType(fullname)
        sys.modules[fullname] = module
        return module


# Install the import hook at the very start
sys.meta_path.insert(0, BlockVisionModules())
