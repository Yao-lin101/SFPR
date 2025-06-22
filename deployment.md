# CSList 部署指南

## 概述

CSList 是一个基于 Django + React 的 Web 应用，使用 Docker 进行容器化部署。

## 架构

- **后端**: Django + PostgreSQL + Redis + Celery
- **前端**: React + Vite
- **反向代理**: Nginx
- **容器化**: Docker + Docker Compose

## 部署前准备

### 1. 服务器要求

- Ubuntu 20.04+ 或 CentOS 7+
- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB RAM
- 至少 20GB 磁盘空间

### 2. 域名配置

确保以下域名指向你的服务器：
- `cslist.ineed.asia`
- `www.cslist.ineed.asia`

### 3. SSL 证书

将 SSL 证书文件放置在 `Server/ssl/` 目录：
```
Server/ssl/
├── cslist.ineed.asia.crt
└── cslist.ineed.asia.key
```

## 部署步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd CSList
```

### 2. 配置环境变量

复制环境变量模板并修改：

```bash
cd Server
cp .env .env.production
```

编辑 `.env.production` 文件，设置以下关键变量：

```bash
# Django 配置
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.production

# 数据库配置
DB_NAME=cslist
DB_PASSWORD=your-secure-database-password

# 邮件配置
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-email-app-password
DEFAULT_FROM_EMAIL=your-email@qq.com

# 其他配置根据需要修改
```

### 3. 运行部署脚本

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 生产环境部署
./deploy.sh prod
```

### 4. 创建超级用户

```bash
# 进入 web 容器
docker exec -it cslist_web bash

# 创建超级用户
python manage.py createsuperuser
```

## 服务管理

### 查看服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart web
```

### 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

## 数据备份

### 数据库备份

```bash
# 备份数据库
docker exec cslist_db pg_dump -U postgres cslist > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker exec -i cslist_db psql -U postgres cslist < backup_file.sql
```

### 媒体文件备份

```bash
# 备份媒体文件
docker run --rm -v cslist_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

## 更新部署

### 1. 更新代码

```bash
git pull origin main
```

### 2. 重新部署

```bash
./deploy.sh prod
```

## 监控和维护

### 1. 健康检查

访问 `https://cslist.ineed.asia/health/` 检查服务状态。

### 2. 日志监控

定期检查应用日志：

```bash
# 检查 Django 日志
docker-compose -f docker-compose.prod.yml logs web | tail -100

# 检查 Nginx 日志
docker-compose -f docker-compose.prod.yml logs nginx | tail -100
```

### 3. 磁盘空间监控

```bash
# 检查 Docker 卷使用情况
docker system df

# 清理未使用的 Docker 资源
docker system prune -a
```

## 故障排除

### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs [service_name]

# 检查容器状态
docker-compose -f docker-compose.prod.yml ps
```

### 2. 数据库连接失败

```bash
# 检查数据库容器状态
docker exec cslist_db pg_isready -U postgres

# 检查环境变量
docker exec cslist_web env | grep DB_
```

### 3. SSL 证书问题

确保证书文件路径正确且权限合适：

```bash
ls -la Server/ssl/
chmod 644 Server/ssl/*.crt
chmod 600 Server/ssl/*.key
```

## 性能优化

### 1. Nginx 优化

- 启用 gzip 压缩
- 设置适当的缓存策略
- 配置 rate limiting

### 2. Django 优化

- 启用数据库查询优化
- 配置 Redis 缓存
- 优化静态文件服务

### 3. 数据库优化

- 定期执行 VACUUM
- 监控慢查询
- 适当创建索引

## 安全建议

1. 定期更新 Docker 镜像
2. 使用强密码和密钥
3. 启用防火墙
4. 定期备份数据
5. 监控系统日志
6. 限制管理员账户数量

## 联系支持

如有问题，请查看日志文件或联系技术支持。
