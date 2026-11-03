import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="네오바이오텍 기업분석", layout="wide")

st.title("네오바이오텍 기업분석 대시보드")
st.caption("DART 공시자료 기반 재무분석")

st.subheader("기업 개요")
st.write("기업명: 네오바이오텍")
st.write("분석 자료: DART 사업보고서 및 분기·반기보고서")

file = "dart_financial_data.csv"

if os.path.exists(file):
    df = pd.read_csv(file)
    st.subheader("재무 데이터")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("아직 재무 데이터가 없습니다. DART 자료 수집을 먼저 실행해 주세요.")

st.subheader("재무분석 항목")
st.write("- 매출액")
st.write("- 영업이익")
st.write("- 당기순이익")
st.write("- 자산 및 부채")
st.write("- 재무비율")
