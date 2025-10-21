from pathlib import Path
import os, shutil, json, sys

ALLOWED = {".md", ".pdf", ".docx", ".xlsx", ".yaml", ".yml"}

def pick_top_to_open(root: Path, limit: int = 8):
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED]
    def weight(p: Path):
        name = p.name.lower()
        w = 0
        if "readme" in name or "overview" in name: w += 100
        if "guide" in name: w += 50
        if p.suffix.lower() == ".md": w += 10
        return (-w, len(str(p)))
    return sorted(files, key=weight)[:limit]

def main():
    repo = Path.cwd()
    src = os.environ.get("ONTOLOGY_DOCS_DIR", "")
    if not src:
        print("ERROR: ONTOLOGY_DOCS_DIR is not set", file=sys.stderr); sys.exit(2)
    src_dir = Path(src)
    if not src_dir.exists():
        print(f"ERROR: Source not found → {src_dir}", file=sys.stderr); sys.exit(2)

    dst = repo / "docs" / "ontology_unified"
    dst.mkdir(parents=True, exist_ok=True)

    # mirror copy
    copied = 0
    for sp in src_dir.rglob("*"):
        if sp.is_file() and sp.suffix.lower() in ALLOWED:
            rel = sp.relative_to(src_dir)
            dp = dst / rel
            dp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, dp)
            copied += 1

    # preload_docs.yaml
    top_n = 8
    if len(sys.argv) >= 3 and sys.argv[1] == "--open-top":
        try: top_n = int(sys.argv[2])
        except: pass
    open_list = pick_top_to_open(dst, limit=top_n)
    hooks = repo / ".cursor" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    yaml_lines = ["preload_docs:"]
    for p in open_list:
        rel = p.relative_to(repo)
        yaml_lines.append(f"  - path: \"{rel.as_posix()}\"")
        yaml_lines.append(f"    open_on_start: true")
    (hooks / "preload_docs.yaml").write_text("\n".join(yaml_lines), encoding="utf-8")

    # workspace.json merge
    cfg_dir = repo / ".cursor" / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    ws = cfg_dir / "workspace.json"
    data = {"active_tabs": ["Docs","Code","Git","Rules","Terminals"],
            "docs_default": [],
            "rules_path": ".cursor/rules/",
            "git_auto_init": True}
    if ws.exists():
        try: data.update(json.loads(ws.read_text(encoding="utf-8")))
        except: pass
    for p in open_list:
        rel = p.relative_to(repo).as_posix()
        if rel not in data.setdefault("docs_default", []):
            data["docs_default"].append(rel)
    ws.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Synced files: {copied}; open_on_start entries: {len(open_list)}")

if __name__ == "__main__":
    main()
