"""Main CLI interface for html2md."""

import sys
from pathlib import Path
from typing import Optional, Literal, cast

import click
from colorama import Fore, Style, init
from tqdm import tqdm

from . import __version__
from .converter import HTMLToMarkdownConverter
from .processor import ConflictResolver, FileProcessor

# Initialize colorama for Windows
init(autoreset=True)


def print_banner():
    """Print the tool banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                            HTML2MD v{__version__}                            ║
║                     HTML to Markdown Converter                       ║
║                  Fast • Flexible • Developer Friendly                ║
╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

Examples:
  {Fore.YELLOW}html2md file.html{Style.RESET_ALL}                    # Convert single file
  {Fore.YELLOW}html2md directory/{Style.RESET_ALL}                   # Convert all HTML files in directory  
  {Fore.YELLOW}html2md . --output converted{Style.RESET_ALL}         # Convert to output directory
  {Fore.YELLOW}html2md . --overwrite{Style.RESET_ALL}                # Replace HTML files with Markdown

{Fore.GREEN}For more options, use: html2md --help{Style.RESET_ALL}
"""
    print(banner)


def print_success(message: str, use_tqdm: bool = False):
    """Print a success message."""
    text = f"{Fore.GREEN}✓{Style.RESET_ALL} {message}"
    if use_tqdm:
        tqdm.write(text)
    else:
        print(text)


def print_error(message: str, use_tqdm: bool = False):
    """Print an error message."""
    text = f"{Fore.RED}✗{Style.RESET_ALL} {message}"
    if use_tqdm:
        tqdm.write(text)
    else:
        print(text)


def print_warning(message: str, use_tqdm: bool = False):
    """Print a warning message."""
    text = f"{Fore.YELLOW}⚠{Style.RESET_ALL} {message}"
    if use_tqdm:
        tqdm.write(text)
    else:
        print(text)


def print_info(message: str, use_tqdm: bool = False):
    """Print an info message."""
    text = f"{Fore.CYAN}ℹ{Style.RESET_ALL} {message}"
    if use_tqdm:
        tqdm.write(text)
    else:
        print(text)


