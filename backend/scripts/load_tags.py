"""
태그 데이터를 DB에 일괄 삽입하는 배치 스크립트.

사용법:
    python scripts/load_tags.py data/tags_sample.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.tag import Tag


def get_or_create_tag(
    db: SessionLocal,
    name: str,
) -> Tag:
    """
    태그가 존재하면 조회하고, 없으면 생성한다.
    
    Args:
        db: 데이터베이스 세션
        name: 태그 이름
        
    Returns:
        Tag 객체
    """
    # 이름으로 기존 태그 확인 (unique 제약)
    existing_tag = db.execute(
        select(Tag).where(Tag.name == name)
    ).scalar_one_or_none()
    
    if existing_tag:
        return existing_tag
    
    # 태그 생성 (tag_id는 자동 증가)
    tag = Tag(
        name=name,
    )
    
    db.add(tag)
    db.flush()  # tag_id를 DB에 확정
    
    return tag


def load_tags_from_json(json_file_path: str) -> None:
    """
    JSON 파일에서 태그 데이터를 읽어 DB에 삽입한다.
    
    Args:
        json_file_path: JSON 파일 경로
    """
    db = SessionLocal()
    
    try:
        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as f:
            tags_data = json.load(f)
        
        # 리스트가 아니면 단일 태그로 처리
        if not isinstance(tags_data, list):
            tags_data = [tags_data]
        
        # 태그 개수
        total_count = len(tags_data)
        success_count = 0
        error_count = 0
        skip_count = 0
        
        print(f"총 {total_count}개의 태그를 삽입합니다...\n")
        
        # 각 태그 삽입
        for idx, tag_data in enumerate(tags_data, 1):
            try:
                name = tag_data["name"]
                
                # 기존 태그 확인
                existing_tag = db.execute(
                    select(Tag).where(Tag.name == name)
                ).scalar_one_or_none()
                
                if existing_tag:
                    skip_count += 1
                    print(
                        f"[{idx}/{total_count}] ⊘ 태그 ID: {existing_tag.tag_id}, 이름: {name} (이미 존재)"
                    )
                    continue
                
                # 태그 생성 또는 조회
                tag = get_or_create_tag(
                    db=db,
                    name=name,
                )
                
                # 커밋
                db.commit()
                
                success_count += 1
                print(
                    f"[{idx}/{total_count}] ✓ 태그 ID: {tag.tag_id}, 이름: {tag.name}"
                )
                
            except Exception as e:
                db.rollback()
                error_count += 1
                name = tag_data.get("name", "알 수 없음")
                print(f"[{idx}/{total_count}] ✗ 태그 이름 '{name}': {str(e)}")
        
        # 결과 요약
        print(f"\n{'='*50}")
        print(f"완료: {success_count}개 성공, {skip_count}개 스킵, {error_count}개 실패")
        print(f"{'='*50}")
        
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다: {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파싱 실패: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"오류: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python scripts/load_tags.py <json_file_path>")
        print("예시: python scripts/load_tags.py data/tags_sample.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    load_tags_from_json(json_file_path)


if __name__ == "__main__":
    main()

