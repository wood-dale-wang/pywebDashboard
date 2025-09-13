// static/js/dashboard.js
class DashboardManager {
    constructor() {
        this.widgets = new Map();
        this.refreshIntervals = new Map();
    }

    async initializeWidget(widgetName, config) {
        try {
            const response = await fetch(`/api/widget/${widgetName}`);
            const result = await response.json();

            if (result.status === 'success') {
                this.renderWidget(widgetName, result.data, config);
                this.updateWidgetStatus(widgetName, 'online');
            } else {
                this.showWidgetError(widgetName, result.message);
                this.updateWidgetStatus(widgetName, 'error');
            }
        } catch (error) {
            this.showWidgetError(widgetName, error.message);
            this.updateWidgetStatus(widgetName, 'offline');
        }
    }

    renderWidget(widgetName, data, config) {
        const widgetElement = document.getElementById(`widget-${widgetName}`);
        if (!widgetElement) return;
        widgetElement.style.display = '';
        // 根据widget类型渲染不同内容
        switch (config.type) {
            case 'card':
                widgetElement.innerHTML = this.renderCard(data);
                break;
            case 'chart':
                widgetElement.innerHTML = this.renderChart(data);
                break;
            case 'list':
                widgetElement.innerHTML = this.renderList(data);
                break;
            case 'digital':
                widgetElement.innerHTML = this.renderDigital(data);
                break;
            default:
                widgetElement.innerHTML = this.renderDefault(data);
        }
    }

    /**
     * 将数据对象渲染为 HTML 卡片字符串
     * @param {Object} data - 包含多个数据对象的对象
     * @returns {string} - 生成的 HTML 字符串
     */
    renderCard(data) {
        // 用于累积最终 HTML 的数组
        const htmlParts = [];

        // 遍历每个数据对象
        for (const [key, obj] of Object.entries(data)) {
            const { type, ...rest } = obj;

            if (type === 'stacked-bar-chart') {
                const { total, ...items } = rest;
                // 计算已用比例
                const used = Object.entries(items).reduce((s, [, v]) => s + v, 0);
                const left = Math.max(0, total - used);   // 防止负值
                const bars = Object.entries(items)
                    .map(([name, value]) => {
                        const percent = ((value / total) * 100).toFixed(2);
                        return `<div style="background:#555;height:12px;flex:${percent};margin-right:2px;"
                    title="${name}: ${value}"></div>`;
                    })
                    .join('');

                // 如果还有剩余，就补一段透明占位
                const restBar = left > 0
                    ? `<div style="height:12px;flex:${((left / total) * 100).toFixed(2)};background:transparent;"></div>`
                    : '';

                htmlParts.push(`<div style="margin-bottom:16px;">
        <div style="font-weight:bold;margin-bottom:4px;">${key}</div>
        <div style="display:flex;width:100%;background:#eee;align-items:center;">
            ${bars}${restBar}
        </div>
    </div>
`);
            } else if (type === 'table') {
                const rows = Object.entries(rest)
                    .map(([k, v]) => `<tr><td style="padding:4px 8px; border:1px solid #ccc;">${k}</td><td style="padding:4px 8px; border:1px solid #ccc;">${v}</td></tr>`)
                    .join('');
                htmlParts.push(`
                <div style="margin-bottom:16px;">
                    <div style="font-weight:bold; margin-bottom:4px;">${key}</div>
                    <table style="border-collapse:collapse; width:100%;">
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            `);
            }
            // 可继续扩展其它 type
        }
        return htmlParts.join('');
    }

    renderChart(data) {
        // 简单的图表渲染，实际项目中可以使用Chart.js等库
        return `
            <div class="chart-widget">
                <canvas id="chart-${Date.now()}"></canvas>
                <div class="chart-legend">
                    ${data.series ? data.series.map((s, i) =>
            `<span class="legend-item" style="color: ${this.getColor(i)}">${s.name}</span>`
        ).join('') : ''}
                </div>
            </div>
        `;
    }

    renderList(data) {
        return `
            <div class="list-widget">
                ${data.items ? data.items.map(item => `
                    <div class="list-item">
                        <div class="list-item-title">${item.title}</div>
                        <div class="list-item-meta">${item.summary || ''}</div>
                        <span class="list-item-meta">
                            <span class="author">${item.author}</span>
                            <span class="meta">${item.meta}</span>
                        </span>
                    </div>
                `).join('') : '<div class="empty">暂无数据</div>'}
            </div>
        `;
    }

    renderDigital(data) {
        return `
            <div class="digital-widget">
                <div class="digital-time">${data.time || '--:--:--'}</div>
                <div class="digital-date">${data.date || ''}</div>
            </div>
        `;
    }

    updateWidgetStatus(widgetName, status) {
        const statusElement = document.getElementById(`status-${widgetName}`);
        if (statusElement) {
            statusElement.className = `widget-status status-${status}`;
        }
    }

    showWidgetError(widgetName, error) {
        const widgetElement = document.getElementById(`widget-${widgetName}`);
        if (widgetElement) {
            widgetElement.innerHTML = `<div class="error">错误: ${error}</div>`;
        }
    }

    getColor(index) {
        const colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'];
        return colors[index % colors.length];
    }
}

// 全局函数
let dashboardManager;

function initializeDashboard(widgets) {
    dashboardManager = new DashboardManager();

    widgets.forEach(widget => {
        dashboardManager.initializeWidget(widget.name, widget.config);

        // 设置自动刷新
        if (widget.config.refresh_interval > 0) {
            setInterval(() => {
                dashboardManager.initializeWidget(widget.name, widget.config);
            }, widget.config.refresh_interval);
        }
    });
}

function refreshWidget(widgetName) {
    const widget = Array.from(dashboardManager.widgets.keys()).find(w => w === widgetName);
    if (widget) {
        dashboardManager.initializeWidget(widgetName, widget);
    }
}

function refreshAllWidgets() {
    dashboardManager.widgets.forEach((config, widgetName) => {
        dashboardManager.initializeWidget(widgetName, config);
    });
}

function toggleLayout() {
    const container = document.querySelector('.dashboard-container');
    const currentLayout = container.classList.contains('layout-grid') ? 'grid' :
        container.classList.contains('layout-list') ? 'list' : 'masonry';

    let newLayout;
    switch (currentLayout) {
        case 'grid': newLayout = 'list'; break;
        case 'list': newLayout = 'masonry'; break;
        default: newLayout = 'grid';
    }

    container.className = `dashboard-container layout-${newLayout}`;
    localStorage.setItem('dashboardLayout', newLayout);
}

// 从localStorage恢复布局偏好
document.addEventListener('DOMContentLoaded', function () {
    const savedLayout = localStorage.getItem('dashboardLayout');
    if (savedLayout) {
        const container = document.querySelector('.dashboard-container');
        container.className = `dashboard-container layout-${savedLayout}`;
    }
});