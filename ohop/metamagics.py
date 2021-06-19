from ast import parse
from inspect import signature
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)


@magics_class
class MetaMagics(Magics):
    
    @line_magic
    def myline(self, line):
        return self.shell.ev(compile(parse(line, mode='eval'), '<line-magic>', 'eval'))

    @cell_magic
    def mycell(self, line, cell):
        if line:
            myline_ast = parse(line, mode='eval')
            myline_co = compile(myline_ast, '<cell-magic-line>', 'eval')
            myline = self.shell.ev(myline_co)
        else:
            myline = None
        if callable(myline):
            myline_sig = signature(myline)
            myline_param_count = len(myline_sig.parameters)
            if myline_param_count == 1:
                return myline(cell)
            elif myline_param_count > 1:
                return myline(cell, self.shell)
        else:
            mycell_ast = parse(cell, mode='exec')
            mycell_co = compile(mycell_ast, '<cell-magic-cell>', 'exec')
            self.shell.ex(mycell_co)
        return

    @cell_magic
    def mybug(self, _, cell):
        return eval(compile(parse(cell, mode='exec'), '<cell-magic>', 'exec'))


def load_ipython_extension(ipython):
    ipython.register_magics(MetaMagics)
