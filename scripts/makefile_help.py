#!/usr/bin/env python3
"""
Platform-agnostic script to display Makefile help messages.
This replaces the grep-based help functionality in the Makefile for Windows compatibility.
"""

import os
import re
import sys
from pathlib import Path


def find_makefile():
    """Find the Makefile in the current directory or parent directories."""
    current_dir = Path.cwd()
    
    # Look for Makefile in current directory first
    makefile_paths = [
        current_dir / "Makefile",
        current_dir / "makefile",
        current_dir / "GNUmakefile"
    ]
    
    for makefile_path in makefile_paths:
        if makefile_path.exists():
            return makefile_path
    
    # If not found, look in parent directories up to 3 levels
    for i in range(3):
        current_dir = current_dir.parent
        for makefile_name in ["Makefile", "makefile", "GNUmakefile"]:
            makefile_path = current_dir / makefile_name
            if makefile_path.exists():
                return makefile_path
    
    return None


def extract_help_messages(makefile_path):
    """Extract help messages from the Makefile."""
    help_messages = []
    
    try:
        with open(makefile_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading Makefile: {e}", file=sys.stderr)
        return []
    
    # Pattern to match lines like: "target: ## Description"
    pattern = re.compile(r'^([a-zA-Z_-]+):.*?##\s*(.*)$')
    
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            target = match.group(1)
            description = match.group(2)
            help_messages.append((target, description))
    
    return help_messages


def display_help(help_messages):
    """Display the help messages in a formatted way."""
    if not help_messages:
        print("No help messages found in Makefile")
        return
    
    print("Available targets:")
    
    # Calculate the maximum width for target names for proper alignment
    max_target_width = max(len(target) for target, _ in help_messages) if help_messages else 0
    max_target_width = max(max_target_width, 15)  # Minimum width of 15
    
    # Sort targets alphabetically
    help_messages.sort(key=lambda x: x[0])
    
    for target, description in help_messages:
        print(f"  {target:<{max_target_width}} {description}")


def main():
    """Main function to find Makefile and display help."""
    makefile_path = find_makefile()
    
    if not makefile_path:
        print("Error: No Makefile found in current directory or parent directories", file=sys.stderr)
        sys.exit(1)
    
    print(f"Reading help from: {makefile_path}")
    help_messages = extract_help_messages(makefile_path)
    display_help(help_messages)


if __name__ == "__main__":
    main()
