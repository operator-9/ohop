'''Utility library for working with Jupyter Notebooks.

Based on import tools in the Jupyter documentation.
https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Importing%20Notebooks.html
'''

import io, logging, os, sys, types

from IPython import get_ipython
from nbformat import read
from IPython.core.interactiveshell import InteractiveShell


class NamespaceManager:
    def __init__(self, namespace):
        self.namespace = namespace
        self.shell = InteractiveShell.instance()
        self._old_ns = None

    def __enter__(self):
        self._old_ns = self.shell.user_ns
        self.shell.user_ns = self.namespace
        return self

    def __exit__(self, *args, **kws):
        self.shell.user_ns = self._old_ns


class PeaceAndQuiet:
    def __init__(self):
        self._old_stdout = None
        self._old_stderr = None

    def __enter__(self):
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def __exit__(self, *args, **kws):
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr


def find_notebook(fullname, path=None):
    '''find a notebook, given its fully qualified name and an optional path

    This turns 'foo.bar' into 'foo/bar.ipynb'
    and tries turning 'Foo_Bar' into 'Foo Bar' if Foo_Bar
    does not exist.
    '''
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for dirpath in path:
        nb_path = os.path.join(dirpath, name + '.ipynb')
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find 'Notebook Name.ipynb'
        nb_path = nb_path.replace('_', ' ')
        if os.path.isfile(nb_path):
            return nb_path


class NotebookLoader:
    def __init__(self, path=None):
        self.path = path

    def load_module(self, fullname):
        '''import a notebook as a module'''
        path = find_notebook(fullname, self.path)

        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = read(f, 4)

        # create the module and add it to sys.modules
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        sys.modules[fullname] = mod

        with PeaceAndQuiet(), NamespaceManager(mod.__dict__) as manager:
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    code = manager.shell.input_transformer_manager.transform_cell(cell.source)
                    try:
                        exec(code, manager.namespace)
                    except Exception as exn:
                        logging.exception('Exception in cell.', exc_info=exn)

        return mod


class NotebookFinder:
    '''Module finder that locates Jupyter Notebooks'''
    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return

        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]


sys.meta_path.append(NotebookFinder())
