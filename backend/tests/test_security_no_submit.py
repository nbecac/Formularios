import re
from pathlib import Path

def test_no_submit_in_extension():
    root_dir = Path(__file__).parent.parent.parent
    extension_dir = root_dir / "extension"
    
    files_to_check = ["contentScript.js", "popup.js"]
    
    forbidden_patterns = [
        r'\.submit\(\)',
        r'form\.submit',
        r'querySelector\([\'"]button\[type=[\'"]?submit[\'"]?\][\'"]\)',
        r'\.click\(\)' # generally shouldn't auto-click for forms in our MVP
    ]
    
    # We do allow looking for submit buttons manually if we want to block them, 
    # but the extension shouldn't click them or submit the form.
    # We will enforce the specific patterns explicitly.
    
    for filename in files_to_check:
        filepath = extension_dir / filename
        assert filepath.exists(), f"{filename} not found"
        content = filepath.read_text(encoding="utf-8")
        
        for pattern in forbidden_patterns:
            assert not re.search(pattern, content), f"Forbidden pattern '{pattern}' found in {filename}"
            
        # Check for automated strings attempting to submit
        lower_content = content.lower()
        # We ensure there's no attempt to find buttons by "enviar" text and click them
        if "enviar" in lower_content or "submit" in lower_content:
            # We just do a basic heuristic: make sure it doesn't do something like .click() after finding it.
            # In our current script we don't even look for these texts, so if they exist in logic context, it might fail.
            pass
