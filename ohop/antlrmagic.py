'''Module for inlining ANTLR grammars in Jupyter.
'''
import importlib
import os
import re
import sys
import subprocess
import tempfile

GRAMMAR_RE = re.compile(r'^grammar[ \t]+(\w+)[ \t]*;')

def antlrify(cell, shell):
    # Step 1: Create a temporary directory, and dump the input into a grammar file.
    # Figure out the grammar name from the cell.
    grammar_matches = GRAMMAR_RE.findall(cell)
    if len(grammar_matches) == 0:
        raise ValueError('Could not find grammar name in ANTLR grammar.')
    grammar_name = grammar_matches[-1]
    with tempfile.TemporaryDirectory() as temp_dir:
        grammar_path = os.path.join(temp_dir, f'{grammar_name}.g4')
        with open(grammar_path, 'w') as grammar_file:
            grammar_file.write(cell)
        # Step 2: Run ANTLR, piping stdout and stderr to console.
        antlr_result = subprocess.run(
            ['antlr4', '-o', temp_dir, '-Dlanguage=Python3', grammar_path],
            capture_output=True)
        if len(antlr_result.stderr) > 0:
            sys.stderr.write(antlr_result.stderr)
        if len(antlr_result.stdout) > 0:
            sys.stdout.write(antlr_result.stdout)
        if antlr_result.returncode != 0:
            raise subprocess.SubprocessError(f'ANTLR returned non-zero exit status')
        # Step 3: Find ANTLR's output modules and import them into the shell.
        sys.path.append(temp_dir)
        try:
            lexer_module = grammar_name + 'Lexer'
            shell.user_global_ns[lexer_module] = importlib.import_module(lexer_module)
            print(f'Imported {lexer_module}')
            parser_module = grammar_name + 'Parser'
            shell.user_global_ns[parser_module] = importlib.import_module(parser_module)
            print(f'Imported {parser_module}')
            listener_module = grammar_name + 'Listener'
            shell.user_global_ns[listener_module] = importlib.import_module(listener_module)
            print(f'Imported {listener_module}')
        finally:
            sys.path.pop()
