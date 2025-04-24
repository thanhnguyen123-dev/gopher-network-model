from typing import Optional

class FileStats:
    def __init__(self, path: str, size: float, content: Optional[bytes] = None):
        self.path = path
        self.size = size
        self.content = content

    def get_path(self) -> str:
        return self.path
    
    def get_size(self) -> float:
        return self.size
    
    def get_content(self) -> Optional[bytes]:
        return self.content
    
        
        