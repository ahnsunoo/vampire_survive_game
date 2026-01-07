import streamlit as st
import json
import os
import pandas as pd

# --- 경로 설정 (게임 코드와 동일하게) ---
DATA_PATH = r"C:\Users\KDT38\Desktop\project\game_data.json"
RANK_CSV = r"C:\Users\KDT38\Desktop\project\ranking_history.csv"

st.title("🏆 인게임 점수 연동 랭킹")

if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding='utf-8') as f:
        data = json.load(f)
    
    st.subheader(f"최근 게임 점수: {data['last_score']}")
    
    if st.button("내 점수 랭킹 등록"):
        new_row = pd.DataFrame([{"점수": data['last_score'], "골드": data['money']}])
        if os.path.exists(RANK_CSV):
            df = pd.read_csv(RANK_CSV)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
        df.sort_values("점수", ascending=False).to_csv(RANK_CSV, index=False, encoding='utf-8-sig')
        st.success("랭킹이 업데이트되었습니다!")

    if os.path.exists(RANK_CSV):
        st.table(pd.read_csv(RANK_CSV).head(10))
else:
    st.error(f"데이터 파일을 찾을 수 없습니다. 경로 확인: {DATA_PATH}")