import click
from scholarly import ScholarCrawler, CitationStorage
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """学术论文引用追踪工具"""
    pass

@cli.command()
@click.argument('paper_list', type=click.Path(exists=True))
@click.option('--driver-path', required=True, help='ChromeDriver路径')
@click.option('--output', default='citations.json', help='输出文件路径')
def track(paper_list: str, driver_path: str, output: str):
    """追踪论文的新增引用"""
    try:
        crawler = ScholarCrawler(driver_path)
        storage = CitationStorage(output)
        
        with open(paper_list, 'r', encoding='utf-8') as f:
            papers = [line.strip() for line in f if line.strip()]
            
        for paper_title in papers:
            logger.info(f"正在处理论文: {paper_title}")
            paper, citations_link = crawler.get_paper_info(paper_title)
            
            if paper.citation_count == 0:
                logger.info("该论文没有被引用")
                continue
                
            if paper.title in storage.data:
                stored_citation_count = storage.data[paper.title]['citation_count']
                if paper.citation_count == stored_citation_count:
                    logger.info("该论文被引用次数无变化")
                    continue
                elif paper.citation_count > stored_citation_count:
                    new_count = paper.citation_count - stored_citation_count
                    logger.info(f"该论文被引用次数增加{new_count}次")
                    
                    citations = crawler.get_citations(paper, citations_link)
                    new_citations = storage.get_new_citations(paper, citations)
                    
                    if new_citations:
                        logger.info("❤新增的被引用文献有：")
                        for idx, citation in enumerate(new_citations, start=1):
                            logger.info(f"{idx}. {citation.paper_title}")
                else:
                    logger.warning("当前被引用次数小于已存储的次数，可能有误")
            else:
                logger.info("新添加论文")
                citations = crawler.get_citations(paper, citations_link)
                storage.data[paper.title] = {
                    'citation_count': paper.citation_count,
                    'citations': citations
                }
                
        storage.save_data()
        logger.info("完成爬取，数据已写入")
        
    except Exception as e:
        logger.error(f"发生错误：{e}")
    finally:
        if crawler.driver:
            crawler.driver.quit()

if __name__ == '__main__':
    cli() 