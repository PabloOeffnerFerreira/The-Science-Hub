import os
import re
import shutil

def improved_refactor_window_tools(directory):
    modified_files = {}

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "hub.py":
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            updated_lines = []
            modified = False

            lines = content.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i]
                func_match = re.match(r'\s*def (open_[a-zA-Z0-9_]+)\s*\(\):', line)
                if func_match:
                    func_name = func_match.group(1)
                    start_idx = i
                    indent = len(line) - len(line.lstrip())
                    i += 1

                    while i < len(lines) and (lines[i].strip() == "" or len(lines[i]) - len(lines[i].lstrip()) > indent):
                        i += 1

                    block = lines[start_idx:i]
                    var_name = None

                    for l in block:
                        match_var = re.search(r'(\w+)\s*=\s*tk\.Toplevel\(\)', l)
                        if match_var:
                            var_name = match_var.group(1)
                            break

                    if var_name:
                        modified = True
                        new_block = [f"def {func_name}():",
                                     f"    def create_window():"]

                        for l in block[1:]:
                            new_block.append("    " + l)
                        new_block.append(f"        return {var_name}")
                        label = func_name.replace("open_", "").replace("_", " ").title()
                        new_block.append(f"    register_window(\"{label}\", create_window)")
                        updated_lines.extend(new_block)
                    else:
                        updated_lines.extend(block)
                else:
                    updated_lines.append(line)
                    i += 1

            if modified:
                updated_content = "\n".join(updated_lines)
                if "register_window" not in updated_content:
                    updated_content = "from utils import register_window  # [AUTO-REFRACTORED]\n" + updated_content
                shutil.copy(filepath, filepath + ".bak")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                modified_files[filename] = True

    return list(modified_files.keys())

# Run on provided simulation path
test_path = "C:/Users/Pablo/Desktop/Code/Hub"
improved_refactor_window_tools(test_path)