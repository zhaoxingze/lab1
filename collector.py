import random
from datetime import datetime, timedelta
from db import SessionLocal, BuildRecord, DeploymentRecord, ServiceHealth, CodeStats

def collect_build_data():
    """模拟从Jenkins/GitLab CI采集构建数据"""
    services = ['user-service', 'order-service', 'payment-service', 'gateway']
    session = SessionLocal()
    
    for service in services:
        record = BuildRecord(
            service_name=service,
            duration_seconds=random.randint(30, 300),
            status=random.choice(['success', 'success', 'success', 'failed']),
            commit_hash=''.join(random.choices('abcdef0123456789', k=8))
        )
        session.add(record)
    
    session.commit()
    print(f"Added {len(services)} build records")
    session.close()

def collect_deployment_data():
    """模拟部署数据"""
    services = ['user-service', 'order-service', 'payment-service', 'gateway']
    envs = ['dev', 'staging', 'prod']
    session = SessionLocal()
    
    for service in services:
        for _ in range(random.randint(1, 3)):
            record = DeploymentRecord(
                service_name=service,
                deploy_duration=random.randint(10, 120),
                success=1 if random.random() > 0.1 else 0,  # 90%成功率
                environment=random.choice(envs)
            )
            session.add(record)
    
    session.commit()
    session.close()

def collect_health_metrics():
    """模拟服务健康指标"""
    services = ['user-service', 'order-service', 'payment-service', 'gateway']
    session = SessionLocal()
    
    for service in services:
        record = ServiceHealth(
            service_name=service,
            response_time_ms=random.uniform(10, 500),
            error_rate=random.uniform(0, 5),
            cpu_usage=random.uniform(10, 80),
            memory_usage=random.uniform(20, 90)
        )
        session.add(record)
    
    session.commit()
    session.close()

def collect_code_stats():
    """模拟代码统计"""
    session = SessionLocal()
    record = CodeStats(
        lines_of_code=random.randint(5000, 15000),
        commits_count=random.randint(5, 50),
        bug_count=random.randint(0, 15)
    )
    session.add(record)
    session.commit()
    session.close()

def run_collection():
    """运行所有采集任务"""
    collect_build_data()
    collect_deployment_data()
    collect_health_metrics()
    collect_code_stats()
    print("Data collection completed")

if __name__ == "__main__":
    run_collection()
