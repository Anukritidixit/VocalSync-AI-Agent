import os
from pathlib import Path

def create_local_file(filename: str, content: str) -> str:
    """
    Securely creates a file within the designated output directory.
    Prevents directory traversal attacks.
    """
    try:
        # 1. Ensure output directory exists safely
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 2. Security constraint: Extract just the filename to prevent malicious paths 
        # (e.g., if the AI tries to write to "../../system_file.txt")
        safe_filename = Path(filename).name
        file_path = output_dir / safe_filename
        
        # 3. Write the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ Success: File saved securely at `{file_path}`"
        
    except Exception as e:
        return f"❌ Error creating file: {str(e)}"

def summarize_content(text: str) -> str:
    """Provides a simple fallback summary snippet."""
    if not text:
        return "No text provided to summarize."
    return f"Summary snippet: {text[:150]}..."