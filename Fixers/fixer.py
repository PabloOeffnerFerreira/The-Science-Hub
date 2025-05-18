import os
import re

def fix_return_win_in_files(directory):
    fixed_files = []

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "hub.py":
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            defined_vars = set()
            new_lines = []

            for line in lines:
                var_match = re.search(r'^.*?(\w+)\s*=\s*tk\.Toplevel\(\)', line)
                if var_match:
                    defined_vars.add(var_match.group(1))

                if re.match(r'\s*return win\b', line):
                    if 'win' not in defined_vars:
                        modified = True
                        # Try fallback if only one var is known
                        if len(defined_vars) == 1:
                            real_name = list(defined_vars)[0]
                            new_lines.append(line.replace("return win", f"return {real_name}"))
                        else:
                            new_lines.append("# [FIXME] 'win' not defined. Please replace manually or confirm below.\n")
                            new_lines.append("# " + line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                fixed_files.append(filename)

    return fixed_files

fix_return_win_in_files("C:/Users/Pablo/Desktop/Code/Hub")
