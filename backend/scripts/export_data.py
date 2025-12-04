"""
데이터 내보내기 스크립트 (export_data.py)

이 스크립트는 데이터베이스에 저장된 사용자 상호작용(UserCoordiInteraction)과
시청 로그(UserCoordiViewLog) 데이터를 CSV 파일로 내보냅니다.

생성되는 파일:
1. user_outfit_interaction.csv: 사용자-코디 상호작용 데이터 (interaction: 'like', 'preference', 'skip')
2. user_outfit_view_time.csv: 사용자-코디 시청 시간 데이터 (view_time_seconds: 초 단위)
"""
import sys
import os
import csv

# Add backend directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.user_coordi_interaction import UserCoordiInteraction
from app.models.user_coordi_view_log import UserCoordiViewLog

def export_data():
    db = SessionLocal()
    try:
        print("Exporting data to CSV...")

        # 1. Export user_outfit_interaction.csv
        # interaction: 'like', 'preference', 'skip'
        interactions = db.execute(select(UserCoordiInteraction)).scalars().all()
        
        with open('user_outfit_interaction.csv', 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'outfit_id', 'interaction']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for interaction in interactions:
                writer.writerow({
                    'user_id': interaction.user_id,
                    'outfit_id': interaction.coordi_id,
                    'interaction': interaction.action_type
                })
        print(f"Exported {len(interactions)} rows to user_outfit_interaction.csv")

        # 2. Export user_outfit_view_time.csv
        view_logs = db.execute(select(UserCoordiViewLog)).scalars().all()
        
        with open('user_outfit_view_time.csv', 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'outfit_id', 'view_time_seconds']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in view_logs:
                writer.writerow({
                    'user_id': log.user_id,
                    'outfit_id': log.coordi_id,
                    'view_time_seconds': log.duration_seconds
                })
        print(f"Exported {len(view_logs)} rows to user_outfit_view_time.csv")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_data()
