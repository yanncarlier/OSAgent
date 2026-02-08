# extract_metadata.py
import ast
import json
import os

class DisclosureScanner(ast.NodeVisitor):
    """
    Scans Python source code to extract metadata for progressive disclosure.
    This mimics how OpenClaw identifies 'Skills' without loading full logic.
    """
    def __init__(self):
        self.metadata = []

    def visit_FunctionDef(self, node):
        # We only want top-level functions or public methods (not starting with _)
        if not node.name.startswith('_'):
            func_data = {
                "name": node.name,
                "description": ast.get_docstring(node) or "No description provided.",
                "parameters": self._get_args(node),
                "return_annotation": self._get_return_type(node),
                "line_number": node.lineno
            }
            self.metadata.append(func_data)
        self.generic_visit(node)

    def _get_args(self, node):
        args = []
        for arg in node.args.args:
            # Extract type hints if they exist
            arg_type = "Any"
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    arg_type = arg.annotation.id
                elif isinstance(arg.annotation, ast.Constant):
                    arg_type = arg.annotation.value
            
            args.append({
                "name": arg.arg,
                "type": arg_type
            })
        return args

    def _get_return_type(self, node):
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
        return "Unknown"

def scan_file(file_path):
    if not os.path.exists(file_path):
        return {"error": f"File {file_path} not found."}

    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    scanner = DisclosureScanner()
    scanner.visit(tree)
    return scanner.metadata

if __name__ == "__main__":
    # Scan real files from the context directory instead of creating a dummy file.
    CONTEXT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../context_files"))

    def scan_markdown(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [l.rstrip() for l in f]
        except Exception as e:
            return {"error": str(e)}

        title = None
        description_lines = []
        in_para = False
        for ln in lines:
            if not title and ln.startswith("#"):
                title = ln.lstrip('#').strip()
            if ln.strip() == "":
                if in_para:
                    break
                continue
            # accumulate first paragraph (non-empty consecutive lines)
            description_lines.append(ln)
            in_para = True

        if not title and lines:
            # fallback to first non-empty line
            for ln in lines:
                if ln.strip():
                    title = ln.strip()
                    break

        description = "\n".join(description_lines).strip() if description_lines else "No description available."
        return {"type": "markdown", "title": title or os.path.basename(path), "description": description}

    def scan_generic(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(2048)
        except Exception as e:
            return {"error": str(e)}
        return {"type": "generic", "summary": content[:1024]}

    all_results = []
    if not os.path.isdir(CONTEXT_DIR):
        print(f"Context directory not found: {CONTEXT_DIR}")
        sys.exit(1)

    for root, _, files in os.walk(CONTEXT_DIR):
        for fname in sorted(files):
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, CONTEXT_DIR)
            entry = {"file": rel}
            if fname.endswith('.py'):
                try:
                    funcs = scan_file(path)
                    entry.update({"type": "python", "functions": funcs})
                except Exception as e:
                    entry.update({"error": str(e)})
            elif fname.endswith(('.md', '.markdown', '.txt')):
                entry.update(scan_markdown(path))
            else:
                entry.update(scan_generic(path))

            all_results.append(entry)

    print("--- CONTEXT FILES METADATA ---")
    print(json.dumps(all_results, indent=2, ensure_ascii=False))