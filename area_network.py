import time
import requests
from bs4 import BeautifulSoup
import pandas
import re
import networkx as nx
import matplotlib
from pyvis.network import Network

#ページ取得
def parse_url(url, sleep_second=5):
    res = requests.get(url)
    time.sleep(sleep_second)
    return BeautifulSoup(res.content, "html.parser")

def get_elements(url):
    soup = parse_url(url)
    name_elements = soup.find_all('a', class_='cpy-rst-name')
    rank_elements = soup.find_all("i", class_="u-text-num")
    area_elements = soup.find_all("div", class_="cpy-area-genre")
    return name_elements, rank_elements, area_elements

#距離の抽出
# import re
# # distance_num = re.compile('[0-9]*')
# area_info = area_element.get_text().replace(' ','').rstrip().split('/')
# area = area_info[0]
# area_name = re.search(r'\D+',area).group()
# distance = int(re.search(r'\d+',area).group())

info = {}
import re
def get_info(area_elements, rank_elements, name_elements,info):
    for area_element, rank_element, name_element in zip(area_elements, rank_elements, name_elements):
    #     print('area',area.get_text().replace(' ','').rstrip().split('/'))
        rank = int(rank_element.get_text())
        area_info = area_element.get_text().replace(' ','').rstrip().split('/')
        area = area_info[0]
        area_name = re.search(r'\D+',area).group()
        try:
            distance = int(re.search(r'\d+',area).group())
        except:
            distance = 0
        genre = area_info[1].split('、')
        name = name_element.get_text(strip=True)
        info[rank] = {'name':name, 'genre':genre,'area':area_name,'distance':distance}
    return info
if __name__ == '__main__':
    url = 'https://tabelog.com/osaka/A2701/A270101/rstLst/?SrtT=rt&Srt=D&sort_mode=1'
    pagination_nums = soup.find_all('a',class_='c-pagination__num')
    last_page_num = pagination_nums[-1]
    info = {}
    for i in range(1,last_page_num):
        if i == 1:
            url = 'https://tabelog.com/osaka/A2701/A270101/rstLst/?SrtT=rt&Srt=D&sort_mode=1'
        else:
            url = 'https://tabelog.com/osaka/A2701/A270101/rstLst/{}/?SrtT=rt&Srt=D&sort_mode=1'.format(i)
        name_elements, rank_elements, area_elements = get_elements(url)
        info = get_info(area_elements, rank_elements, name_elements,info)
    df = pandas.DataFrame(info).T
    df['distance'] = df['distance'] / len(df)
    parent_list = list(df['area'].value_counts().index)
    # print(parent_list)
    child_list = list(df['name'])
    # print(child_list)
    G = nx.from_pandas_edgelist(df,source='area',target='name',edge_attr='distance')
    net = Network(notebook=True)
    net.from_nx(G)
    net.show('exaple.html')