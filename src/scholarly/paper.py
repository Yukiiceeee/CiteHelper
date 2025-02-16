from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Paper:
    """表示一篇学术论文的类"""
    title: str
    authors: List[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    citation_count: int = 0
    last_updated: datetime = None
    
    def __str__(self) -> str:
        return f"{self.title} ({self.year}) - 被引用 {self.citation_count} 次" 