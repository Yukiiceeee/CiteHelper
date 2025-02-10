import sys 
import json 
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidgetItem,
    QMessageBox, QInputDialog 
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt 
from ui_mainwindow import Ui_MainWindow 
import rep  # 导入您的爬虫模块 
 
# 加载美化包 
import qt_material 
 
class CrawlerThread(QThread):
    update_signal = pyqtSignal(str, dict)  # (论文标题, 数据)
 
    def __init__(self, paper_list):
        super().__init__()
        self.paper_list  = paper_list 
 
    def run(self):
        for paper in self.paper_list: 
            try:
                # 调用爬虫核心逻辑 
                result = crawler.process_single_paper(paper) 
                self.update_signal.emit(paper,  result)
            except Exception as e:
                self.update_signal.emit(paper,  {"error": str(e)})
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化UI 
        self.ui  = Ui_MainWindow()
        self.ui.setupUi(self) 
        
        # 绑定信号 
        self.ui.startButton.clicked.connect(self.start_crawling) 
        self.ui.actionAdd.triggered.connect(self.add_paper) 
        self.ui.actionRemove.triggered.connect(self.remove_paper) 
        
        # 加载默认论文列表 
        self.load_default_papers() 
 
    def load_default_papers(self):
        try:
            with open('resources/papers.txt',  'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip(): 
                        self.ui.paperList.addItem(line.strip()) 
        except FileNotFoundError:
            pass 
 
    def add_paper(self):
        text, ok = QInputDialog.getText( 
            self, '添加论文', '输入论文标题:'
        )
        if ok and text:
            self.ui.paperList.addItem(text) 
 
    def remove_paper(self):
        current_item = self.ui.paperList.currentItem() 
        if current_item:
            self.ui.paperList.takeItem( 
                self.ui.paperList.row(current_item) 
            )
 
    def start_crawling(self):
        # 获取论文列表 
        papers = [
            self.ui.paperList.item(i).text() 
            for i in range(self.ui.paperList.count()) 
        ]
 
        if not papers:
            QMessageBox.warning(self,  '警告', '请先添加要爬取的论文')
            return 
 
        # 创建爬虫线程 
        self.thread  = CrawlerThread(papers)
        self.thread.update_signal.connect(self.update_results) 
        self.thread.start() 
 
        # 禁用按钮防止重复点击 
        self.ui.startButton.setEnabled(False) 
        self.thread.finished.connect( 
            lambda: self.ui.startButton.setEnabled(True) 
        )
 
    def update_results(self, paper, data):
        if 'error' in data:
            content = f"【错误】{paper}\n{data['error']}\n{'='*30}\n"
        else:
            content = ( 
                f"论文标题：{paper}\n"
                f"被引次数：{data['citation_count']}\n"
                "最新引用：\n" + 
                "\n".join([f"{i+1}. {cite}" for i, cite in enumerate(data['new_citations'])]) +
                "\n" + "="*30 + "\n"
            )
        
        # 在现有内容前插入新结果 
        current = self.ui.resultView.toPlainText() 
        self.ui.resultView.setPlainText(content  + current)
 
if __name__ == "__main__":
    app = QApplication(sys.argv) 
    
    # 应用Material主题 
    qt_material.apply_stylesheet(app,  theme='dark_teal.xml') 
    
    window = MainWindow()
    window.show() 
    sys.exit(app.exec()) 