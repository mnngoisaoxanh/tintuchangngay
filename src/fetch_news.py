import feedparser
import json
import os
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import hashlib

class NewsAggregator:
    def __init__(self):
        self.data_dir = "data/news"
        self.js_dir = "static/js/data"
        self.sources_file = "src/rss_sources.json"
        self.timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        
        # Tạo thư mục data nếu chưa có
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.js_dir, exist_ok=True)
        
    def load_sources(self):
        """Load RSS sources từ file JSON"""
        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Tạo file mặc định nếu chưa có
            default_sources = {
                "sources": [
                    {
                        "name": "VnExpress",
                        "url": "https://vnexpress.net/rss/tin-moi-nhat.rss",
                        "category": "Tổng hợp"
                    },
                    {
                        "name": "Dân Trí",
                        "url": "https://dantri.com.vn/rss.rss",
                        "category": "Tổng hợp"
                    },
                    {
                        "name": "Thanh Niên",
                        "url": "https://thanhnien.vn/rss/home.rss",
                        "category": "Tổng hợp"
                    },
                    {
                        "name": "Tuổi Trẻ",
                        "url": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
                        "category": "Tổng hợp"
                    }
                ]
            }
            # Tạo thư mục src nếu chưa có
            os.makedirs("src", exist_ok=True)
            with open(self.sources_file, 'w', encoding='utf-8') as f:
                json.dump(default_sources, f, ensure_ascii=False, indent=2)
            return default_sources
    
    def get_article_summary(self, url, max_length=200):
        """Lấy tóm tắt nội dung bài viết"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm đoạn tóm tắt cho từng trang báo
            summary = ""
            
            # VnExpress
            if 'vnexpress.net' in url:
                desc = soup.find('p', class_='description')
                if not desc:
                    desc = soup.find('div', class_='description')
                if desc:
                    summary = desc.get_text().strip()
                    
            # Dân Trí
            elif 'dantri.com.vn' in url:
                desc = soup.find('div', class_='singular-sapo')
                if not desc:
                    desc = soup.find('h2', class_='singular-sapo')
                if desc:
                    summary = desc.get_text().strip()
                    
            # Thanh Niên
            elif 'thanhnien.vn' in url:
                desc = soup.find('div', class_='sapo')
                if not desc:
                    desc = soup.find('h2', class_='sapo')
                if desc:
                    summary = desc.get_text().strip()
                    
            # Tuổi Trẻ
            elif 'tuoitre.vn' in url:
                desc = soup.find('h2', class_='sapo')
                if not desc:
                    desc = soup.find('div', class_='sapo')
                if desc:
                    summary = desc.get_text().strip()
            
            # Fallback: lấy đoạn đầu tiên
            if not summary:
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:
                        summary = text
                        break
            
            # Cắt ngắn tóm tắt
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
                
            return summary
            
        except Exception as e:
            print(f"Lỗi khi lấy tóm tắt từ {url}: {e}")
            return ""
    
    def fetch_rss(self, source):
        """Lấy tin từ một nguồn RSS"""
        try:
            print(f"Đang lấy tin từ {source['name']}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                print(f"Không lấy được tin từ {source['name']}")
                return []
                
            articles = []
            
            for entry in feed.entries[:15]:  # Lấy 15 tin mới nhất
                try:
                    # Tạo ID duy nhất cho bài viết
                    article_id = hashlib.md5(entry.link.encode()).hexdigest()
                    
                    # Lấy thời gian đăng
                    published = datetime.now(self.timezone)
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            published = datetime(*entry.published_parsed[:6])
                            published = self.timezone.localize(published)
                        except:
                            published = datetime.now(self.timezone)
                    
                    # Lấy tóm tắt
                    summary = ""
                    if hasattr(entry, 'summary') and entry.summary:
                        summary = BeautifulSoup(entry.summary, 'html.parser').get_text().strip()
                    
                    # Nếu tóm tắt quá ngắn, thử lấy từ bài viết
                    if not summary or len(summary) < 50:
                        full_summary = self.get_article_summary(entry.link)
                        if full_summary:
                            summary = full_summary
                    
                    # Nếu vẫn không có tóm tắt, dùng description hoặc title
                    if not summary:
                        if hasattr(entry, 'description'):
                            summary = BeautifulSoup(entry.description, 'html.parser').get_text().strip()
                        else:
                            summary = "Nhấp để xem chi tiết..."
                    
                    article = {
                        'id': article_id,
                        'title': entry.title.strip() if hasattr(entry, 'title') else 'Không có tiêu đề',
                        'link': entry.link,
                        'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                        'source': source['name'],
                        'category': source['category'],
                        'published': published.isoformat(),
                        'fetched': datetime.now(self.timezone).isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Lỗi khi xử lý bài viết từ {source['name']}: {e}")
                    continue
                
            print(f"Đã lấy {len(articles)} bài viết từ {source['name']}")
            return articles
            
        except Exception as e:
            print(f"Lỗi khi lấy RSS từ {source['name']}: {e}")
            return []
    
    def save_articles(self, articles):
        """Lưu tin tức vào file JSON theo ngày (backup)"""
        if not articles:
            return
            
        today = datetime.now(self.timezone).strftime('%Y-%m-%d')
        file_path = os.path.join(self.data_dir, f"{today}.json")
        
        # Load existing articles
        existing_articles = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except:
                existing_articles = []
        
        # Tạo set các ID đã có để tránh trùng lặp
        existing_ids = {article['id'] for article in existing_articles}
        
        # Thêm các bài viết mới
        new_articles = []
        for article in articles:
            if article['id'] not in existing_ids:
                new_articles.append(article)
                existing_articles.append(article)
        
        # Sắp xếp theo thời gian đăng (mới nhất trước)
        existing_articles.sort(key=lambda x: x['published'], reverse=True)
        
        # Lưu file JSON
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_articles, f, ensure_ascii=False, indent=2)
            
            if new_articles:
                print(f"Đã lưu {len(new_articles)} bài viết mới vào {file_path}")
        except Exception as e:
            print(f"Lỗi khi lưu file JSON: {e}")

    def save_articles_as_js(self, articles, date_str):
        """Lưu tin tức vào file JavaScript để tránh CORS"""
        if not articles:
            # Tạo file rỗng nếu không có bài viết
            js_file = os.path.join(self.js_dir, f"{date_str}.js")
            js_data = {
                'date': date_str,
                'lastUpdated': datetime.now(self.timezone).isoformat(),
                'articles': []
            }
            
            try:
                with open(js_file, 'w', encoding='utf-8') as f:
                    f.write(f"window.newsData_{date_str.replace('-', '_')} = ")
                    f.write(json.dumps(js_data, ensure_ascii=False, indent=2))
                    f.write(';')
            except Exception as e:
                print(f"Lỗi khi tạo file JS rỗng: {e}")
            return
            
        # Load existing articles từ file JS
        js_file = os.path.join(self.js_dir, f"{date_str}.js")
        existing_articles = []
        
        if os.path.exists(js_file):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract JSON từ "window.newsData = {...}"
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = content[start:end]
                        data = json.loads(json_str)
                        existing_articles = data.get('articles', [])
            except Exception as e:
                print(f"Lỗi khi đọc file JS cũ: {e}")
                existing_articles = []
        
        # Tạo set các ID đã có để tránh trùng lặp
        existing_ids = {article['id'] for article in existing_articles}
        
        # Thêm các bài viết mới
        new_articles = []
        for article in articles:
            if article['id'] not in existing_ids:
                new_articles.append(article)
                existing_articles.append(article)
        
        # Sắp xếp theo thời gian đăng (mới nhất trước)
        existing_articles.sort(key=lambda x: x['published'], reverse=True)
        
        # Tạo object JavaScript
        js_data = {
            'date': date_str,
            'lastUpdated': datetime.now(self.timezone).isoformat(),
            'articles': existing_articles
        }
        
        # Lưu file JavaScript
        try:
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(f"window.newsData_{date_str.replace('-', '_')} = ")
                f.write(json.dumps(js_data, ensure_ascii=False, indent=2))
                f.write(';')
            
            if new_articles:
                print(f"Đã lưu {len(new_articles)} bài viết mới vào {js_file}")
            else:
                print(f"Cập nhật file {js_file} (không có bài viết mới)")
                
        except Exception as e:
            print(f"Lỗi khi lưu file JS: {e}")

    def create_date_index(self):
        """Tạo file index các ngày có data"""
        try:
            # Lấy danh sách các file JS
            available_dates = []
            if os.path.exists(self.js_dir):
                for filename in os.listdir(self.js_dir):
                    if filename.endswith('.js') and filename != 'index.js':
                        date_str = filename.replace('.js', '')
                        # Validate date format
                        try:
                            datetime.strptime(date_str, '%Y-%m-%d')
                            available_dates.append(date_str)
                        except ValueError:
                            continue
            
            # Thêm ngày hôm nay nếu chưa có
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            if today not in available_dates:
                available_dates.append(today)
            
            available_dates.sort(reverse=True)  # Mới nhất trước
            
            # Tạo file index
            index_file = os.path.join(self.js_dir, 'index.js')
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write("window.availableDates = ")
                f.write(json.dumps(available_dates, ensure_ascii=False, indent=2))
                f.write(';')
                
            print(f"Đã tạo index với {len(available_dates)} ngày có dữ liệu")
            
        except Exception as e:
            print(f"Lỗi khi tạo file index: {e}")
    
    def run(self):
        """Chạy thu thập tin tức"""
        print("=== Bắt đầu thu thập tin tức ===")
        
        sources = self.load_sources()
        all_articles = []
        
        for source in sources['sources']:
            try:
                articles = self.fetch_rss(source)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Lỗi nghiêm trọng khi xử lý nguồn {source.get('name', 'Unknown')}: {e}")
                continue
        
        today = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        print(f"\n=== Tổng kết ===")
        print(f"Tổng cộng thu thập được: {len(all_articles)} bài viết")
        
        # Lưu cả JSON (backup) và JS (cho web)
        self.save_articles(all_articles)
        self.save_articles_as_js(all_articles, today)
        
        # Tạo index file cho các ngày có data
        self.create_date_index()
        
        print(f"Hoàn thành thu thập tin tức cho ngày {today}")
        print("===============================")

if __name__ == "__main__":
    aggregator = NewsAggregator()
    aggregator.run()
