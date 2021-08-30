import unittest
import IPython

from .. import sublambda


SUBLAMBDA_CELL = '''f lambda x: (z := x ** 2, z + x + 1)[-1]'''

TARGET_CELL = '''def wonkify():
    z = 42
    f(99)
    return z
'''


class TestSublambdas(unittest.TestCase):
    def _run_sublambdas(self, sublambdas):
        ipython = IPython.InteractiveShell()
        sublambdas('sublambdas_result')(SUBLAMBDA_CELL, ipython)
        ipython.user_global_ns.get('sublambdas_result')(TARGET_CELL, ipython)
        return ipython.user_global_ns['wonkify']()

    def test_sublambdas(self):
        '''Ensure that generic lambda substitution has bad hygiene.
        '''
        result = self._run_sublambdas(sublambda.sublambdas)
        self.assertEqual(result, 9801)

    def test_hygienic_sublambdas(self):
        '''Ensure that hygienic lambda substitution has better hygiene.
        '''
        result = self._run_sublambdas(sublambda.hygienic_sublambdas)
        self.assertEqual(result, 42)


if __name__ == '__main__':
    unittest.main()
