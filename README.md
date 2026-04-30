# lab1

run.sh - 启动脚本
#!/bin/bash

echo "=== DevOps Metrics Platform ==="

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from db import init_db; init_db()"

# 采集一次初始数据
python collector.py

# 启动服务
echo "Starting FastAPI server at http://localhost:8000"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload


运行方法：
# 1. 创建项目目录并保存所有文件
mkdir devops_metrics && cd devops_metrics

# 2. 给脚本执行权限
chmod +x run.sh

# 3. 运行
./run.sh

# 或者手动执行
python -c "from db import init_db; init_db()"
python collector.py  # 采集模拟数据
python app.py        # 启动服务
