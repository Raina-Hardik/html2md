"""File and directory processing utilities."""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from .converter import HTMLToMarkdownConverter


class FileProcessor:
    """Handles file and directory operations for HTML to Markdown conversion."""

    def __init__(self, converter: HTMLToMarkdownConverter):
        """Initialize with a converter instance.

        Args:
            converter: HTMLToMarkdownConverter instance
        """
        self.converter = converter

    def find_html_files(
        self, path: Union[str, Path], recursive: bool = True
    ) -> List[Path]:
        """Find all HTML files in a path.

        Args:
            path: Directory or file path to search
            recursive: Whether to search recursively

        Returns:
            List of HTML file paths
        """
        path = Path(path)
        html_files = []

        if path.is_file():
            if self._is_html_file(path):
                html_files.append(path)
        elif path.is_dir():
            pattern = "**/*.html" if recursive else "*.html"
            html_files.extend(path.glob(pattern))
            # Also check for .htm files
            pattern = "**/*.htm" if recursive else "*.htm"
            html_files.extend(path.glob(pattern))

        return sorted(html_files)

    def _is_html_file(self, file_path: Path) -> bool:
        """Check if a file is an HTML file.

        Args:
            file_path: Path to check

        Returns:
            True if file is HTML
        """
        return file_path.suffix.lower() in [".html", ".htm"]

    def generate_output_path(
        self,
        input_path: Path,
        base_input_dir: Path,
        output_dir: Optional[Path] = None,
        flatten: bool = False,
        rename_conflicts: bool = False,
    ) -> Path:
        """Generate output path for converted file.

        Args:
            input_path: Original HTML file path
            base_input_dir: Base directory for input files
            output_dir: Output directory (None to convert in place)
            flatten: Whether to flatten directory structure
            rename_conflicts: Whether to rename conflicting files

        Returns:
            Output path for Markdown file
        """
        # Change extension to .md
        md_filename = input_path.stem + ".md"

        if output_dir is None:
            # Convert in place
            return input_path.parent / md_filename

        output_dir = Path(output_dir)

        if flatten:
            # Flatten structure - all files go to output_dir root
            if rename_conflicts:
                # Create hierarchical name: folder_subfolder_filename.md
                try:
                    relative_path = input_path.relative_to(base_input_dir)
                    parts = list(relative_path.parent.parts) + [input_path.stem]
                    flat_name = "_".join(parts) + ".md"
                    return output_dir / flat_name
                except ValueError:
                    # If relative_to fails, just use filename
                    return output_dir / md_filename
            else:
                return output_dir / md_filename
        else:
            # Preserve directory structure
            try:
                relative_path = input_path.relative_to(base_input_dir)
                return output_dir / relative_path.parent / md_filename
            except ValueError:
                # If relative_to fails, put in output_dir root
                return output_dir / md_filename

    def check_conflicts(
        self, file_mapping: Dict[Path, Path]
    ) -> Tuple[Dict[Path, Path], Set[Path]]:
        """Check for output file conflicts.

        Args:
            file_mapping: Mapping of input paths to output paths

        Returns:
            Tuple of (conflict-free mapping, conflicted paths)
        """
        output_counts: Dict[Path, List[Path]] = {}

        # Group input files by output path
        for input_path, output_path in file_mapping.items():
            if output_path not in output_counts:
                output_counts[output_path] = []
            output_counts[output_path].append(input_path)

        # Find conflicts
        conflicts = set()
        clean_mapping = {}

        for output_path, input_paths in output_counts.items():
            if len(input_paths) == 1:
                clean_mapping[input_paths[0]] = output_path
            else:
                conflicts.update(input_paths)

        return clean_mapping, conflicts

    def process_single_file(
        self,
        input_file: Path,
        output_file: Path,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> Tuple[bool, str]:
        """Process a single HTML file.

        Args:
            input_file: Input HTML file path
            output_file: Output Markdown file path
            overwrite: Whether to overwrite existing files
            dry_run: Whether to perform a dry run

        Returns:
            Tuple of (success, message)
        """
        if output_file.exists() and not overwrite:
            return False, f"Output file exists: {output_file}"

        if dry_run:
            return True, f"Would convert: {input_file} -> {output_file}"

        try:
            output_path = self.converter.convert_file(input_file, output_file)
            return True, f"Converted: {input_file} -> {output_path}"
        except Exception as e:
            return False, f"Failed to convert {input_file}: {str(e)}"

    def remove_original_files(
        self, files: List[Path], dry_run: bool = False
    ) -> Tuple[int, List[str]]:
        """Remove original HTML files after conversion.

        Args:
            files: List of files to remove
            dry_run: Whether to perform a dry run

        Returns:
            Tuple of (removed_count, error_messages)
        """
        removed_count = 0
        errors = []

        for file_path in files:
            if dry_run:
                removed_count += 1
                continue

            try:
                file_path.unlink()
                removed_count += 1
            except Exception as e:
                errors.append(f"Failed to remove {file_path}: {str(e)}")

        return removed_count, errors


class ConflictResolver:
    """Handles filename conflicts during conversion."""

    @staticmethod
    def resolve_with_rename(
        conflicts: Set[Path], base_input_dir: Path, output_dir: Path
    ) -> Dict[Path, Path]:
        """Resolve conflicts by renaming files with directory prefixes.

        Args:
            conflicts: Set of conflicting input paths
            base_input_dir: Base input directory
            output_dir: Output directory

        Returns:
            Mapping of input paths to renamed output paths
        """
        resolved = {}

        for input_path in conflicts:
            try:
                relative_path = input_path.relative_to(base_input_dir)
                parts = list(relative_path.parent.parts) + [input_path.stem]
                renamed = "_".join(parts) + ".md"
                resolved[input_path] = output_dir / renamed
            except ValueError:
                # Fallback to simple renaming
                base_name = input_path.stem
                counter = 1
                while True:
                    candidate = output_dir / f"{base_name}_{counter}.md"
                    if candidate not in resolved.values():
                        resolved[input_path] = candidate
                        break
                    counter += 1

        return resolved

    @staticmethod
    def filter_conflicts(
        conflicts: Set[Path], file_mapping: Dict[Path, Path]
    ) -> Dict[Path, Path]:
        """Filter out conflicting files (skip strategy).

        Args:
            conflicts: Set of conflicting input paths
            file_mapping: Original file mapping

        Returns:
            Filtered mapping without conflicts
        """
        return {k: v for k, v in file_mapping.items() if k not in conflicts}
