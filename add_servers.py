import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.sfpr.models import Server

# 服务器列表
servers = [
    "艾欧尼亚", "祖安", "诺克萨斯", "班德尔城", "皮尔特沃夫", 
    "战争学院", "巨神峰", "雷瑟守备", "裁决之地", "黑色玫瑰", 
    "暗影岛", "钢铁烈阳", "水晶之痕", "均衡教派", "影流", 
    "守望之海", "征服之海", "卡拉曼达", "皮城警备", "比尔吉沃特", 
    "德玛西亚", "弗雷尔卓德", "无畏先锋", "恕瑞玛", "扭曲丛林", 
    "巨龙之巢", "教育网专区", "男爵领域", "峡谷之巅", "体验服"
]

# 批量创建服务器
for server_name in servers:
    Server.objects.create(name=server_name, region="中国")
    print(f"已创建服务器: {server_name}")

print(f"总共创建了 {len(servers)} 个服务器") 