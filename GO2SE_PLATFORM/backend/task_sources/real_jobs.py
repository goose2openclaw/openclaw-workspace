"""
💼 真实外部工作池
==================
从公开API获取真实工作机会
"""

import requests
import re
from datetime import datetime
from typing import List, Dict

class RealJobsSource:
    """真实工作数据源"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; GO2SE-Genius/1.0)"
        })
        self.proxies = {
            "http": "http://172.29.144.1:7897",
            "https": "http://172.29.144.1:7897"
        }
    
    def fetch_remotive_jobs(self, category: str = "software-dev", limit: int = 20) -> List[Dict]:
        """从Remotive获取远程工作"""
        try:
            resp = self.session.get(
                f"https://remotive.com/api/remote-jobs?category={category}&limit={limit}",
                timeout=15,
                proxies=self.proxies
            )
            if resp.status_code == 200:
                data = resp.json()
                jobs = []
                for j in data.get("jobs", []):
                    # 估算价值
                    salary = j.get("salary") or ""
                    reward = self._estimate_value(salary)
                    
                    jobs.append({
                        "id": f"remotive_{str(j.get('id', ''))[:8]}",
                        "source": "Remotive",
                        "title": j.get("title", "Unknown"),
                        "company": j.get("company_name", "Unknown"),
                        "description": (j.get("description") or "")[:200],
                        "salary": salary if salary else "未公开",
                        "location": j.get("candidate_required_location", "全球"),
                        "url": j.get("url", ""),
                        "category": category,
                        "job_type": j.get("job_type", "full_time"),
                        "published": j.get("publication_date", ""),
                        "reward": reward,
                        "found_at": datetime.now().isoformat()
                    })
                return jobs
        except Exception as e:
            print(f"❌ Remotive错误: {e}")
        return []
    
    def _estimate_value(self, salary: str) -> int:
        """估算月收入"""
        if not salary:
            return 100
        try:
            nums = re.findall(r'\d+', salary.replace(",", ""))
            if nums:
                num = int(nums[0])
                if "k" in salary.lower() or num > 1000:
                    return min(num, 10000)
                return min(num * 160, 5000)  # 时薪转月薪
        except:
            pass
        return 100
    
    def fetch_all_jobs(self) -> List[Dict]:
        """获取所有真实工作"""
        all_jobs = []
        
        categories = ["software-dev", "business", "design", "marketing", "customer-service"]
        for cat in categories:
            jobs = self.fetch_remotive_jobs(cat, 10)
            all_jobs.extend(jobs)
        
        return all_jobs


def get_real_jobs() -> List[Dict]:
    """便捷函数"""
    source = RealJobsSource()
    return source.fetch_all_jobs()
