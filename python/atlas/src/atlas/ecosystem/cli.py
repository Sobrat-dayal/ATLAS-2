"""
ATLAS Developer CLI (`atlas-dev`) for Stage 149.
Command-line utility supporting agent project initialization, package validation,
tool schema testing, and `.atlas-agent` bundle packaging.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional

from atlas.ecosystem.packages import AgentPackageManager
from atlas.ecosystem.tools import CustomToolRegistryService


def init_agent_project(target_dir: str, name: str) -> int:
    """Scaffolds an ATLAS Agent package project structure."""
    os.makedirs(os.path.join(target_dir, "agent"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "dependencies"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "permissions"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "docs"), exist_ok=True)

    slug = name.lower().replace(" ", "-")
    manifest = {
        "manifest_version": "1.0",
        "package_id": f"pkg.{slug}",
        "name": name,
        "version": "1.0.0",
        "kind": "atlas-agent",
        "description": f"Institutional agent for {name}.",
        "publisher": {"id": "dev-local", "name": "Developer"},
        "compatibility": {"atlas": ">=1.0.0"},
        "requirements": {
            "capabilities": ["text-generation", "structured-output"],
            "tools": ["atlas.research.sec_filings_search"],
        },
        "permissions": ["READ_RESEARCH"],
        "entrypoint": "agent/definition.json",
    }
    with open(os.path.join(target_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    definition = {
        "name": name,
        "description": f"Autonomous financial intelligence agent: {name}.",
        "role": "RESEARCHER",
        "model_id": "gpt-4o",
        "execution_limits": {"max_tokens": 4096},
        "instructions_ref": "agent/instructions.md",
    }
    with open(os.path.join(target_dir, "agent", "definition.json"), "w", encoding="utf-8") as f:
        json.dump(definition, f, indent=2)

    instructions = f"# System Prompt: {name}\nYou are an institutional financial intelligence agent.\n"
    with open(os.path.join(target_dir, "agent", "instructions.md"), "w", encoding="utf-8") as f:
        f.write(instructions)

    readme = f"# {name}\n\nATLAS Agent Package definition.\n"
    with open(os.path.join(target_dir, "docs", "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Scaffolded agent project '{name}' in '{target_dir}'.")
    return 0


def validate_package_file(package_path: str) -> int:
    """Validates an existing .atlas-agent archive."""
    if not os.path.isfile(package_path):
        print(f"Error: File '{package_path}' does not exist.", file=sys.stderr)
        return 1

    with open(package_path, "rb") as f:
        data = f.read()

    pm = AgentPackageManager()
    res = pm.validate_package_bytes(data)
    if res.is_valid:
        print(f"SUCCESS: Package '{res.package_id}' (v{res.version}) is valid.")
        print(f"Files: {res.file_count}, Total bytes: {res.total_bytes}, Integrity verified: {res.checksum_verified}")
        return 0
    else:
        print(f"VALIDATION FAILED for '{package_path}':", file=sys.stderr)
        for err in res.errors:
            print(f" - {err}", file=sys.stderr)
        return 2


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="atlas-dev", description="ATLAS Developer Ecosystem CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init agent
    init_parser = subparsers.add_parser("init", help="Initialize a project")
    init_parser.add_argument("type", choices=["agent"], help="Project type")
    init_parser.add_argument("--name", default="Custom Research Agent", help="Agent name")
    init_parser.add_argument("--dir", default="./my-agent", help="Target directory")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate an .atlas-agent package")
    validate_parser.add_argument("package_path", help="Path to .atlas-agent file")

    args = parser.parse_args(argv)

    if args.command == "init" and args.type == "agent":
        return init_agent_project(args.dir, args.name)
    elif args.command == "validate":
        return validate_package_file(args.package_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())

