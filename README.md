# 🗞️ News Aggregator

Hệ thống thu thập tin tức tự động từ các báo lớn Việt Nam, cập nhật mỗi 2 tiếng và hiển thị trên GitHub Pages.

## ✨ Tính năng

- 🔄 **Thu thập tự động**: Lấy tin từ RSS feeds mỗi 2 tiếng
- 📱 **Responsive design**: Tương thích mọi thiết bị
- 🗂️ **Lọc và tìm kiếm**: Theo nguồn, ngày, và danh mục
- ⚙️ **Quản lý nguồn**: Thêm/xóa nguồn RSS trực tiếp trên web
- 💾 **Lưu trữ 7 ngày**: Tự động xóa tin cũ
- 🚀 **Zero maintenance**: Hoàn toàn tự động trên GitHub Actions

## 🌐 Demo

[Xem tại đây](https://hotrung1234.github.io/news-aggregator)

## 📊 Nguồn tin hiện tại

- VnExpress (Tổng hợp, Thế giới, Kinh doanh, Công nghệ, Thể thao)
- Dân Trí
- Thanh Niên  
- Tuổi Trẻ

## 🛠️ Cấu trúc dự án"# news-aggregator" 
news-aggregator/
├── .github/workflows/    # GitHub Actions
├── src/                  # Python scripts
├── static/              # CSS, JS, assets
├── data/news/           # JSON backup files
└── index.html           # Trang web chính

## 🚀 Cài đặt

1. Fork repository này
2. Bật GitHub Pages trong Settings → Pages → Source: GitHub Actions
3. Workflow sẽ tự động chạy và tạo website

## ⚙️ Tùy chỉnh

### Thêm nguồn RSS mới

Chỉnh sửa file `src/rss_sources.json`:

```json
{
  "sources": [
    {
      "name": "Tên báo",
      "url": "https://example.com/rss.xml",
      "category": "Danh mục"
    }
  ]
}
