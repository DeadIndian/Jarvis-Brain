from typing import List, Dict, Any
import os


class MarkdownLoader:
    def __init__(self):
        pass
    
    def load_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_directory(self, directory_path: str) -> List[str]:
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        markdown_files = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                content = self.load_file(file_path)
                markdown_files.append(content)
        
        return markdown_files
