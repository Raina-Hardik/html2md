# HTML to Markdown Converter

A fast and flexible CLI tool for converting HTML files to Markdown format, inspired by Black's simplicity and power.

## Features

- Convert single HTML files or entire directories recursively
- Preserve directory structure or flatten to a single output directory
- Handle filename conflicts with rename or skip strategies
- Overwrite original files option
- Beautiful progress bars and colored output
- Comprehensive error handling and logging

## Installation

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
# Display tool information
html2md

# Convert all HTML files in current directory recursively
html2md .

# Convert specific directory
html2md path/to/directory

# Convert specific file
html2md path/to/file.html
```

### Advanced Options

```bash
# Overwrite original HTML files after conversion
html2md . --overwrite

# Flatten directory structure to single output directory
html2md . --output output_dir

# Handle filename conflicts by renaming (folder_subfolder_filename.md)
html2md . --output output_dir --rename

# Handle filename conflicts by skipping
html2md . --output output_dir --skip

# Verbose output
html2md . --verbose

# Dry run (show what would be converted without actually converting)
html2md . --dry-run
```

## Examples

```bash
# Convert all HTML files in data/ directory, preserving structure
html2md data/

# Convert and flatten to markdown/ directory with conflict resolution
html2md data/ --output markdown/ --rename

# Convert current directory, overwrite originals, with verbose output
html2md . --overwrite --verbose

# Dry run to see what would be converted
html2md complex_project/ --dry-run
```

## License

MIT License
