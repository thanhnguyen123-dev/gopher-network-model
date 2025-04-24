from typing import Optional

class FileStats:
    def __init__(self, path: str, size: float, content: Optional[bytes] = None):
        self.path = path
        self.size = size
        self.content = content

    """
        Get the path of the file

        :return: the path of the file
    """
    def get_path(self) -> str:
        return self.path
    

    """
        Get the size of the file

        :return: the size of the file
    """
    def get_size(self) -> float:
        return self.size
    

    """
        Get the content of the file

        :return: the content of the file
    """
    def get_content(self) -> Optional[bytes]:
        return self.content
    
        
        