# 🌊 AquaGuard AI

해양생태계 관측 자료를 업로드하고 표준 컬럼으로 정리한 뒤, 생물종·해역·좌표 현황을 확인하는 Streamlit 웹 앱입니다.

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 포함 기능
- CSV 및 XLSX 업로드
- UTF-8 / CP949 / EUC-KR CSV 인코딩 읽기 시도
- 표준 컬럼 자동 인식 및 수동 매핑
- 중복 행 제거 및 데이터 통합
- 등록 데이터 수, 생물종 수, 해역 수, 좌표 보유 행 KPI
- 생물종/해역별 관측 기록 그래프 및 좌표 지도
- 분석 데이터 CSV 다운로드

## 데이터 관련 주의
이 버전은 **기초 데이터 등록·시각화 프로토타입**입니다. 실제 양식장 위험도를 예측하거나 생태학적 인과관계를 판정하지 않습니다. 위험도 모델을 구현하려면 검증된 피해 사례, 관측 시점·위치, 환경 변수, 양식장 위치 등의 자료와 별도 검증이 필요합니다. 업로드 데이터의 품질과 단위도 사용자가 확인해야 합니다.

## Streamlit Community Cloud 배포
1. 이 프로젝트를 GitHub 저장소에 업로드합니다.
2. Streamlit Community Cloud에서 GitHub 계정을 연결합니다.
3. `New app`에서 저장소와 브랜치를 선택합니다.
4. Main file path를 `app.py`로 지정해 배포합니다.
