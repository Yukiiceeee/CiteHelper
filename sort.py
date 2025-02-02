import re
from collections import defaultdict

def read_citation_results(file_path):
    citation_data = {}
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
                            match = re.match(r'^\d+\.\s+(.*)$', line)
                            if match:
                                citation_text = match.group(1)
                                citations.append(citation_text)
                            else:
                                citations.append(line)
                        idx += 1
                    citation_data[current_paper] = citations
                else:
                    idx += 1
            else:
                idx += 1
        else:
            idx += 1
    return citation_data

def build_citation_to_input_papers(citation_data):
    citation_to_input_papers = defaultdict(set)
    for input_paper, citations in citation_data.items():
        for citation in citations:
            citation_to_input_papers[citation].add(input_paper)
    return citation_to_input_papers

def main():
    file_path = 'citation_results.txt'
    citation_data = read_citation_results(file_path)
    citation_to_input_papers = build_citation_to_input_papers(citation_data)

    citation_list = []
    for citation, input_papers in citation_to_input_papers.items():
        count = len(input_papers)
        citation_list.append((citation, count, input_papers))

    citation_list.sort(key=lambda x: x[1], reverse=True)

    print("被引用文献出现次数统计：")
    for idx, (citation, count, input_papers) in enumerate(citation_list, start=1):
        input_papers_str = '、'.join(input_papers)
        print(f"{idx}. {citation}")
        print(f"- 该文献引用的输入文章数：{count}")
        print(f"- 该文献引用的输入文章为：{input_papers_str}")
        print()

if __name__ == "__main__":
    main()