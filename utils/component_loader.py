import importlib
import os

def load_components(path="components"):
    """
    Dynamically loads all component modules in the given directory.
    Only considers Python files that do not start with '__'.
    """
    components = {}
    for filename in os.listdir(path):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]  # Remove '.py' extension
            try:
                module = importlib.import_module(f"{path}.{module_name}")
                # Check if the function exists in the module
                if hasattr(module, module_name):
                    components[module_name.capitalize()] = getattr(module, module_name)
                else:
                    print(f"Warning: No matching function '{module_name}' found in module '{module_name}.py'")
            except Exception as e:
                print(f"Error loading component '{module_name}': {e}")
    return components
