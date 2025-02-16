from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Citation:
    """表示一条引用的类"""
    paper_title: str
    authors: List[str]
    year: int
    venue: str
    citation_date: datetime
    
    def format_apa(self) -> str:
        """返回APA格式的引用"""
        authors_str = ", ".join(self.authors)
        return f"{authors_str} ({self.year}). {self.paper_title}. {self.venue}" 