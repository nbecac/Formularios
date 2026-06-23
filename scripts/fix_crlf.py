import os
import glob
import json

def fix_line_endings(directory, extensions):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, f)
                with open(filepath, 'rb') as file:
                    content = file.read()
                
                # Decode, replace all \r\n and \r with \n
                try:
                    text = content.decode('utf-8')
                    # normalize
                    text = text.replace('\r\n', '\n').replace('\r', '\n')
                    
                    with open(filepath, 'wb') as file:
                        file.write(text.encode('utf-8'))
                    print(f"Fixed line endings: {filepath}")
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")

if __name__ == '__main__':
    fix_line_endings('backend', ['.py', '.txt'])
    fix_line_endings('extension', ['.js', '.json', '.html', '.css'])
    fix_line_endings('docs', ['.md', '.html'])
    fix_line_endings('scripts', ['.bat'])
    print("Done formatting.")
