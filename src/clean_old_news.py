import os
import json
from datetime import datetime, timedelta
import pytz

def clean_old_news():
    """Xóa tin tức cũ hơn 7 ngày"""
    data_dir = "data/news"
    js_dir = "static/js/data"
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    cutoff_date = datetime.now(timezone) - timedelta(days=7)
    
    removed_files = []
    
    print("=== Bắt đầu dọn dẹp tin cũ ===")
    
    # Xóa JSON files cũ
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                try:
                    date_str = filename.replace('.json', '')
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    file_date = timezone.localize(file_date)
                    
                    if file_date < cutoff_date:
                        file_path = os.path.join(data_dir, filename)
                        os.remove(file_path)
                        removed_files.append(filename)
                        print(f"Đã xóa JSON: {filename}")
                        
                except ValueError:
                    continue
    
    # Xóa JS files cũ
    if os.path.exists(js_dir):
        for filename in os.listdir(js_dir):
            if filename.endswith('.js') and filename != 'index.js':
                try:
                    date_str = filename.replace('.js', '')
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    file_date = timezone.localize(file_date)
                    
                    if file_date < cutoff_date:
                        file_path = os.path.join(js_dir, filename)
                        os.remove(file_path)
                        removed_files.append(filename)
                        print(f"Đã xóa JS: {filename}")
                        
                except ValueError:
                    continue
    
    # Cập nhật lại file index sau khi xóa
    update_date_index(js_dir, timezone)
    
    if removed_files:
        print(f"Tổng cộng đã xóa {len(removed_files)} file tin cũ")
    else:
        print("Không có file tin cũ nào cần xóa")
    
    print("=== Hoàn thành dọn dẹp ===")

def update_date_index(js_dir, timezone):
    """Cập nhật lại file index sau khi xóa file cũ"""
    try:
        available_dates = []
        if os.path.exists(js_dir):
            for filename in os.listdir(js_dir):
                if filename.endswith('.js') and filename != 'index.js':
                    date_str = filename.replace('.js', '')
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        available_dates.append(date_str)
                    except ValueError:
                        continue
        
        available_dates.sort(reverse=True)  # Mới nhất trước
        
        # Tạo file index
        index_file = os.path.join(js_dir, 'index.js')
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("window.availableDates = ")
            f.write(json.dumps(available_dates, ensure_ascii=False, indent=2))
            f.write(';')
            
        print(f"Đã cập nhật index với {len(available_dates)} ngày")
        
    except Exception as e:
        print(f"Lỗi khi cập nhật file index: {e}")

if __name__ == "__main__":
    clean_old_news()
