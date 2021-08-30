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
    def __init__(self, in_expr=None):
        self._lambda_args = None
        self._lambda_body = None
        if in_expr is not None:
            if isinstance(in_expr, str):
                self.in_expr_tree = ast.parse(in_expr, mode='eval')
            elif in_expr is not None:
                assert isinstance(in_expr, ast.Expression)
                self.in_expr_tree = in_expr
            assert isinstance(self.in_expr_tree.body, ast.Lambda), "Expected lambda expression as argument."
            self.visit(self.in_expr_tree.body)

    def visit_Lambda(self, node):
        if self._lambda_body is None:
            self._lambda_args = [arg.arg for arg in node.args.args]
            self._lambda_body = node.body


class SublambdaMagics:
    def __init__(self, build_lambda_visitor=None):
        self.build_lambda_visitor = build_lambda_visitor or LambdaVisitor

    def build_closure(self, in_expr):
        visitor = self.build_lambda_visitor(in_expr)
        def _sub_closure(*args, **kws):
            assert len(args) == len(visitor._lambda_args)
            result = copy.deepcopy(visitor._lambda_body)
            transformer = NameSubstitutionTransformer(**{k: v for k, v in zip(visitor._lambda_args, args)})
            return ast.fix_missing_locations(transformer.visit(result))
        return _sub_closure

    def inline_lambdas(self, pairs):
        substitutions = {name: self.build_closure(expr) for name, expr in pairs}
        transformer = ParametricSubstitutionTransformer(**substitutions)
        def inliner(source):
            target = ast.parse(source)
            return ast.fix_missing_locations(transformer.visit(target))
        return inliner

    def build_sublambdas(self, cell):
        the_lambdas0 = [ln.split(' ', 1) for ln in cell.split('\n')]
        the_lambdas = [(content[0], content[1])
                    for content in the_lambdas0
                    if len(content) == 2]
        return self.inline_lambdas(the_lambdas)

    def sublambdas(self, transformer_name):
        def binding_sublambdas(cell0, shell):
            inliner = self.build_sublambdas(cell0)
            def the_magic(cell1, shell):
                inlined = inliner(cell1)
                return shell.ex(compile(inlined, '<substituted-string>', 'exec'))
            shell.user_global_ns[transformer_name] = the_magic
            return inliner
        return binding_sublambdas


DEFAULT_SUBLAMBDA = SublambdaMagics()
build_closure = DEFAULT_SUBLAMBDA.build_closure
inline_lambdas = DEFAULT_SUBLAMBDA.inline_lambdas
build_sublambdas = DEFAULT_SUBLAMBDA.build_sublambdas
sublambdas = DEFAULT_SUBLAMBDA.sublambdas


class RenameNameTransformer(ast.NodeTransformer):
    def __init__(self, names=None):
        if names is None:
            names = []
        self.symbols = {name: None for name in names}

    def visit_Lambda(self, node):
        for arg in node.args.args:
            self.symbols[arg.arg] = arg.arg
        return self.generic_visit(node)

    def visit_NamedExpr(self, node):
        rhs = self.visit(node.value)
        lhs = self.visit(node.target)
        return ast.NamedExpr(lhs, rhs)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            new_id = f'${node.id}'
            self.symbols[node.id] = new_id
            return ast.Name(new_id, node.ctx)
        elif node.id in self.symbols:
            sub_id = self.symbols[node.id]
            if sub_id is not None:
                return ast.Name(sub_id, node.ctx)
        return self.generic_visit(node)


def build_hygienic_visitor(in_expr):
    in_expr_tree = ast.parse(in_expr, mode='eval')
    clean_expr_tree = RenameNameTransformer().visit(in_expr_tree)
    return LambdaVisitor(clean_expr_tree)


HYGIENIC_SUBLAMBDAS = SublambdaMagics(build_hygienic_visitor)
hygienic_sublambdas = HYGIENIC_SUBLAMBDAS.sublambdas
