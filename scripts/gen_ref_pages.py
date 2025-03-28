"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()
ignore_folders = ['tests', 'scripts', 'utils', '.venv']
root = Path(__file__).parent.parent
src = root 


for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)
    if parts[0] in ignore_folders or 'lib' in parts:
        continue

    if parts[-1] == "__init__":
        continue
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()  

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")
    
    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))
    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)  

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:  
    nav_file.writelines(nav.build_literate_nav())  