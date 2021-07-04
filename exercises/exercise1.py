import ast
import unittest

from .solutions.solution1 import Solution1


class TestSolution1(unittest.TestCase):
    test_cases = [
        ('1 + 2 + 3', '6'),
        ('1 + 2 + zab', '3 + zab'),
        ('1 + 2 + frotz + 3 + 4', '10 + frotz'),
        ('1 + 2 + frotz + "3" + "4"', '3 + frotz + "34"'),
    ]

    def _run_test_case(self, index):
        input_str, output_str = self.test_cases[index]
        transformer = Solution1()
        result = transformer.visit(ast.parse(input_str))
        self.assertEqual(
            ast.dump(result, indent=4),
            ast.dump(ast.parse(output_str), indent=4)
        )

    def test_constant_fold_0(self):
        self._run_test_case(0)

    def test_constant_fold_1(self):
        self._run_test_case(1)

    def test_constant_fold_2(self):
        self._run_test_case(2)

    def test_constant_fold_3(self):
        self._run_test_case(3)

if __name__ == '__main__':
    unittest.main()
