import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import os

from app.services.training_service import run_night_training

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler 인스턴스 생성
scheduler = BackgroundScheduler()

def train_night_model_job():
    """
    매일 새벽 실행되는 Night Model 학습 작업.
    1. Night Model 재학습 (User & Item Embedding Update)
    2. 학습 결과로 DB의 'night_v1' 데이터 갱신
    3. 'day_v1' 데이터를 'night_v1' 값으로 초기화 (Reset)
    """
    logger.info("[Scheduler] Starting Night Model Training Job...")
    
    try:
        run_night_training()
        logger.info("[Scheduler] Night Model Training Job Completed Successfully.")
    except Exception as e:
        logger.error(f"[Scheduler] Night Model Training Job Failed: {e}")


def start_scheduler():
    """
    스케줄러 시작 함수. main.py에서 호출됨.
    """
    if not scheduler.running:
        # 매일 새벽 3시에 실행
        trigger = CronTrigger(hour=3, minute=0)
    
        scheduler.add_job(
            train_night_model_job,
            trigger=trigger,
            id="train_night_model",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("[Scheduler] Background Scheduler Started. Night Training scheduled at 03:00 AM.")

def shutdown_scheduler():
    """
    스케줄러 종료 함수.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[Scheduler] Background Scheduler Shutdown.")
