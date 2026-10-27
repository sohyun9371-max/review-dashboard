import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="주말 체험단 모아보기", page_icon="📍", layout="wide")
st.title("📍 주말 체험단 모아보기")
st.caption("수원 영통 출발 · 자동차 편도 60분 이내 · 주말 체험 가능")
path = Path(__file__).with_name("campaigns.json")
try:
    campaigns = json.loads(path.read_text(encoding="utf-8"))
except (OSError, ValueError):
    campaigns = []
df = pd.DataFrame(campaigns)
if not df.empty:
    required = {"title", "source", "url", "location", "weekend_status", "drive_minutes"}
    if not required.issubset(df.columns):
        st.error("공고 데이터 형식이 올바르지 않습니다.")
        st.stop()
    minutes = pd.to_numeric(df["drive_minutes"], errors="coerce")
    eligible = df[(df["weekend_status"] == "confirmed") & (minutes <= 60)]
else:
    eligible = pd.DataFrame()
a, b = st.columns(2)
a.metric("조건 확인된 공고", len(eligible))
b.metric("전체 수집 공고", len(df))
st.divider()
if eligible.empty:
    st.info("아직 조건을 검증한 실제 공고가 없습니다. 자동 수집과 경로 API 연결 전입니다.")
else:
    q = st.text_input("공고 검색")
    for _, r in eligible.iterrows():
        if q and q.lower() not in str(r["title"]).lower():
            continue
        with st.container(border=True):
            st.subheader(str(r["title"]))
            st.write(f'출처: {r["source"]} · 지역: {r["location"]} · 자동차 약 {r["drive_minutes"]}분')
            st.link_button("공고 원문 보기", str(r["url"]))
st.caption("주말 방문 가능 여부와 이동시간이 확인된 공고만 표시합니다. 제공금액 필터, 직접 등록, CSV 기능은 없습니다.")
