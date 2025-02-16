import json
from datetime import datetime
from typing import Dict, List
from .paper import Paper
from .citation import Citation

class CitationStorage:
    """处理引用数据的存储和检索"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Dict[str, Dict] = {}
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
    
    def save_data(self):
        """保存数据到文件"""
        formatted_data = {}
        for paper_title, data in self.data.items():
            formatted_data[paper_title] = {
                'citation_count': data['citation_count'],
                'last_updated': data.get('last_updated', datetime.now().isoformat()),
                'citations': [
                    {
                        'title': citation.paper_title,
                        'authors': citation.authors,
                        'year': citation.year,
                        'venue': citation.venue,
                        'citation_date': citation.citation_date.isoformat()
                    }
                    for citation in data['citations']
                ]
            }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
    
    def get_new_citations(self, paper: Paper, current_citations: List[Citation]) -> List[Citation]:
        """比较并返回新增的引用"""
        if paper.title not in self.data:
            return current_citations
            
        stored_citations = {c['title'] for c in self.data[paper.title]['citations']}
        return [c for c in current_citations if c.paper_title not in stored_citations] 