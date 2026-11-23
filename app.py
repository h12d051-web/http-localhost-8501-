import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="AquaGuard AI", page_icon="🌊", layout="wide")

STANDARD_COLUMNS = {
    "채집일": ["채집일", "조사일", "관측일", "date", "sampling_date"],
    "위도": ["위도", "lat", "latitude"],
    "경도": ["경도", "lon", "lng", "longitude"],
    "해역": ["해역", "조사지역", "지역", "정점명", "site", "location"],
    "생물종": ["생물종", "종명", "국명", "species", "name"],
    "개체수": ["개체수", "관찰개체수", "수량", "count", "abundance"],
    "수온": ["수온", "표층수온", "water_temperature", "temperature"],
    "염분": ["염분", "salinity"],
}

def read_table(uploaded):
    name = uploaded.name.lower()
    raw = uploaded.getvalue()
    if name.endswith(".csv"):
        for enc in ("utf-8-sig", "cp949", "euc-kr"):
            try:
                return pd.read_csv(BytesIO(raw), encoding=enc)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(BytesIO(raw))
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(raw))
    raise ValueError("CSV 또는 XLSX 파일만 지원합니다.")

def guess_mapping(columns):
    result = {}
    normalized = {str(c).strip().lower(): c for c in columns}
    for standard, aliases in STANDARD_COLUMNS.items():
        match = None
        for alias in aliases:
            if alias.lower() in normalized:
                match = normalized[alias.lower()]
                break
        result[standard] = match
    return result

def make_template():
    return pd.DataFrame(columns=list(STANDARD_COLUMNS.keys())).to_csv(index=False).encode("utf-8-sig")

st.title("🌊 AquaGuard AI")
st.caption("해양생태계 변화 데이터를 정리하고 양식장 주변의 관측 현황을 살펴보는 데이터 분석 도구")

with st.sidebar:
    st.header("프로젝트 안내")
    st.write("공공기관 등에서 확보한 해양 생물·환경 관측 자료를 업로드해 분석합니다.")
    st.info("현재 버전은 데이터 등록과 기초 현황 분석 단계입니다. 실제 위험도 예측 모델은 검증된 학습 데이터가 확보된 뒤 추가해야 합니다.")
    st.download_button("빈 CSV 템플릿 다운로드", make_template(), "aquaguard_template.csv", "text/csv")

if "dataset" not in st.session_state:
    st.session_state.dataset = pd.DataFrame(columns=STANDARD_COLUMNS.keys())

st.subheader("1. 데이터 업로드")
uploads = st.file_uploader("CSV 또는 XLSX 파일을 선택하세요", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

if uploads:
    for uploaded in uploads:
        try:
            source = read_table(uploaded)
            st.markdown(f"**파일:** `{uploaded.name}` · {len(source):,}행 × {len(source.columns):,}열")
            st.dataframe(source.head(8), use_container_width=True)
            mapping_guess = guess_mapping(source.columns)
            st.markdown("**표준 컬럼 연결**")
            options = ["(연결 안 함)"] + [str(c) for c in source.columns]
            mapping = {}
            cols = st.columns(4)
            for i, (standard, guessed) in enumerate(mapping_guess.items()):
                default = options.index(str(guessed)) if guessed is not None and str(guessed) in options else 0
                with cols[i % 4]:
                    selected = st.selectbox(
                        standard, options, index=default,
                        key=f"{uploaded.name}_{standard}"
                    )
                mapping[standard] = None if selected == "(연결 안 함)" else selected

            if st.button(f"「{uploaded.name}」 매핑 확정 및 등록", key=f"register_{uploaded.name}"):
                selected_cols = {src: std for std, src in mapping.items() if src is not None}
                if not selected_cols:
                    st.error("최소 한 개 이상의 컬럼을 연결해 주세요.")
                else:
                    cleaned = source[list(selected_cols.keys())].rename(columns=selected_cols)
                    for col in STANDARD_COLUMNS:
                        if col not in cleaned.columns:
                            cleaned[col] = pd.NA
                    cleaned = cleaned[list(STANDARD_COLUMNS.keys())]
                    before = len(cleaned)
                    cleaned = cleaned.drop_duplicates()
                    st.session_state.dataset = pd.concat(
                        [st.session_state.dataset, cleaned], ignore_index=True
                    ).drop_duplicates().reset_index(drop=True)
                    st.success(f"등록 완료: 파일 내 중복 {before-len(cleaned):,}행 제거")
        except Exception as e:
            st.error(f"파일을 읽지 못했습니다: {e}")

df = st.session_state.dataset.copy()
st.divider()
st.subheader("2. 메인 대시보드")
a, b, c, d = st.columns(4)
a.metric("등록 데이터", f"{len(df):,}행")
b.metric("관측 생물종", f"{df['생물종'].dropna().nunique():,}종" if len(df) else "0종")
c.metric("조사 해역", f"{df['해역'].dropna().nunique():,}곳" if len(df) else "0곳")
d.metric("좌표 보유 행", f"{df[['위도','경도']].dropna().shape[0]:,}행" if len(df) else "0행")

if df.empty:
    st.info("아직 등록된 데이터가 없습니다. 왼쪽의 빈 CSV 템플릿을 내려받거나 관측 자료를 업로드해 주세요. 데이터가 없을 때 지표는 0으로 표시됩니다.")
else:
    left, right = st.columns(2)
    with left:
        species = df["생물종"].dropna().astype(str).value_counts().head(10)
        if not species.empty:
            st.markdown("**관측 생물종 상위 10개**")
            st.plotly_chart(px.bar(species, labels={"index":"생물종", "value":"관측 행 수"}, title="생물종별 관측 기록"), use_container_width=True)
    with right:
        areas = df["해역"].dropna().astype(str).value_counts().head(10)
        if not areas.empty:
            st.markdown("**해역별 관측 기록**")
            st.plotly_chart(px.bar(areas, title="해역별 관측 기록", labels={"index":"해역", "value":"관측 행 수"}), use_container_width=True)

    if {"위도", "경도"}.issubset(df.columns):
        coords = df.copy()
        coords["위도"] = pd.to_numeric(coords["위도"], errors="coerce")
        coords["경도"] = pd.to_numeric(coords["경도"], errors="coerce")
        coords = coords.dropna(subset=["위도", "경도"])
        if not coords.empty:
            st.markdown("**관측 위치 분포**")
            st.map(coords.rename(columns={"위도":"lat", "경도":"lon"}))

st.divider()
st.subheader("3. 등록 데이터 확인 및 내보내기")
st.dataframe(df, use_container_width=True, height=300)
if not df.empty:
    st.download_button(
        "분석 데이터 CSV 다운로드",
        df.to_csv(index=False).encode("utf-8-sig"),
        "aquaguard_analysis_dataset.csv",
        "text/csv"
    )
