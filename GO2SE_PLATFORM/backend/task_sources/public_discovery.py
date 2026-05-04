"""
🔍 公开任务发现系统
====================
无需API密钥，通过网页抓取获取公开任务
"""

import requests
import re
from typing import List, Dict
from datetime import datetime

class PublicTaskDiscovery:
    """公开任务发现器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # 公开任务来源
        self.public_sources = {
            # Python Freelance工作
            "remoteok": {
                "url": "https://remoteok.com/remote-python-jobs",
                "parser": self._parse_remoteok
            },
            "weworkremotely": {
                "url": "https://weworkremotely.com/remote-jobs/search?utf8=✓&term=python",
                "parser": self._parse_wwr
            },
            "remote_co": {
                "url": "https://remote.co/remote-jobs/search/?search=python",
                "parser": self._parse_remoteco
            }
        }
    
    def discover(self, keyword: str = "python", limit: int = 20) -> List[Dict]:
        """发现公开任务"""
        all_tasks = []
        
        for name, source in self.public_sources.items():
            try:
                tasks = self._fetch_source(source["url"], source["parser"], keyword)
                all_tasks.extend(tasks)
            except Exception as e:
                print(f"⚠️ {name}抓取失败: {e}")
        
        # 去重并排序
        seen = set()
        unique_tasks = []
        for task in all_tasks:
            if task["id"] not in seen:
                seen.add(task["id"])
                unique_tasks.append(task)
        
        unique_tasks.sort(key=lambda x: x.get("score", 0), reverse=True)
        return unique_tasks[:limit]
    
    def _fetch_source(self, url: str, parser, keyword: str) -> List[Dict]:
        """抓取单个来源"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return parser(response.text, keyword)
        except Exception as e:
            print(f"⚠️ 请求失败: {e}")
        return []
    
    def _parse_remoteok(self, html: str, keyword: str) -> List[Dict]:
        """解析RemoteOK"""
        tasks = []
        # 简化解析
        pattern = r'data-company="([^"]+)".*?data-position="([^"]+)".*?(\$[\d,]+)'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for i, (company, position, pay) in enumerate(matches[:10]):
            tasks.append({
                "id": f"remoteok_{i}",
                "source": "RemoteOK",
                "company": company.strip(),
                "title": position.strip(),
                "salary": pay.strip(),
                "category": "freelance",
                "score": 80,
                "url": "https://remoteok.com",
                "found_at": datetime.now().isoformat()
            })
        return tasks
    
    def _parse_wwr(self, html: str, keyword: str) -> List[Dict]:
        """解析WeWorkRemotely"""
        tasks = []
        pattern = r'class="company">([^<]+)</div>.*?class="title">([^<]+)</div>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for i, (company, title) in enumerate(matches[:10]):
            tasks.append({
                "id": f"wwr_{i}",
                "source": "WeWorkRemotely",
                "company": company.strip(),
                "title": title.strip(),
                "salary": "待定",
                "category": "freelance",
                "score": 75,
                "url": "https://weworkremotely.com",
                "found_at": datetime.now().isoformat()
            })
        return tasks
    
    def _parse_remoteco(self, html: str, keyword: str) -> List[Dict]:
        """解析Remote.co"""
        tasks = []
        pattern = r'<h2>([^<]+)</h2>.*?<p>([^<]+)</p>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for i, (title, company) in enumerate(matches[:10]):
            tasks.append({
                "id": f"remoteco_{i}",
                "source": "Remote.co",
                "company": company.strip()[:50],
                "title": title.strip(),
                "salary": "待定",
                "category": "freelance",
                "score": 70,
                "url": "https://remote.co",
                "found_at": datetime.now().isoformat()
            })
        return tasks


def get_public_tasks(keyword: str = "python", limit: int = 20) -> List[Dict]:
    """便捷函数"""
    discovery = PublicTaskDiscovery()
    return discovery.discover(keyword, limit)