@click.command()
@click.argument("path", required=False, type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Output directory for converted files"
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing files and remove original HTML files",
)
@click.option(
    "--flatten",
    is_flag=True,
    help="Flatten directory structure in output (only with --output)",
)
@click.option(
    "--rename", is_flag=True, help="Rename conflicting files with directory prefixes"
)
@click.option("--skip", is_flag=True, help="Skip conflicting files instead of renaming")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be converted without actually converting",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--no-progress-bar", is_flag=True, help="Disable progress bar display")
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Search for HTML files recursively (default: True)",
)
@click.option(
    "--heading-style",
    type=click.Choice(["underlined", "atx", "atx_closed"]),
    default="atx",
    help="Header style (default: atx)",
)
@click.option(
    "--highlight-style",
    type=click.Choice(["double-equal", "html", "bold"]),
    default="double-equal",
    help="Style for highlighted text (default: double-equal)",
)
@click.option(
    "--strong-em-symbol",
    type=click.Choice(["*", "_"]),
    default="*",
    help="Symbol for strong/emphasized text (default: *)",
)
@click.option(
    "--bullets",
    default="*+-",
    help="Characters to use for bullet points (default: *+-)",
)
@click.option(
    "--no-autolinks", is_flag=True, help="Disable automatic URL to link conversion"
)
@click.option("--no-extract-metadata", is_flag=True, help="Disable metadata extraction")
@click.option(
    "--convert-as-inline", is_flag=True, help="Treat content as inline elements only"
)
@click.option("--strip-newlines", is_flag=True, help="Remove newlines from HTML input")
@click.option(
    "--no-escape-asterisks", is_flag=True, help="Disable escaping of * characters"
)
@click.option(
    "--no-escape-underscores", is_flag=True, help="Disable escaping of _ characters"
)
@click.option(
    "--no-escape-misc",
    is_flag=True,
    help="Disable escaping of miscellaneous characters",
)
@click.option(
    "--stream-processing",
    is_flag=True,
    help="Enable streaming processing for large documents",
)
@click.option(
    "--chunk-size",
    type=int,
    default=1024,
    help="Chunk size for streaming processing (default: 1024)",
)
@click.option("--code-language", default="", help="Default language for code blocks")
@click.option(
    "--parser",
    type=click.Choice(["lxml", "html.parser", "auto"]),
    default="auto",
    help="HTML parser to use (default: auto-detect)",
)
@click.option("--wrap", is_flag=True, help="Enable text wrapping")
@click.option(
    "--wrap-width", type=int, default=80, help="Text wrap width (default: 80)"
)
@click.version_option(version=__version__)
def main(
    path: Optional[str],
    output: Optional[str],
    overwrite: bool,
    flatten: bool,
    rename: bool,
    skip: bool,
    dry_run: bool,
    verbose: bool,
    no_progress_bar: bool,
    recursive: bool,
    heading_style: str,
    highlight_style: str,
    strong_em_symbol: str,
    bullets: str,
    no_autolinks: bool,
    no_extract_metadata: bool,
    convert_as_inline: bool,
    strip_newlines: bool,
    no_escape_asterisks: bool,
    no_escape_underscores: bool,
    no_escape_misc: bool,
    stream_processing: bool,
    chunk_size: int,
    code_language: str,
    parser: str,
    wrap: bool,
    wrap_width: int,
):
    """Convert HTML files to Markdown.

    PATH can be a file or directory. If not provided, shows help and examples.
    """
    # Show banner and exit if no path provided
    if path is None:
        print_banner()
        return

    # Validate option combinations
    if flatten and not output:
        print_error("--flatten can only be used with --output")
        sys.exit(1)

    if rename and skip:
        print_error("--rename and --skip are mutually exclusive")
        sys.exit(1)

    if overwrite and output:
        print_error("--overwrite and --output are mutually exclusive")
        sys.exit(1)

    # Create converter with options
    converter = HTMLToMarkdownConverter(
        extract_metadata=not no_extract_metadata,
        convert_as_inline=convert_as_inline,
        heading_style=cast(Literal["underlined", "atx", "atx_closed"], heading_style),
        highlight_style=cast(Literal["double-equal", "html", "bold"], highlight_style),
        autolinks=not no_autolinks,
        bullets=bullets,
        strong_em_symbol=cast(Literal["*", "_"], strong_em_symbol),
        escape_asterisks=not no_escape_asterisks,
        escape_underscores=not no_escape_underscores,
        escape_misc=not no_escape_misc,
        wrap=wrap,
        wrap_width=wrap_width,
        code_language=code_language,
        strip_newlines=strip_newlines,
        parser=parser if parser != "auto" else None,
        stream_processing=stream_processing,
        chunk_size=chunk_size,
    )

    processor = FileProcessor(converter)

    # Find HTML files
    input_path = Path(path)
    output_path = Path(output) if output else None

    html_files = processor.find_html_files(input_path, recursive=recursive)
    if not html_files:
        print_error(f"No HTML files found in: {input_path}")
        sys.exit(1)

    # Display found files count
    print_info(f"Searching for HTML files in: {input_path}")
    print_info(f"Found {len(html_files)} HTML file(s)")

    # Determine base input directory
    if input_path.is_file():
        base_input_dir = input_path.parent
    else:
        base_input_dir = input_path

    # Generate file mapping
    file_mapping = {}
    for html_file in html_files:
        output_file = processor.generate_output_path(
            html_file,
            base_input_dir,
            output_path,
            flatten=flatten,
            rename_conflicts=False,  # We'll handle conflicts separately
        )
        file_mapping[html_file] = output_file

    # Handle conflicts if outputting to a directory
    if output_path and (flatten or len(html_files) > 1):
        clean_mapping, conflicts = processor.check_conflicts(file_mapping)

        if conflicts:
            if verbose:
                print_warning(
                    f"Found {len(conflicts)} file(s) with naming conflicts",
                    use_tqdm=False,
                )

            if rename:
                if verbose:
                    print_info("Resolving conflicts by renaming...", use_tqdm=False)
                resolved = ConflictResolver.resolve_with_rename(
                    conflicts, base_input_dir, output_path
                )
                file_mapping.update(resolved)
            elif skip:
                if verbose:
                    print_info("Skipping conflicted files...", use_tqdm=False)
                file_mapping = ConflictResolver.filter_conflicts(
                    conflicts, file_mapping
                )
                for conflict in conflicts:
                    print_warning(
                        f"Skipping conflicted file: {conflict}", use_tqdm=False
                    )
            else:
                print_error(
                    f"Found {len(conflicts)} naming conflicts. Use --rename or --skip to resolve.",
                    use_tqdm=False,
                )
                if verbose:
                    for conflict in conflicts:
                        print_error(f"  Conflict: {conflict}", use_tqdm=False)
                sys.exit(1)

    # Show what will be done in dry-run mode
    if dry_run:
        print_info("DRY RUN - No files will be converted:")
        for input_file, output_file in file_mapping.items():
            print(f"  {input_file} -> {output_file}")
        return

    # Convert files
    success_count = 0
    error_count = 0
    use_tqdm_output = len(file_mapping) > 1 and not no_progress_bar

    # Use progress bar for multiple files
    if len(file_mapping) > 1:
        file_iter = tqdm(
            file_mapping.items(),
            desc="Converting files",
            unit="file",
            disable=no_progress_bar,
        )
    else:
        file_iter = file_mapping.items()

    for input_file, output_file in file_iter:
        success, message = processor.process_single_file(
            input_file, output_file, overwrite=overwrite, dry_run=dry_run
        )

        if success:
            success_count += 1
            if verbose:
                print_success(message, use_tqdm=use_tqdm_output)
        else:
            error_count += 1
            print_error(message, use_tqdm=use_tqdm_output)

    # Remove original files if requested
    if overwrite and not dry_run and success_count > 0:
        successful_inputs = [
            input_file
            for input_file, output_file in file_mapping.items()
            if processor.process_single_file(
                input_file, output_file, overwrite=False, dry_run=True
            )[0]
        ]

        _remove_original_files(successful_inputs, dry_run)

    # Summary
    total_files = len(file_mapping)

    if dry_run:
        print_info(f"Would convert {total_files} file(s)")
    else:
        if error_count == 0:
            print_success(f"✓ Successfully converted {success_count} file(s)")
        else:
            print_warning(
                f"Converted {success_count}/{total_files} file(s), {error_count} error(s)"
            )

    sys.exit(0 if error_count == 0 else 1)


def _remove_original_files(file_paths, dry_run: bool):
    """Remove original HTML files after successful conversion.

    Args:
        file_paths: List of file paths to remove
        dry_run: Whether this is a dry run
    """
    if dry_run:
        return

    removed_count = 0
    for file_path in file_paths:
        try:
            file_path.unlink()
            removed_count += 1
        except Exception as e:
            print_error(f"Failed to remove {file_path}: {e}")

    if removed_count > 0:
        print_info(f"Removed {removed_count} original HTML file(s)")


if __name__ == "__main__":
    main()
