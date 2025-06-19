# SFPR

## 技术栈

### 后端
- Python 3.10+
- Django 4.2
- Django REST framework
- PostgreSQL
- Redis
- Celery

### 前端
- React 18
- TypeScript
- TailwindCSS
- shadcn/ui

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/stillalive.git
cd stillalive
```

2. 安装依赖
```bash
# 后端
cd Server
pip install -r requirements.txt


3. 配置环境变量
```bash
# 后端
cp .env.example .env
# 编辑 .env 文件，填写必要的配置

```

4. 运行开发服务器
```bash
# 后端
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000

```

## 部署

1. 后端部署
- 使用 Docker Compose 进行容器化部署
- 配置 Nginx 作为反向代理
- 设置 SSL 证书实现 HTTPS

2. 前端部署
- 构建静态文件：`npm run build`
- 使用 Nginx 托管静态文件
- 配置 CORS 和缓存策略

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
