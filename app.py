import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="주말 체험단 모아보기", page_icon="📍", layout="wide")
st.title("📍 주말 체험단 모아보기")
st.caption("수원 영통 출발 · 주말 방문 가능 · 자동차 60분 이내")
st.warning("자동 수집 후보는 실제 공고지만, 주말 체험 및 자동차 60분 이내 여부는 별도 확인이 필요합니다.")
def load(name):
    try:
        data=json.loads(Path(__file__).with_name(name).read_text(encoding="utf-8"))
        return data if isinstance(data,list) else []
    except (OSError,ValueError):
        return []
verified=load("campaigns.json")
candidates=load("candidates.json")
a,b=st.columns(2)
a.metric("조건 검증 완료",len(verified))
b.metric("수집된 확인 후보",len(candidates))
tab1,tab2=st.tabs(["조건 검증 완료","확인 필요 공고"])
with tab1:
    if not verified:
        st.info("주말 체험과 자동차 60분 이내 조건까지 검증된 공고는 아직 없습니다.")
    for item in verified:
        with st.container(border=True):
            st.subheader(item.get("title","제목 없음"))
            st.write(item.get("location",""))
            if item.get("url","").startswith("https://"):
                st.link_button("원문 보기",item["url"])
with tab2:
    st.caption("주말 가능 여부나 운전시간을 확인하지 않은 공고입니다. 조건에 맞는다고 보장하지 않습니다.")
    search=st.text_input("후보 검색")
    for item in candidates:
        if search and search.lower() not in (item.get("title","")+" "+item.get("location","")).lower():
            continue
        with st.container(border=True):
            st.subheader(item.get("title","제목 없음"))
            st.write("출처: "+item.get("source","모아알림")+" · "+item.get("location","지역 확인 필요"))
            st.caption("주말 방문: 미확인 · 차량 이동시간: 미확인")
            if item.get("url","").startswith("https://"):
                st.link_button("공고 확인",item["url"])
st.divider()
st.caption("수집 대상: 모아알림 우선. 리뷰노마드·리뷰티풀·인플렉서는 연동 검토 중. 제공금액·직접 등록·CSV 기능 없음.")
