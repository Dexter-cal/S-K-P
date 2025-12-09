import random
import string
import ast
import base64

def generate_random_name(length=8):
    """Generates a random alphanumeric name."""
    return ''.join(random.choices(string.ascii_letters, k=length))

class CodeTransformer(ast.NodeTransformer):
    """
    AST transformer to rename variables, functions, and obfuscate strings.
    """
    def __init__(self):
        self.name_map = {}
        self.obfuscated_strings = {}

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            if node.id not in self.name_map:
                self.name_map[node.id] = generate_random_name()
            node.id = self.name_map[node.id]
        return node

    def visit_FunctionDef(self, node):
        if node.name not in self.name_map:
            self.name_map[node.name] = generate_random_name()
        node.name = self.name_map[node.name]
        self.generic_visit(node)
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if node.value not in self.obfuscated_strings:
                encoded_string = base64.b64encode(node.value.encode()).decode()
                self.obfuscated_strings[node.value] = encoded_string

            # Replace the string with a decoding expression
            b64_name = self.obfuscated_strings[node.value]
            new_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Call(
                        func=ast.Name(id='base64', ctx=ast.Load()),
                        args=[ast.Constant(value=b64_name)],
                        keywords=[]
                    ),
                    attr='decode',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
            ast.copy_location(new_node, node)
            return new_node
        return node

def morph_code(source_code):
    """
    Applies polymorphic transformations to a Python script.
    """
    try:
        # 1. Parse the code into an AST
        tree = ast.parse(source_code)

        # 2. Rename variables and functions, and obfuscate strings
        transformer = CodeTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        # 3. Add necessary imports for obfuscated strings
        new_tree.body.insert(0, ast.Import(names=[ast.alias(name='base64', asname=None)]))
        ast.fix_missing_locations(new_tree)

        # 4. Scramble the order of top-level functions and classes
        top_level_nodes = [n for n in new_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        other_nodes = [n for n in new_tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        random.shuffle(top_level_nodes)
        new_tree.body = other_nodes + top_level_nodes

        # 5. Insert junk code (simple version)
        for node in new_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                junk_var = generate_random_name()
                junk_val = random.randint(1000, 9999)
                junk_node = ast.Assign(targets=[ast.Name(id=junk_var, ctx=ast.Store())], value=ast.Constant(value=junk_val))
                node.body.insert(0, junk_node)

        # 6. Unparse the AST back into code
        morphed_code = ast.unparse(new_tree)

        return morphed_code

    except Exception as e:
        logging.error(f"Failed to morph code: {e}")
        return source_code # Return original on failure
