from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from typing import List, Optional, Tuple
import time
import random
import urllib.parse
from datetime import datetime
from .paper import Paper
from .citation import Citation
import math

class ScholarCrawler:
    """谷歌学术爬虫类"""
    
    def __init__(self, driver_path: str):
        self.driver_path = driver_path
        self.driver = None
        
    def setup_driver(self):
        """初始化Chrome驱动"""
        chrome_options = Options()
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        )
        service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def construct_search_url(self, query: str) -> str:
        """构造搜索URL"""
        base_url = "https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q="
        encoded_query = urllib.parse.quote(query)
        return f"{base_url}{encoded_query}&btnG="

    def check_captcha(self, is_citation_page: bool = False) -> bool:
        """检查是否出现验证码"""
        try:
            if not is_citation_page:
                self.driver.find_element(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl h3.gs_rt')
            else:
                self.driver.find_element(By.XPATH, '//*[@id="gs_res_ccl_top"]')
            return False
        except:
            return True

    def wait_for_captcha(self):
        """等待用户完成验证码"""
        print("检测到验证码，请手动完成验证。")
        while True:
            input("完成验证码后按回车继续...")
            time.sleep(2)
            if not self.check_captcha() and not self.check_captcha(True):
                break

    def get_paper_info(self, query: str) -> Tuple[Paper, Optional[str]]:
        """获取论文基本信息和引用链接"""
        if not self.driver:
            self.setup_driver()
            
        search_url = self.construct_search_url(query)
        self.driver.get(search_url)
        time.sleep(random.uniform(1, 2))
        
        if self.check_captcha():
            self.wait_for_captcha()
            
        try:
            first_paper = self.driver.find_element(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl')
            title = first_paper.find_element(By.CSS_SELECTOR, 'h3.gs_rt').text
            
            # 获取引用信息
            citation_count = 0
            citations_link = None
            try:
                citation_element = first_paper.find_element(
                    By.XPATH, './/a[contains(text(), "被引用次数")]'
                )
                citation_text = citation_element.text
                citation_count = int(citation_text.split('：')[1])
                citations_link = citation_element.get_attribute('href')
            except:
                pass
                
            # 创建Paper对象
            paper = Paper(
                title=title,
                citation_count=citation_count,
                last_updated=datetime.now()
            )
            
            return paper, citations_link
            
        except Exception as e:
            raise Exception(f"获取论文信息失败: {str(e)}")

    def get_citations(self, paper: Paper, citations_link: str) -> List[Citation]:
        """获取引用该论文的所有文献"""
        if paper.citation_count == 0 or not citations_link:
            return []
            
        citations = []
        citations_link_by_date = citations_link + "&scipsc=&q=&scisbd=1"
        max_pages = math.ceil(paper.citation_count / 10)
        
        for page in range(max_pages):
            start = page * 10
            if '&start=' in citations_link_by_date:
                current_url = citations_link_by_date.replace(
                    f'&start={start-10}', f'&start={start}'
                ) if start > 0 else citations_link_by_date
            else:
                current_url = citations_link_by_date + f'&start={start}'
                
            self.driver.get(current_url)
            time.sleep(random.uniform(1, 2))
            
            if self.check_captcha(True):
                self.wait_for_captcha()
                
            papers = self.driver.find_elements(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl')
            if not papers:
                print("已到达最后一页，未找到更多引用文献。")
                break
                
            for paper_element in papers:
                try:
                    title = paper_element.find_element(By.CSS_SELECTOR, 'h3.gs_rt').text
                    # 由于Google Scholar可能不总是提供完整信息，我们设置一些默认值
                    citation = Citation(
                        paper_title=title,
                        authors=[],  # 需要额外解析作者信息
                        year=datetime.now().year,  # 默认当前年份
                        venue="",  # 需要额外解析会议/期刊信息
                        citation_date=datetime.now()
                    )
                    citations.append(citation)
                except Exception as e:
                    continue
                    
        return citations

    def __del__(self):
        """确保关闭浏览器"""
        if self.driver:
            self.driver.quit() 