#!/bin/bash

# CSList 部署脚本
# 使用方法: ./deploy.sh [environment]
# environment: dev (默认) 或 prod

set -e

ENVIRONMENT=${1:-dev}
PROJECT_NAME="cslist"

echo "=== CSList 部署脚本 ==="
echo "环境: $ENVIRONMENT"
echo "项目名称: $PROJECT_NAME"

# 检查必要的文件
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: 找不到 docker-compose.yml 文件"
    exit 1
fi

if [ "$ENVIRONMENT" = "prod" ] && [ ! -f "docker-compose.prod.yml" ]; then
    echo "错误: 找不到 docker-compose.prod.yml 文件"
    exit 1
fi

# 停止现有容器
echo "=== 停止现有容器 ==="
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml down
else
    docker-compose down
fi

# 创建网络（如果不存在）
echo "=== 创建 Docker 网络 ==="
docker network create ${PROJECT_NAME}_network 2>/dev/null || echo "网络已存在"

# 创建卷（如果不存在）
echo "=== 创建 Docker 卷 ==="
docker volume create ${PROJECT_NAME}_static_volume 2>/dev/null || echo "静态文件卷已存在"
docker volume create ${PROJECT_NAME}_media_volume 2>/dev/null || echo "媒体文件卷已存在"

# 构建镜像
echo "=== 构建 Docker 镜像 ==="
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml build --no-cache
else
    docker-compose build --no-cache
fi

# 启动服务
echo "=== 启动服务 ==="
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

# 等待服务启动
echo "=== 等待服务启动 ==="
sleep 10

# 检查服务状态
echo "=== 检查服务状态 ==="
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose ps
fi

# 显示日志
echo "=== 显示最近的日志 ==="
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml logs --tail=50
else
    docker-compose logs --tail=50
fi

echo "=== 部署完成 ==="
echo "访问地址:"
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "  - https://cslist.ineed.asia"
    echo "  - https://cslist.ineed.asia/admin/"
else
    echo "  - http://localhost:8000"
    echo "  - http://localhost:8000/admin/"
fi

echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f [service_name]"
echo "  进入容器: docker exec -it ${PROJECT_NAME}_web bash"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart" 