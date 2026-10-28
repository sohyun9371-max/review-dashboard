import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="주말 체험단 모아보기", page_icon="📍", layout="wide")
st.title("📍 주말 체험단 모아보기")
st.caption("수원 영통 출발 · 주말 방문 가능 · 자동차 60분 이내")
st.warning("공고 원문 자동 점검 결과는 참고용입니다. 주말 방문·모집 중 여부와 차량 60분 이내 조건을 모두 검증한 공고만 첫 번째 탭에 표시합니다.")
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
    weekend_only=st.checkbox("주말 가능 문구 발견 공고만 보기",value=False)
    open_only=st.checkbox("마감 확인된 공고 제외",value=True)
    for item in candidates:
        if weekend_only and item.get("weekend_status")!="possible":
            continue
        if open_only and item.get("recruitment_status")=="expired":
            continue
        if search and search.lower() not in (item.get("title","")+" "+item.get("location","")).lower():
            continue
        with st.container(border=True):
            st.subheader(item.get("title","제목 없음"))
            st.write("출처: "+item.get("source","모아알림")+" · "+item.get("location","지역 확인 필요"))
            weekend={"possible":"가능 문구 발견(확정 아님)","no":"불가 문구 발견","unknown":"미확인"}.get(item.get("weekend_status"),"미확인")
            recruit={"possible":"마감일 기준 진행 가능성","expired":"마감일 경과","unknown":"미확인"}.get(item.get("recruitment_status"),"미확인")
            st.caption(f"주말: {weekend} · 모집: {recruit} · 차량 이동시간: 미확인")
            st.caption(item.get("verification_note","원문 확인 필요"))
            if item.get("url","").startswith("https://"):
                st.link_button("공고 확인",item["url"])
st.divider()
st.caption("수집 대상: 모아알림 우선. 리뷰노마드·리뷰티풀·인플렉서는 연동 검토 중. 제공금액·직접 등록·CSV 기능 없음.")
