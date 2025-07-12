"""Core conversion functionality for HTML to Markdown."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Literal, Callable, Any

from html_to_markdown import convert_to_markdown


class HTMLToMarkdownConverter:
    """Main converter class for HTML to Markdown conversion using html-to-markdown."""
    
    def __init__(
        self,
        extract_metadata: bool = True,
        convert_as_inline: bool = False,
        heading_style: Literal["underlined", "atx", "atx_closed"] = "atx",
        highlight_style: Literal["double-equal", "html", "bold"] = "double-equal",
        autolinks: bool = True,
        bullets: str = "*+-",
        strong_em_symbol: Literal["*", "_"] = "*",
        escape_asterisks: bool = True,
        escape_underscores: bool = True,
        escape_misc: bool = True,
        wrap: bool = False,
        wrap_width: int = 80,
        code_language: str = "",
        strip_newlines: bool = False,
        parser: Optional[str] = None,
        stream_processing: bool = False,
        chunk_size: int = 1024
    ):
        """Initialize the converter with configuration options.
        
        Args:
            extract_metadata: Extract document metadata as comment header
            convert_as_inline: Treat content as inline elements only
            heading_style: Header style ('underlined', 'atx', 'atx_closed')
            highlight_style: Style for highlighted text
            autolinks: Auto-convert URLs to Markdown links
            bullets: Characters to use for bullet points
            strong_em_symbol: Symbol for strong/emphasized text
            escape_asterisks: Escape * characters
            escape_underscores: Escape _ characters  
            escape_misc: Escape miscellaneous characters
            wrap: Enable text wrapping
            wrap_width: Text wrap width
            code_language: Default language for code blocks
            strip_newlines: Remove newlines from input
            parser: HTML parser to use ('lxml' or 'html.parser')
            stream_processing: Enable streaming for large documents
            chunk_size: Chunk size for streaming
        """
        self.config = {
            'extract_metadata': extract_metadata,
            'convert_as_inline': convert_as_inline,
            'heading_style': heading_style,
            'highlight_style': highlight_style,
            'autolinks': autolinks,
            'bullets': bullets,
            'strong_em_symbol': strong_em_symbol,
            'escape_asterisks': escape_asterisks,
            'escape_underscores': escape_underscores,
            'escape_misc': escape_misc,
            'wrap': wrap,
            'wrap_width': wrap_width,
            'code_language': code_language,
            'strip_newlines': strip_newlines,
            'parser': parser,
            'stream_processing': stream_processing,
            'chunk_size': chunk_size
        }
    def convert_html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown using html-to-markdown.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Converted Markdown content
        """
        try:
            # Use the html-to-markdown library with our configuration
            markdown = convert_to_markdown(html_content, **self.config)
            
            # Additional post-processing if needed
            markdown = self.postprocess_markdown(markdown)
            
            return markdown
            
        except Exception as e:
            raise ConversionError(f"Failed to convert HTML to Markdown: {str(e)}")
    
    def postprocess_markdown(self, markdown_content: str) -> str:
        """Clean up markdown content after conversion.
        
        Args:
            markdown_content: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        # The html-to-markdown library already does most cleanup,
        # but we can add any additional custom processing here
        
        # Ensure file ends with single newline
        if markdown_content and not markdown_content.endswith('\n'):
            markdown_content += '\n'
        
        return markdown_content
    
    def convert_file(
        self, 
        input_file: Union[str, Path], 
        output_file: Optional[Union[str, Path]] = None,
        encoding: str = 'utf-8'
    ) -> str:
        """Convert an HTML file to Markdown.
        
        Args:
            input_file: Path to HTML file
            output_file: Path for output file (optional)
            encoding: File encoding
            
        Returns:
            Path to output file
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not input_path.is_file():
            raise ValueError(f"Input path is not a file: {input_path}")
        
        # Determine output file path
        if output_file is None:
            output_path = input_path.with_suffix('.md')
        else:
            output_path = Path(output_file)
        
        # Read HTML content
        try:
            with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                html_content = f.read()
        except Exception as e:
            raise FileReadError(f"Failed to read file {input_path}: {str(e)}")
        
        # Convert to markdown
        markdown_content = self.convert_html_to_markdown(html_content)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write markdown content
        try:
            with open(output_path, 'w', encoding=encoding, errors='replace') as f:
                f.write(markdown_content)
        except Exception as e:
            raise FileWriteError(f"Failed to write file {output_path}: {str(e)}")
        
        return str(output_path)


class ConversionError(Exception):
    """Exception raised when HTML to Markdown conversion fails."""
    pass


class FileReadError(Exception):
    """Exception raised when reading input file fails."""
    pass


class FileWriteError(Exception):
    """Exception raised when writing output file fails."""
    pass
