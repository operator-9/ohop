import ast


class Episode8Solution(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                result = ast.Constant(value=left.value + right.value)
            else:
                result = ast.BinOp(left=left, op=ast.Add(), right=right)
            return result
        return self.generic_visit(node)


class Episode9Solution(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if isinstance(right, ast.Constant):
                if (isinstance(left, ast.BinOp) and
                    isinstance(left.op, ast.Add)):
                    fire = False
                    if isinstance(left.left, ast.Constant):
                        llvalue = left.left.value
                        lrvalue = right.value
                        rvalue = left.right
                        if type(llvalue) == type(lrvalue):
                            fire = True
                    elif isinstance(left.right, ast.Constant):
                        llvalue = left.right.value
                        lrvalue = right.value
                        rvalue = left.left
                        if type(llvalue) == type(lrvalue):
                            fire = True
                    if fire:
                        return ast.BinOp(
                            left=ast.Constant(value=llvalue + lrvalue),
                            op=node.op,
                            right=rvalue
                        )
                elif isinstance(left, ast.Constant):
                    return ast.Constant(value=left.value + right.value)
            return ast.BinOp(left=left, op=node.op, right=right)
        return self.generic_visit(node)


Solution1 = Episode9Solution
