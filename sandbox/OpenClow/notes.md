In the **OpenClaw** architecture (as of early 2026), the progressive disclosure mechanism is primarily governed by the **Skill** system.

The core file that determines *what* is disclosed is usually a **`skill.md`** (or `SKILL.md`) located within each tool's directory. This follows a 3-layer disclosure pattern designed to save tokens and prevent "context pollution":

1. **Layer 1 (The Hook):** At startup, OpenClaw only reads the **YAML frontmatter** (name and description) of every `skill.md`.
2. **Layer 2 (The Activation):** If the agent determines the description matches the user's intent, it then loads the full **Instructions** and **Logic** from that specific `skill.md`.
3. **Layer 3 (Deep Context):** Specific implementation details or large documentation files are linked as sub-files (e.g., `docs/api_details.md`) and only read if the agent explicitly calls a "read" tool.

------

### Meta-Extractor Script

To see how a library would be "disclosed," you can use this script. It uses the TypeScript compiler API to extract function signatures and JSDoc comments—exactly the kind of metadata OpenClaw's `scanner.ts` or `SearchToolsService.ts` would use to generate a Layer 1/Layer 2 summary.

TypeScript

```
// extract_metadata.ts
import * as ts from 'typescript';
import * as fs from 'fs';

/**
 * This script simulates the "Disclosure Discovery" phase of OpenClaw.
 * It parses a TypeScript file and extracts only the metadata relevant 
 * for an AI agent's initial context window.
 */

interface FunctionMetadata {
    name: string;
    description: string;
    parameters: { name: string; type: string; description: string }[];
    returnType: string;
}

function extractMetadata(filePath: string): FunctionMetadata[] {
    const program = ts.createProgram([filePath], { allowJs: true });
    const sourceFile = program.getSourceFile(filePath);
    const checker = program.getTypeChecker();
    const metadata: FunctionMetadata[] = [];

    if (!sourceFile) {
        console.error("Could not find source file.");
        return [];
    }

    ts.forEachChild(sourceFile, (node) => {
        // We only care about exported functions for disclosure
        if (ts.isFunctionDeclaration(node) && node.name) {
            const symbol = checker.getSymbolAtLocation(node.name);
            if (symbol) {
                const details: FunctionMetadata = {
                    name: node.name.text,
                    description: ts.displayPartsToString(symbol.getDocumentationComment(checker)),
                    parameters: node.parameters.map(param => ({
                        name: param.name.getText(),
                        type: checker.typeToString(checker.getTypeAtLocation(param)),
                        description: "" // JSDoc tags could be parsed here for deeper disclosure
                    })),
                    returnType: checker.typeToString(checker.getReturnTypeOfSignature(checker.getSignatureFromDeclaration(node)!))
                };
                metadata.push(details);
            }
        }
    });

    return metadata;
}

// EXECUTION
const targetFile = 'example_lib.ts'; // Replace with your target file
const disclosureData = extractMetadata(targetFile);

console.log("--- PROGRESSIVE DISCLOSURE PAYLOAD ---");
console.log(JSON.stringify(disclosureData, null, 2));

/**
 * OpenClaw would take this 'disclosureData' and inject 
 * ONLY the 'name' and 'description' into Layer 1.
 */
```

### How to use this:

1. **Install dependencies**: `npm install typescript @types/node`
2. **Run with ts-node**: `npx ts-node extract_metadata.ts`

### Why this matters for OpenClaw

If you check the OpenClaw source (specifically the `packages/gateway` or `packages/runtime` folders), you'll see a service that performs this exact "Thinning" of the code.

By extracting just the **signatures**, OpenClaw allows an agent to "know" a function exists (Disclosure) without having to "see" the 500 lines of implementation code inside it, keeping the **context window** clean and the response time fast.

**Would you like me to show you how to format this metadata into a `skill.md` file that OpenClaw can natively import?**

























In Python, achieving the same "progressive disclosure" logic requires parsing the code's structure without executing it. We can use the built-in `ast` (Abstract Syntax Tree) module to find functions, their arguments, and their docstrings.

In the context of **OpenClaw**, this script mimics the "Scanner" service that prepares a library's metadata for the AI agent's initial lookup.

### Python Metadata Extractor

This script parses a target Python file and extracts the "surface area" (the signature) while ignoring the implementation logic.

Python

```
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
    # Create a dummy file for demonstration
    example_code = """
def calculate_risk(amount: float, credit_score: int) -> str:
    \"\"\"
    Analyzes the financial risk of a loan application.
    This would be the 'Layer 1' disclosure text.
    \"\"\"
    # Implementation details are hidden from the AI initially
    return "High" if credit_score < 600 else "Low"

def _private_helper():
    \"\"\"This should be ignored by the scanner.\"\"\"
    pass
    """
    
    with open("example_lib.py", "w") as f:
        f.write(example_code)

    # Run the scanner
    print("--- OPENCLAW DISCLOSURE MOCK ---")
    results = scan_file("example_lib.py")
    print(json.dumps(results, indent=2))
```

------

### How this fits OpenClaw's logic

When OpenClaw "discloses" information, it follows an **Information Hierarchy**. By using the script above, you are essentially creating the "Summary" layer of that hierarchy.

### Disclosure Breakdown

- **The Script Output:** Provides the `name` and `description`.
- **Layer 1 (The Hook):** OpenClaw shows the agent just the `name` and the first sentence of the `description`.
- **Layer 2 (The Tool Definition):** If the agent is interested, OpenClaw provides the `parameters` and `return_annotation` so the agent knows how to format the call.
- **Layer 3 (The Execution):** Only when the agent calls the function does the actual code inside the `FunctionDef` (the part we didn't extract) actually run.

**Would you like me to show you how to wrap this into a FastAPI endpoint that acts as a "Disclosure Server" for an AI agent?**

