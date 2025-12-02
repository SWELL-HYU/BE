"""
이미지 검증 관련 유틸리티 함수.
"""

from __future__ import annotations

from io import BytesIO

import mediapipe as mp
import numpy as np
from PIL import Image

from app.core.exceptions import InvalidPersonImageError

# MediaPipe Pose 초기화 (모듈 레벨에서 한 번만 초기화)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
)


def validate_person_in_image(image_bytes: bytes) -> None:
    """
    이미지에 사람이 포함되어 있는지 MediaPipe Pose를 사용하여 검증합니다.
    
    검증 기준:
    - 코(NOSE) 키포인트 visibility >= 0.5
    - 발목(LEFT_ANKLE 또는 RIGHT_ANKLE) 중 하나 이상 visibility >= 0.5
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        
    Raises:
        InvalidPersonImageError: 사람이 포함되어 있지 않거나 포즈가 적절하지 않은 경우
    """
    try:
        # 이미지 로드 및 RGB 변환
        image = Image.open(BytesIO(image_bytes))
        image_rgb = image.convert("RGB")
        
        # PIL Image를 numpy array로 변환 (MediaPipe는 numpy array를 기대함)
        image_array = np.array(image_rgb)
        
        # MediaPipe Pose 처리
        results = pose.process(image_array)
        
        # 포즈 랜드마크가 감지되지 않은 경우
        if not results.pose_landmarks:
            raise InvalidPersonImageError()
        
        landmarks = results.pose_landmarks.landmark
        
        # 코(NOSE) 키포인트 확인
        nose = landmarks[mp_pose.PoseLandmark.NOSE]
        if nose.visibility < 0.5:
            raise InvalidPersonImageError()
        
        # 발목 키포인트 확인 (LEFT_ANKLE 또는 RIGHT_ANKLE 중 하나 이상)
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        if left_ankle.visibility < 0.5 and right_ankle.visibility < 0.5:
            raise InvalidPersonImageError()
        
        # 검증 통과
        return None
        
    except InvalidPersonImageError:
        # InvalidPersonImageError는 그대로 재발생
        raise
    except Exception as e:
        # 기타 예외(이미지 로드 실패 등)도 InvalidPersonImageError로 변환
        raise InvalidPersonImageError() from e

