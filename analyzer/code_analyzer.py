import ast


def analyze_python_code(code: str) -> dict[str, int]:
    """Return deterministic structural metrics for syntactically valid Python."""
    tree = ast.parse(code)
    assigned_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    argument_names = {
        argument.arg
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
        for argument in (
            node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            + ([node.args.vararg] if node.args.vararg else [])
            + ([node.args.kwarg] if node.args.kwarg else [])
        )
    }
    nodes = list(ast.walk(tree))
    return {
        "lines": len(code.splitlines()),
        "functions": sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in nodes
        ),
        "classes": sum(isinstance(node, ast.ClassDef) for node in nodes),
        "loops": sum(isinstance(node, (ast.For, ast.AsyncFor, ast.While)) for node in nodes),
        "conditions": sum(isinstance(node, (ast.If, ast.IfExp)) for node in nodes),
        "imports": sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in nodes),
        "variables": len(assigned_names | argument_names),
    }
