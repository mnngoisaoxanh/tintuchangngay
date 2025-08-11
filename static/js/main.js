class NewsApp {
    constructor() {
        this.currentDate = new Date().toISOString().split('T')[0];
        this.currentSource = '';
        this.sources = [];
        this.availableDates = [];
        this.currentArticles = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadSources();
        await this.loadAvailableDates();
        await this.loadNews();
        this.updateLastUpdateTime();
    }

    setupEventListeners() {
        // Date selector
        document.getElementById('dateSelect').addEventListener('change', (e) => {
            this.currentDate = e.target.value;
            this.loadNews();
        });

        // Source filter
        document.getElementById('sourceFilter').addEventListener('change', (e) => {
            this.currentSource = e.target.value;
            this.filterNews();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshPage();
        });

        // Manage sources button
        document.getElementById('manageSourcesBtn').addEventListener('click', () => {
            this.showSourceModal();
        });

        // Modal close
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideSourceModal();
        });

        // Add source form
        document.getElementById('addSourceForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addSource();
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('sourceModal');
            if (e.target === modal) {
                this.hideSourceModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideSourceModal();
            }
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshPage();
            }
        });
    }

    async loadSources() {
        try {
            const response = await fetch('src/rss_sources.json?' + Date.now());
            if (response.ok) {
                const data = await response.json();
                this.sources = data.sources;
                this.updateSourceFilter();
                this.updateStats();
            } else {
                throw new Error('Cannot load sources');
            }
        } catch (error) {
            console.error('Lỗi khi tải danh sách nguồn:', error);
            // Fallback to default sources
            this.sources = [
                { name: "VnExpress", url: "https://vnexpress.net/rss/tin-moi-nhat.rss", category: "Tổng hợp" },
                { name: "Dân Trí", url: "https://dantri.com.vn/rss.rss", category: "Tổng hợp" },
                { name: "Thanh Niên", url: "https://thanhnien.vn/rss/home.rss", category: "Tổng hợp" },
                { name: "Tuổi Trẻ", url: "https://tuoitre.vn/rss/tin-moi-nhat.rss", category: "Tổng hợp" }
            ];
            this.updateSourceFilter();
            this.updateStats();
        }
    }

    async loadAvailableDates() {
        try {
            // Tạo script tag để load available dates
            const script = document.createElement('script');
            script.src = 'static/js/data/index.js?' + Date.now();
            
            return new Promise((resolve, reject) => {
                script.onload = () => {
                    if (window.availableDates && window.availableDates.length > 0) {
                        this.availableDates = window.availableDates;
                    } else {
                        // Fallback: tạo 7 ngày gần đây
                        this.availableDates = this.generateFallbackDates();
                    }
                    this.updateDateSelector();
                    resolve();
                };
                
                script.onerror = () => {
                    console.warn('Không thể load file index, sử dụng fallback dates');
                    this.availableDates = this.generateFallbackDates();
                    this.updateDateSelector();
                    resolve();
                };
                
                document.head.appendChild(script);
                
                // Timeout fallback
                setTimeout(() => {
                    if (this.availableDates.length === 0) {
                        this.availableDates = this.generateFallbackDates();
                        this.updateDateSelector();
                        resolve();
                    }
                }, 3000);
            });
        } catch (error) {
            console.error('Lỗi khi tải ngày:', error);
            this.availableDates = this.generateFallbackDates();
            this.updateDateSelector();
        }
    }

    generateFallbackDates() {
        const dates = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toISOString().split('T')[0]);
        }
        return dates;
    }

    updateDateSelector() {
        const select = document.getElementById('dateSelect');
        select.innerHTML = '';
        
        if (this.availableDates.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Không có dữ liệu';
            select.appendChild(option);
            return;
        }
        
        this.availableDates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = this.formatDate(date);
            if (date === this.currentDate) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        // Nếu ngày hiện tại không có trong danh sách, chọn ngày gần nhất
        if (!this.availableDates.includes(this.currentDate)) {
            this.currentDate = this.availableDates[0];
            select.value = this.currentDate;
        }
    }

    updateSourceFilter() {
        const select = document.getElementById('sourceFilter');
        const currentValue = select.value;
        
        select.innerHTML = '<option value="">Tất cả nguồn</option>';
        
        const uniqueSources = [...new Set(this.sources.map(s => s.name))];
        uniqueSources.forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            select.appendChild(option);
        });
        
        select.value = currentValue;
    }

    updateStats() {
        document.getElementById('totalSources').textContent = this.sources.length;
    }

    async loadNews() {
        this.showLoading();
        
        try {
            const dateKey = this.currentDate.replace(/-/g, '_');
            
            // Remove old script if exists
            const oldScript = document.getElementById(`news-script-${dateKey}`);
            if (oldScript) {
                oldScript.remove();
            }
            
            const script = document.createElement('script');
            script.id = `news-script-${dateKey}`;
            script.src = `static/js/data/${this.currentDate}.js?` + Date.now();
            
            return new Promise((resolve) => {
                script.onload = () => {
                    const newsData = window[`newsData_${dateKey}`];
                    if (newsData && newsData.articles && newsData.articles.length > 0) {
                        this.currentArticles = newsData.articles;
                        this.displayNews(this.currentArticles);
                        this.updateNewsTitle();
                    } else {
                        this.currentArticles = [];
                        this.showNoNews();
                    }
                    resolve();
                };
                
                script.onerror = () => {
                    this.currentArticles = [];
                    this.showNoNews();
                    resolve();
                };
                
                document.head.appendChild(script);
                
                // Timeout fallback
                setTimeout(() => {
                    if (document.getElementById('loading').style.display !== 'none') {
                        this.currentArticles = [];
                        this.showNoNews();
                        resolve();
                    }
                }, 5000);
            });
        } catch (error) {
            console.error('Lỗi khi tải tin tức:', error);
            this.currentArticles = [];
            this.showNoNews();
        }
    }

    displayNews(articles) {
        const container = document.getElementById('newsList');
        container.innerHTML = '';

        if (!articles || articles.length === 0) {
            this.showNoNews();
            return;
        }

        // Lọc theo nguồn nếu có
        const filteredArticles = this.currentSource 
            ? articles.filter(article => article.source === this.currentSource)
            : articles;

        if (filteredArticles.length === 0) {
            this.showNoNews();
            return;
        }

        // Sort by published date (newest first)
        filteredArticles.sort((a, b) => new Date(b.published) - new Date(a.published));

        filteredArticles.forEach(article => {
            const articleElement = this.createArticleElement(article);
            container.appendChild(articleElement);
        });

        // Update article count
        document.getElementById('displayedCount').textContent = filteredArticles.length;
        document.getElementById('totalArticles').textContent = articles.length;

        this.hideLoading();
        document.getElementById('newsContainer').style.display = 'block';
    }

    createArticleElement(article) {
        const div = document.createElement('div');
        div.className = 'news-item';
        
        const publishedDate = new Date(article.published);
        const timeString = publishedDate.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        // Clean summary text
        const summary = this.cleanText(article.summary || '');
        const title = this.cleanText(article.title || 'Không có tiêu đề');
        
        div.innerHTML = `
            <div class="news-meta">
                <span class="news-source">${this.escapeHtml(article.source)}</span>
                <span class="news-time">📅 ${timeString}</span>
            </div>
            <div class="news-title">
                <a href="${article.link}" target="_blank" rel="noopener noreferrer">${title}</a>
            </div>
            <div class="news-summary">${summary}</div>
            <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="news-link">
                📖 Đọc tiếp →
            </a>
        `;
        
        return div;
    }

    cleanText(text) {
        if (!text) return '';
        // Remove HTML tags and decode entities
        const div = document.createElement('div');
        div.innerHTML = text;
        return div.textContent || div.innerText || '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    filterNews() {
        this.displayNews(this.currentArticles);
    }

    updateNewsTitle() {
        const titleElement = document.getElementById('newsTitle');
        if (this.currentDate === new Date().toISOString().split('T')[0]) {
            titleElement.textContent = 'Tin tức hôm nay';
        } else {
            titleElement.textContent = `Tin tức ngày ${this.formatDate(this.currentDate)}`;
        }
    }

    refreshPage() {
        this.showLoading();
        location.reload();
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('newsContainer').style.display = 'none';
        document.getElementById('noNews').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showNoNews() {
        this.hideLoading();
        document.getElementById('newsContainer').style.display = 'none';
        document.getElementById('noNews').style.display = 'block';
        
        // Update counts
        document.getElementById('displayedCount').textContent = '0';
        document.getElementById('totalArticles').textContent = '0';
    }

    // Modal functions
    showSourceModal() {
        document.getElementById('sourceModal').style.display = 'block';
        this.loadSourceList();
        document.body.style.overflow = 'hidden'; // Prevent body scroll
    }

    hideSourceModal() {
        document.getElementById('sourceModal').style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore body scroll
    }

    loadSourceList() {
        const container = document.getElementById('sourceListContainer');
        container.innerHTML = '';

        if (this.sources.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">Chưa có nguồn nào</p>';
            return;
        }

        this.sources.forEach((source, index) => {
            const div = document.createElement('div');
            div.className = 'source-item';
            div.innerHTML = `
                <div class="source-info">
                    <h4>${this.escapeHtml(source.name)}</h4>
                    <p>${this.escapeHtml(source.url)}</p>
                    <small>Danh mục: ${this.escapeHtml(source.category || 'Không xác định')}</small>
                </div>
                <div class="source-actions">
                    <button class="btn btn-danger" onclick="newsApp.removeSource(${index})">🗑️ Xóa</button>
                </div>
            `;
            container.appendChild(div);
        });
    }

    addSource() {
        const name = document.getElementById('sourceName').value.trim();
        const url = document.getElementById('sourceUrl').value.trim();
        const category = document.getElementById('sourceCategory').value.trim();

        if (!name || !url) {
            alert('⚠️ Vui lòng điền đầy đủ thông tin');
            return;
        }

        // Validate URL
        try {
            new URL(url);
        } catch (e) {
            alert('⚠️ URL không hợp lệ');
            return;
        }

        // Check if source already exists
        if (this.sources.some(s => s.url === url)) {
            alert('⚠️ Nguồn này đã tồn tại');
            return;
        }

        const newSource = { 
            name, 
            url, 
            category: category || 'Tổng hợp' 
        };
        
        this.sources.push(newSource);
        
        this.updateSourceFilter();
        this.updateStats();
        this.loadSourceList();
        
        // Reset form
        document.getElementById('addSourceForm').reset();
        document.getElementById('sourceCategory').value = 'Tổng hợp';
        
        alert('✅ Đã thêm nguồn mới! Lưu ý: Thay đổi chỉ có hiệu lực trong phiên làm việc này.');
    }

    removeSource(index) {
        if (index < 0 || index >= this.sources.length) {
            return;
        }

        const source = this.sources[index];
        if (confirm(`🗑️ Bạn có chắc muốn xóa nguồn "${source.name}"?`)) {
            this.sources.splice(index, 1);
            this.updateSourceFilter();
            this.updateStats();
            this.loadSourceList();
            
            // If current filter is the removed source, reset filter
            if (this.currentSource === source.name) {
                this.currentSource = '';
                document.getElementById('sourceFilter').value = '';
                this.filterNews();
            }
            
            alert('✅ Đã xóa nguồn!');
        }
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            const dateStr = date.toISOString().split('T')[0];
            const todayStr = today.toISOString().split('T')[0];
            const yesterdayStr = yesterday.toISOString().split('T')[0];
            
            if (dateStr === todayStr) {
                return '📅 Hôm nay';
            } else if (dateStr === yesterdayStr) {
                return '📅 Hôm qua';
            } else {
                return '📅 ' + date.toLocaleDateString('vi-VN', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }
        } catch (e) {
            return dateString;
        }
    }

    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('lastUpdate').textContent = timeString;
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
});

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.newsApp = new NewsApp();
    });
} else {
    window.newsApp = new NewsApp();
}

// Service Worker registration (optional, for caching)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment if you want to add service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}
