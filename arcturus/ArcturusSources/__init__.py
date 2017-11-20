# coding=utf-8

from os.path import dirname, basename, isfile, abspath
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') and f != 'Source.py']

def get_by_name(module_name: str):
    for module in __all__:
        if module_name in module.__name__:
            return module
    raise ImportError(f"module '{module_name}' cannot be found in {dirname(abspath(__file__))}")