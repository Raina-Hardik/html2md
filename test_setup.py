#!/usr/bin/env python3
"""Test script for html2md tool."""

import tempfile
import shutil
from pathlib import Path

# Sample HTML content for testing
SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Test Document</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .highlight { background-color: yellow; }
    </style>
</head>
<body>
    <h1>Main Title</h1>
    <p>This is a <strong>sample</strong> HTML document with <em>various</em> elements.</p>
    
    <h2>Features List</h2>
    <ul>
        <li>HTML to Markdown conversion</li>
        <li>Recursive directory processing</li>
        <li>Conflict resolution</li>
    </ul>
    
    <h3>Code Example</h3>
    <pre><code>
def hello_world():
    print("Hello, World!")
    </code></pre>
    
    <blockquote>
        <p>This is a quote block with some <a href="https://example.com">links</a>.</p>
    </blockquote>
    
    <table>
        <tr>
            <th>Feature</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>CLI Interface</td>
            <td>✓ Complete</td>
        </tr>
        <tr>
            <td>Batch Processing</td>
            <td>✓ Complete</td>
        </tr>
    </table>
    
    <p>Visit our <a href="https://github.com/example/html2md">GitHub repository</a> for more information.</p>
    
    <script>
        // This script should be removed
        console.log("This should not appear in markdown");
    </script>
</body>
</html>"""

COMPLEX_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Complex Document</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Complex HTML Structure</h1>
            <nav>
                <ul>
                    <li><a href="#section1">Section 1</a></li>
                    <li><a href="#section2">Section 2</a></li>
                </ul>
            </nav>
        </header>
        
        <main>
            <section id="section1">
                <h2>Section 1: Nested Content</h2>
                <div class="content">
                    <p>This section contains <span class="highlight">highlighted text</span> and multiple paragraphs.</p>
                    <p>Here's another paragraph with <code>inline code</code> and more content.</p>
                </div>
            </section>
            
            <section id="section2">
                <h2>Section 2: Lists and Tables</h2>
                <ol>
                    <li>First ordered item</li>
                    <li>Second ordered item with <strong>bold text</strong></li>
                    <li>Third item</li>
                </ol>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2025 Test Company. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>"""


def create_test_structure():
    """Create a test directory structure with HTML files."""
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp(prefix="html2md_test_"))
    
    # Create directory structure
    (test_dir / "docs").mkdir()
    (test_dir / "docs" / "guides").mkdir()
    (test_dir / "examples").mkdir()
    
    # Create HTML files
    files_created = []
    
    # Root level files
    (test_dir / "index.html").write_text(SAMPLE_HTML)
    files_created.append("index.html")
    
    (test_dir / "about.html").write_text(COMPLEX_HTML)
    files_created.append("about.html")
    
    # Docs directory
    (test_dir / "docs" / "overview.html").write_text(SAMPLE_HTML.replace("Test Document", "Overview"))
    files_created.append("docs/overview.html")
    
    (test_dir / "docs" / "guides" / "getting-started.html").write_text(
        COMPLEX_HTML.replace("Complex Document", "Getting Started Guide")
    )
    files_created.append("docs/guides/getting-started.html")
    
    # Examples directory
    (test_dir / "examples" / "basic.html").write_text(SAMPLE_HTML.replace("Test Document", "Basic Example"))
    files_created.append("examples/basic.html")
    
    (test_dir / "examples" / "advanced.html").write_text(COMPLEX_HTML.replace("Complex Document", "Advanced Example"))
    files_created.append("examples/advanced.html")
    
    print(f"Created test directory: {test_dir}")
    print(f"Files created: {len(files_created)}")
    for file in files_created:
        print(f"  - {file}")
    
    return test_dir


def cleanup_test_structure(test_dir):
    """Clean up test directory."""
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Cleaned up test directory: {test_dir}")


if __name__ == "__main__":
    test_dir = create_test_structure()
    print()
    print("Test structure created! You can now test the html2md tool:")
    print()
    print(f"cd {test_dir}")
    print("html2md .")
    print("html2md . --output converted --flatten --rename")
    print("html2md . --dry-run --verbose")
    print()
    print("When done testing, run this script with 'cleanup' to remove test files:")
    print(f"python test_setup.py cleanup {test_dir}")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        if len(sys.argv) > 2:
            cleanup_dir = Path(sys.argv[2])
            cleanup_test_structure(cleanup_dir)
        else:
            print("Please provide the test directory path to cleanup")
