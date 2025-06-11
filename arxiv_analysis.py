import requests
import feedparser
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime

# 设置arXiv API参数
ARXIV_URL = "http://export.arxiv.org/api/query?"
CATEGORY = "math"  # 数学领域
MAX_RESULTS = 500  # 获取的论文数量
DAYS_BACK = 30     # 获取最近多少天的论文

# 定义数学子领域关键词(可根据需要扩展)
KEYWORDS = {
    'Algebra': ['algebra', 'group', 'ring', 'field', 'module', 'homomorphism'],
    'Analysis': ['analysis', 'function', 'derivative', 'integral', 'measure', 'harmonic'],
    'Geometry': ['geometry', 'topology', 'manifold', 'curve', 'surface', 'metric'],
    'Number Theory': ['number theory', 'prime', 'modular', 'diophantine', 'zeta'],
    'Applied Math': ['applied', 'model', 'simulation', 'numerical', 'optimization'],
    'Probability': ['probability', 'stochastic', 'random', 'markov', 'brownian'],
    'Statistics': ['statistics', 'regression', 'hypothesis', 'bayesian', 'estimation'],
    'Dynamical Systems': ['dynamical', 'chaos', 'bifurcation', 'attractor', 'flow'],
    'Logic': ['logic', 'set theory', 'model theory', 'proof', 'computability'],
    'Combinatorics': ['combinatorics', 'graph', 'permutation', 'partition', 'matroid']
}

def get_arxiv_papers():
    """从arXiv API获取数学论文数据"""
    query = f"search_query=cat:{CATEGORY}&start=0&max_results={MAX_RESULTS}&sortBy=submittedDate&sortOrder=descending"
    url = ARXIV_URL + query
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    
    papers = []
    for entry in feed.entries:
        # 提取论文信息
        paper = {
            'title': entry.title,
            'abstract': entry.summary,
            'published': entry.published,
            'authors': [author.name for author in entry.authors],
            'arxiv_id': entry.id.split('/abs/')[-1],
            'pdf_link': entry.link
        }
        papers.append(paper)
    
    return papers

def classify_paper(text, keywords_dict):
    """根据标题和摘要中的关键词分类论文"""
    text = text.lower()
    categories = set()
    
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            # 使用正则表达式确保匹配完整单词
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
                categories.add(category)
                break  # 一个类别匹配一个关键词即可
    
    return list(categories) if categories else ['Other']

def analyze_papers(papers):
    """分析论文并统计分类结果"""
    category_counts = defaultdict(int)
    classified_papers = []
    
    for paper in papers:
        combined_text = paper['title'] + " " + paper['abstract']
        categories = classify_paper(combined_text, KEYWORDS)
        
        # 更新统计
        for category in categories:
            category_counts[category] += 1
        
        # 保存分类结果
        classified_paper = paper.copy()
        classified_paper['categories'] = categories
        classified_papers.append(classified_paper)
    
    return dict(category_counts), classified_papers

def visualize_results(category_counts):
    """可视化分类统计结果"""
    # 准备数据
    categories = list(category_counts.keys())
    counts = list(category_counts.values())
    
    # 设置样式
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))
    
    # 创建条形图
    ax = sns.barplot(x=counts, y=categories, palette="viridis")
    ax.set_title(f'arXiv Math Papers Classification (Last {MAX_RESULTS} Papers)', fontsize=16)
    ax.set_xlabel('Number of Papers', fontsize=14)
    ax.set_ylabel('Categories', fontsize=14)
    
    # 添加数值标签
    for i, v in enumerate(counts):
        ax.text(v + 0.5, i, str(v), color='black', va='center')
    
    plt.tight_layout()
    plt.savefig('arxiv_math_classification.png')
    plt.show()
    
    # 创建词云
    if category_counts.get('Other', 0) > 0:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies({'Other': category_counts['Other']})
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Unclassified Papers (Other)', fontsize=16)
        plt.savefig('arxiv_math_other_wordcloud.png')
        plt.show()

def main():
    print("Fetching arXiv math papers...")
    papers = get_arxiv_papers()
    print(f"Retrieved {len(papers)} papers.")
    
    print("Classifying papers...")
    category_counts, classified_papers = analyze_papers(papers)
    
    print("\nClassification Results:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{category}: {count} papers")
    
    print("\nGenerating visualizations...")
    visualize_results(category_counts)
    print("Visualizations saved as 'arxiv_math_classification.png' and 'arxiv_math_other_wordcloud.png'")

if __name__ == "__main__":
    main()
