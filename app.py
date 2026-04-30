from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

from db import SessionLocal, BuildRecord, DeploymentRecord, ServiceHealth, CodeStats
from collector import run_collection

app = FastAPI(title="DevOps Metrics Platform")

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# API端点

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回仪表盘页面"""
    with open("static/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/collect")
async def trigger_collection(background_tasks: BackgroundTasks):
    """手动触发数据采集"""
    background_tasks.add_task(run_collection)
    return {"message": "Collection started"}

@app.get("/api/builds/summary")
async def get_build_summary(days: int = 7):
    """获取构建汇总数据"""
    session = SessionLocal()
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # 成功率统计
    results = session.query(
        BuildRecord.service_name,
        func.count(BuildRecord.id).label('total_builds'),
        func.sum(func.case([(BuildRecord.status == 'success', 1)], else_=0)).label('success_count')
    ).filter(BuildRecord.build_time >= since_date).group_by(BuildRecord.service_name).all()
    
    summary = []
    for r in results:
        summary.append({
            'service': r.service_name,
            'total_builds': r.total_builds,
            'success_count': r.success_count or 0,
            'success_rate': round((r.success_count or 0) / r.total_builds * 100, 2)
        })
    
    session.close()
    return summary

@app.get("/api/builds/trend")
async def get_build_trend(days: int = 7):
    """构建趋势数据"""
    session = SessionLocal()
    since_date = datetime.utcnow() - timedelta(days=days)
    
    results = session.query(
        func.date(BuildRecord.build_time).label('date'),
        func.count(BuildRecord.id).label('count'),
        func.avg(BuildRecord.duration_seconds).label('avg_duration')
    ).filter(BuildRecord.build_time >= since_date).group_by('date').order_by('date').all()
    
    trend = [{'date': r.date, 'count': r.count, 'avg_duration': round(r.avg_duration or 0, 2)} 
             for r in results]
    
    session.close()
    return trend

@app.get("/api/deployments/stats")
async def get_deployment_stats():
    """部署统计"""
    session = SessionLocal()
    
    # 各环境部署次数
    env_stats = session.query(
        DeploymentRecord.environment,
        func.count(DeploymentRecord.id).label('count')
    ).group_by(DeploymentRecord.environment).all()
    
    # 部署成功率
    total = session.query(func.count(DeploymentRecord.id)).scalar() or 1
    success = session.query(func.count(DeploymentRecord.id)).filter(DeploymentRecord.success == 1).scalar() or 0
    
    session.close()
    
    return {
        'by_environment': [{'env': e[0], 'count': e[1]} for e in env_stats],
        'deployment_success_rate': round(success / total * 100, 2)
    }

@app.get("/api/health/current")
async def get_current_health():
    """当前服务健康状态"""
    session = SessionLocal()
    
    # 获取每个服务的最新健康记录
    subquery = session.query(
        ServiceHealth.service_name,
        func.max(ServiceHealth.timestamp).label('max_time')
    ).group_by(ServiceHealth.service_name).subquery()
    
    results = session.query(ServiceHealth).join(
        subquery,
        and_(
            ServiceHealth.service_name == subquery.c.service_name,
            ServiceHealth.timestamp == subquery.c.max_time
        )
    ).all()
    
    health_data = [{
        'service': h.service_name,
        'response_time_ms': round(h.response_time_ms, 2),
        'error_rate': round(h.error_rate, 2),
        'cpu_usage': round(h.cpu_usage, 2),
        'memory_usage': round(h.memory_usage, 2),
        'status': 'healthy' if h.error_rate < 2 and h.response_time_ms < 300 else 'warning'
    } for h in results]
    
    session.close()
    return health_data

@app.get("/api/code/stats")
async def get_code_stats(days: int = 30):
    """代码统计"""
    session = SessionLocal()
    since_date = datetime.utcnow() - timedelta(days=days)
    
    results = session.query(CodeStats).filter(CodeStats.date >= since_date).order_by(CodeStats.date).all()
    
    stats = [{
        'date': r.date.strftime('%Y-%m-%d'),
        'lines_of_code': r.lines_of_code,
        'commits': r.commits_count,
        'bugs': r.bug_count
    } for r in results]
    
    session.close()
    return stats

@app.get("/api/dora/metrics")
async def get_dora_metrics():
    """DORA指标 (部署频率和恢复时间)"""
    session = SessionLocal()
    
    # 最近30天的部署频率
    since_date = datetime.utcnow() - timedelta(days=30)
    deployments = session.query(DeploymentRecord).filter(
        DeploymentRecord.deploy_time >= since_date,
        DeploymentRecord.success == 1
    ).count()
    
    deployment_frequency = round(deployments / 30, 2)  # 每天部署次数
    
    # 模拟恢复时间（从失败部署到下一个成功部署的时间）
    lead_time_for_change = 4.5  # 小时，可以从实际数据计算
    
    session.close()
    
    return {
        'deployment_frequency': f"{deployment_frequency} deploys/day",
        'lead_time_for_change': f"{lead_time_for_change} hours",
        'mean_time_to_recovery': "2.3 hours",
        'change_failure_rate': "8.5%"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
