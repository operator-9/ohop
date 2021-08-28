'''Lambda substitution library from Episodes 10, 11, and 12...
'''
import ast, copy


class NameSubstitutionTransformer(ast.NodeTransformer):
    def __init__(self, **substitutions):
        self.substitutions = substitutions
        
    def visit_Name(self, node):
        if node.id in self.substitutions and isinstance(node.ctx, ast.Load):
            substitution = self.substitutions[node.id]
            return substitution
        return self.generic_visit(node)


class ParametricSubstitutionTransformer(ast.NodeTransformer):
    def __init__(self, **substitutions):
        self.substitutions = substitutions
        
    def visit_Call(self, node):
        func = node.func
        fire = (
            isinstance(func, ast.Name) and
            func.id in self.substitutions and
            isinstance(func.ctx, ast.Load) and
            not node.keywords
        )
        if fire:
            substitution = self.substitutions[func.id](*node.args)
            return substitution
        return self.generic_visit(node)


class LambdaVisitor(ast.NodeVisitor):
    def __init__(self, in_expr):
        self.in_expr_tree = ast.parse(in_expr, mode='eval')
        assert isinstance(self.in_expr_tree.body, ast.Lambda), "Expected lambda expression as argument."
        self._lambda_args = None
        self._lambda_body = None
        self.visit(self.in_expr_tree.body)

    def visit_Lambda(self, node):
        if self._lambda_body is None:
            self._lambda_args = [arg.arg for arg in node.args.args]
            self._lambda_body = node.body


def build_closure(in_expr):
    visitor = LambdaVisitor(in_expr)
    def _sub_closure(*args, **kws):
        assert len(args) == len(visitor._lambda_args)
        result = copy.deepcopy(visitor._lambda_body)
        transformer = NameSubstitutionTransformer(**{k: v for k, v in zip(visitor._lambda_args, args)})
        return ast.fix_missing_locations(transformer.visit(result))
    return _sub_closure


def inline_lambdas(pairs):
    substitutions = {name: build_closure(expr) for name, expr in pairs}
    transformer = ParametricSubstitutionTransformer(**substitutions)
    def inliner(source):
        target = ast.parse(source)
        return ast.fix_missing_locations(transformer.visit(target))
    return inliner


def build_sublambdas(cell):
    the_lambdas0 = [ln.split(' ', 1) for ln in cell.split('\n')]
    the_lambdas = [(content[0], content[1])
                   for content in the_lambdas0
                   if len(content) == 2]
    return inline_lambdas(the_lambdas)


def sublambdas(transformer_name):
    def binding_sublambdas(cell0, shell):
        inliner = build_sublambdas(cell0)
        def the_magic(cell1, shell):
            inlined = inliner(cell1)
            return shell.ex(compile(inlined, '<substituted-string>', 'exec'))
        shell.user_global_ns[transformer_name] = the_magic
        return inliner
    return binding_sublambdas
