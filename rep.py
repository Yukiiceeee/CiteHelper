from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import urllib.parse
import math
import re
import os

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    )
    # 替换为你的 ChromeDriver 路径
    driver_path = r"D:\ChromeDriver\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def construct_search_url(query):
    base_url = "https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q="
    encoded_query = urllib.parse.quote(query)
    return f"{base_url}{encoded_query}&btnG="

def get_first_paper_info(driver):
    time.sleep(random.uniform(1, 2))
    if check_captcha(driver):
        wait_for_captcha(driver)
    first_paper = driver.find_element(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl')
    paper_title = first_paper.find_element(By.CSS_SELECTOR, 'h3.gs_rt').text
    try:
        citation_element = first_paper.find_element(By.XPATH, './/a[contains(text(), "被引用次数")]')
        citation_text = citation_element.text
        citation_count = int(citation_text.split('：')[1])
        citations_link = citation_element.get_attribute('href')
    except:
        citation_count = 0
        citations_link = None
    return paper_title, citation_count, citations_link

def get_citing_papers_titles(driver, num_papers):
    if num_papers == 0:
        return []
    time.sleep(random.uniform(1, 2))
    if check_captcha_in_citation_page(driver):
        wait_for_captcha(driver)
    titles = []
    total_citations = num_papers
    max_pages = 100
    for page in range(max_pages):
        if len(titles) >= num_papers:
            break
        start = page * 10
        current_url = driver.current_url
        if '&start=' in current_url:
            current_url = re.sub(r'&start=\d+', f'&start={start}', current_url)
        else:
            current_url += f'&start={start}'
        driver.get(current_url)
        time.sleep(random.uniform(1, 2))
        if check_captcha_in_citation_page(driver):
            wait_for_captcha(driver)
        papers = driver.find_elements(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl')
        if not papers:
            print("已到达最后一页，未找到更多引用文献。")
            break
        for paper in papers:
            if len(titles) >= num_papers:
                break
            title = paper.find_element(By.CSS_SELECTOR, 'h3.gs_rt').text
            titles.append(title)
    titles.reverse()
    return titles

def check_captcha(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, 'div.gs_r.gs_or.gs_scl h3.gs_rt')
        return False
    except:
        return True

def check_captcha_in_citation_page(driver):
    try:
        driver.find_element(By.XPATH, '//*[@id="gs_res_ccl_top"]')
        return False
    except:
        return True

def wait_for_captcha(driver):
    print("检测到验证码，请手动完成验证。")
    while True:
        input("完成验证码后按回车继续...")
        time.sleep(2)
        if not check_captcha(driver) or not check_captcha_in_citation_page(driver):
            break

def read_citation_results(file_path):
    citation_data = {}
    if not os.path.exists(file_path):
        return citation_data
    current_paper = None
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if line.startswith('论文标题：'):
            current_paper = line[len('论文标题：'):].strip()
            idx += 1
            line = lines[idx].strip()
            if line.startswith('该论文被引用次数：'):
                citation_count = int(line[len('该论文被引用次数：'):].strip())
                idx += 1
                line = lines[idx].strip()
                if line == '该论文被检索到的引用文献：':
                    idx += 1
                    citations = []
                    while idx < len(lines):
                        line = lines[idx].strip()
                        if not line:
                            break
                        else:
                            match = re.match(r'^(\d+)\.\s+(.*)$', line)
                            if match:
                                number = int(match.group(1))
                                citation_text = match.group(2)
                                citations.append((number, citation_text))
                            else:
                                citations.append((None, line))
                        idx += 1
                    citation_data[current_paper] = {
                        'citation_count': citation_count,
                        'citations': citations
                    }
                else:
                    idx += 1
            else:
                idx += 1
        else:
            idx += 1
    return citation_data

def write_citation_results(file_path, citation_data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for paper_title, data in citation_data.items():
            f.write(f"论文标题：{paper_title}\n")
            f.write(f"该论文被引用次数：{data['citation_count']}\n")
            f.write("该论文被检索到的引用文献：\n")
            for number, citation in data['citations']:
                f.write(f"{number}. {citation}\n")
            f.write("\n")

def main():
    paper_names = [
        "MOELoRA: An MOE-based Parameter Efficient Fine-Tuning Method for Multi-task Medical Applications",
        "MoELoRA: Contrastive Learning Guided Mixture of Experts on Parameter-Efficient Fine-Tuning for Large Language Models",
        "LoRAMoE: Alleviating World Knowledge Forgetting in Large Language Models via MoE-Style Plugin",
        "Higher Layers Need More LoRA Experts",
        "MoRA: High-Rank Updating for Parameter-Efficient Fine-Tuning",
        "MIXLORA: ENHANCING LARGE LANGUAGE MODELS FINE-TUNING WITH LORA BASED MIXTURE OF EXPERTS",
        "Mixture-of-Subspaces in Low-Rank Adaptation",
        "MoRAL: MoE Augmented LoRA for LLMs’ Lifelong Learning",
        "Mixture of Cluster-Conditional LoRA Experts for Vision-Language Instruction Tuning",
        "Mixture-of-LoRAs: An Efficient Multitask Tuning for Large Language Models",
        "CTRLorALTer: Conditional LoRAdapter for Efficient 0-Shot Control & Altering of T2I Models",
        "Implicit Style-Content Separation using B-LoRA",
        "ZipLoRA: Any Subject in Any Style by Effectively Merging LoRAs",
        "UnZipLoRA: Separating Content and Style from a Single Image"
    ]
    driver = setup_driver()
    citation_data = read_citation_results('citation_results.txt')
    try:
        for paper_name in paper_names:
            search_url = construct_search_url(paper_name)
            driver.get(search_url)
            paper_title, current_citation_count, citations_link = get_first_paper_info(driver)
            if current_citation_count == 0 or not citations_link:
                print(f"论文标题：{paper_title}")
                print("该论文没有被引用")
                if paper_title not in citation_data:
                    citation_data[paper_title] = {
                        'citation_count': 0,
                        'citations': []
                    }
                else:
                    citation_data[paper_title]['citation_count'] = 0
                continue
            citations_link_by_date = citations_link + "&scipsc=&q=&scisbd=1"
            if paper_title in citation_data:
                stored_citation_count = citation_data[paper_title]['citation_count']
                if current_citation_count == stored_citation_count:
                    print(f"论文标题：{paper_title}")
                    print("该论文被引用次数无变化")
                    continue
                elif current_citation_count > stored_citation_count:
                    x = current_citation_count - stored_citation_count
                    print(f"论文标题：{paper_title}")
                    print(f"该论文被引用次数增加{x}次")
                    driver.get(citations_link_by_date)
                    new_citations = get_citing_papers_titles(driver, x)
                    last_number = citation_data[paper_title]['citations'][-1][0] if citation_data[paper_title]['citations'] else 0
                    new_citation_entries = []
                    for idx, citation in enumerate(new_citations, start=last_number + 1):
                        new_citation_entries.append((idx, citation))
                    citation_data[paper_title]['citations'].extend(new_citation_entries)
                    citation_data[paper_title]['citation_count'] = current_citation_count
                    print("❤新增的被引用文献有：")
                    for idx, citation in enumerate(new_citations, start=1):
                        print(f"{idx}. {citation}")
                else:
                    print(f"论文标题：{paper_title}")
                    print("当前被引用次数小于已存储的次数，可能有误")
            else:
                print(f"论文标题：{paper_title}")
                print("新添加论文")
                driver.get(citations_link_by_date)
                all_citations = get_citing_papers_titles(driver, current_citation_count)
                citation_entries = []
                for idx, citation in enumerate(all_citations, start=1):
                    citation_entries.append((idx, citation))
                citation_data[paper_title] = {
                    'citation_count': current_citation_count,
                    'citations': citation_entries
                }
    except Exception as e:
        print(f"发生错误：{e}")
    finally:
        write_citation_results('citation_results.txt', citation_data)
        print("完成爬取，数据已写入")
        driver.quit()

if __name__ == "__main__":
    main()