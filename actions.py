import os
from pathlib import Path

def create_local_file(filename: str, content: str) -> str:
    # Handles both files and sub-folders inside 'output'
    try:
        base_output = Path("output")
        
        # Combine output dir with the user's requested path
        full_path = base_output / filename
        
        # Create any necessary sub-folders automatically (This is the magic line!)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ Success: Saved to `{full_path}`"
        
    except Exception as e:
        return f" Error: {str(e)}"

def summarize_content(text: str) -> str:
    # fallback for when we just need a quick text snippet
    if not text:
        return "No text provided to summarize."
    return f"Summary snippet: {text[:150]}..."