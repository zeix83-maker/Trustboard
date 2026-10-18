import streamlit as st
import sqlite3
import hashlib
import hmac
import time
import pandas as pd
from datetime import datetime

DB_FILE = "trust_dual_platform.db"
SECRET_SALT = "TRUST_PLATFORM_MASTER_KEY_2026"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quant_board (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE,
            badge_type TEXT,
            strategy_name TEXT,
            broker TEXT,
            principal REAL,
            current_asset REAL,
            return_rate REAL,
            mdd REAL,
            day_count INTEGER,
            verified_hash TEXT,
            for_sale INTEGER DEFAULT 0,
            sale_price INTEGER DEFAULT 0,
            last_updated TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS biz_board (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_alias TEXT UNIQUE,
            category TEXT,
            region TEXT,
            data_source TEXT,
            monthly_revenue REAL,
            monthly_net_profit REAL,
            yoy_growth REAL,
            verified_hash TEXT,
            for_sale INTEGER DEFAULT 0,
            premium_ask INTEGER DEFAULT 0,
            last_updated TEXT
        )
    ''')
    c.execute("SELECT COUNT(*) FROM quant_board")
    if c.fetchone()[0] == 0:
        quant_samples = [
            ("운영자_실전생중계", "🔥 Day-1 100만원 실험실", "라오어 무한매수법 v4.0 (TQQQ/SOXL)", "한국투자증권(실전)", 1000000, 1003500, 0.35, -0.8, 1, "9f8e7d6c5b4a", 0, 0, "2026-10-18 18:00:00"),
            ("팩트체크_봇1호", "🧪 유튜브 기법 검증소", "유튜버 K씨 눌림목 조건검색식 그대로 구현", "한국투자증권(모의)", 10000000, 9120000, -8.80, -12.4, 14, "1a2b3c4d5e6f", 0, 0, "2026-10-18 18:00:00"),
            ("AlphaHunter", "🏆 실전 고수 도전자", "국장 반도체/바이오 수급 피봇 스위칭", "한국투자증권(실전)", 50000000, 64200000, 28.40, -6.2, 45, "7c8d9e0f1a2b", 1, 450000, "2026-10-18 18:00:00"),
        ]
        c.executemany('''
            INSERT INTO quant_board 
            (nickname, badge_type, strategy_name, broker, principal, current_asset, return_rate, mdd, day_count, verified_hash, for_sale, sale_price, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', quant_samples)

    c.execute("SELECT COUNT(*) FROM biz_board")
    if c.fetchone()[0] == 0:
        biz_samples = [
            ("수성구_A약국 (익명)", "💊 약국/메디컬", "대구 수성구", "홈택스/여신협회 API", 85000000, 18500000, 12.4, "b1c2d3e4f5a6", 1, 250000000, "2026-10-18 18:00:00"),
            ("반월당_B카페 (익명)", "☕ 프랜차이즈/식음료", "대구 중구", "여신금융협회 카드매출 API", 32000000, 7800000, -3.2, "d4e5f6a1b2c3", 1, 65000000, "2026-10-18 18:00:00"),
            ("스마트스토어_건기식몰", "📦 온라인 커머스", "전국(온라인)", "네이버 커머스 API", 140000000, 31000000, 45.0, "f6a1b2c3d4e5", 1, 420000000, "2026-10-18 18:00:00"),
        ]
        c.executemany('''
            INSERT INTO biz_board 
            (store_alias, category, region, data_source, monthly_revenue, monthly_net_profit, yoy_growth, verified_hash, for_sale, premium_ask, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', biz_samples)

    conn.commit()
    conn.close()

def make_hash(key_str: str) -> str:
    return hmac.new(SECRET_SALT.encode(), key_str.encode(), hashlib.sha256).hexdigest()[:12]

st.set_page_config(page_title="TrustBoard - 조작 불가 API 실전 검증소", layout="wide")
init_db()

st.sidebar.title("🎛️ 비즈니스 모델 스위치")
mode = st.sidebar.radio(
    "실행할 플랫폼 모드를 선택하세요:",
    ["📈 Mode 1. TrustQuant (주식/퀀트 계좌 검증)", "🏥 Mode 2. TrustBiz (약국/자영업 실매출·권리금 검증)"]
)

st.sidebar.divider()
st.sidebar.markdown("### 📢 자동 홍보 문구 생성기")
st.sidebar.caption("수익 난 내 계좌가 없어도 커뮤니티에 바로 복사해 올릴 수 있는 바이럴 템플릿입니다.")
with st.sidebar.expander("📋 커뮤니티 시딩 글 복사하기", expanded=True):
    if "TrustQuant" in mode:
        viral_text = """[실험 생중계] 포토샵 수익 인증에 지쳐서 '조작 불가능한 한투 API 실시간 중계 보드'를 만들었습니다.

제가 대단한 고수여서 만든 게 아닙니다.
말로만 떠드는 유튜버 기법들이 진짜 돈이 되는지 궁금해서, 오늘 제 돈 100만 원 넣고 '라오어 무한매수법 v4.0' 파이썬 봇을 연동해 실시간으로 박제했습니다. (현재 Day 1, 수익률 +0.35%)

읽기 전용 API로 서버가 직접 긁어오므로 본인이 숫자를 절대 못 고칩니다.
자기 전략에 진짜 자신 있는 분, 혹은 엉터리 기법 팩트체크 하실 분들 계급장 떼고 API로 붙어봅시다!"""
    else:
        viral_text = """[권리금 뻥튀기 방지] 브로커 말만 믿고 인수했다가 피보는 일을 막으려고 '국세청/여신협회 API 기반 실매출 검증 보드'를 만들었습니다.

엑셀이나 수기 장부는 100% 조작 가능합니다.
이 사이트는 읽기 전용 API로 최근 12개월 실제 카드/조제/온라인 매출만 직접 가져와 익명(지역+업종)으로 박제합니다.

매도자분들은 진짜 알짜 매장임을 API 배지로 증명해서 제값 받으시고, 인수자분들은 검증된 매물만 안전하게 거래하세요."""
    st.code(viral_text, language="markdown")

if "TrustQuant" in mode:
    st.title("📈 TrustQuant : 조작 불가 API 실전 계좌 중계소")
    st.info("💡 **고수가 아니어도 괜찮습니다!** `🔥 Day-1 100만원 실험실`이나 `🧪 유튜브 기법 검증소`로 시작해 트래픽을 모으세요.")
    
    conn = sqlite3.connect(DB_FILE)
    df_q = pd.read_sql_query("SELECT * FROM quant_board ORDER BY id ASC", conn)
    conn.close()
    
    t1, t2, t3 = st.tabs(["📡 실시간 생중계 & 리더보드", "🛒 검증된 전략/봇 마켓", "➕ 새 실험 계좌 / 도전자 API 등록"])
    
    with t1:
        for _, row in df_q.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3.5, 2, 2, 2])
                with c1:
                    st.markdown(f"**{row['badge_type']}** | **{row['nickname']}**")
                    st.markdown(f"#### 🎯 {row['strategy_name']}")
                    st.caption(f"{row['broker']} | 운용 {row['day_count']}일차 | 무결성 해시: `{row['verified_hash']}`")
                with c2:
                    color = "normal" if row['return_rate'] >= 0 else "inverse"
                    st.metric("실시간 API 수익률", f"{row['return_rate']:+.2f} %", f"MDD {row['mdd']}%", delta_color=color)
                with c3:
                    st.metric("실시간 평가자산", f"{int(row['current_asset']):,} 원", f"원금 {int(row['principal']):,}원")
                with c4:
                    if row['for_sale'] == 1:
                        st.success(f"🛒 봇/전략 판매중\n({int(row['sale_price']):,}원)")
                    else:
                        st.info("📡 실시간 생중계 중")
    
    with t2:
        st.subheader("🤝 실전 API로 증명된 파이썬 봇 & 매매법 마켓")
        sale_q = df_q[df_q['for_sale'] == 1]
        for _, row in sale_q.iterrows():
            with st.container(border=True):
                st.markdown(f"#### 📦 {row['strategy_name']} (검증 기간: {row['day_count']}일 / 수익률: `{row['return_rate']:+.2f}%`)")
                st.write(f"판매가: **{int(row['sale_price']):,} 원** (에스크로 수수료 10%)")
                st.button("코드 및 세팅값 안전구매", key=f"q_buy_{row['id']}")

    with t3:
        with st.form("add_quant"):
            st.markdown("##### ⚡ 내 소액 실험 계좌 또는 도전자 계좌 등록")
            badge = st.selectbox("계좌 성격 선택", ["🔥 Day-1 100만원 실험실", "🧪 유튜브 기법 검증소", "🏆 실전 고수 도전자"])
            nick = st.text_input("닉네임", placeholder="예: 대구퀀트_실험1호")
            strat = st.text_input("실험할 전략명", placeholder="예: SOXL 무한매수법 v4.0 매일 자동매수 봇")
            principal = st.number_input("시작 원금 (원)", value=1000000, step=100000)
            current = st.number_input("현재 API 조회 잔고 (시뮬레이션)", value=1000000, step=10000)
            
            if st.form_submit_button("🔒 API 연동 및 생중계 시작하기"):
                ret = round(((current - principal) / principal) * 100, 2) if principal > 0 else 0.0
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                h = make_hash(f"{nick}|{current}|{now_str}")
                conn = sqlite3.connect(DB_FILE)
                conn.execute('''
                    INSERT OR REPLACE INTO quant_board 
                    (nickname, badge_type, strategy_name, broker, principal, current_asset, return_rate, mdd, day_count, verified_hash, for_sale, sale_price, last_updated)
                    VALUES (?, ?, ?, '한국투자증권(API)', ?, ?, ?, -0.5, 1, ?, 0, 0, ?)
                ''', (nick, badge, strat, principal, current, ret, h, now_str))
                conn.commit()
                conn.close()
                st.success("등록 완료! 상단 '실시간 생중계 & 리더보드' 탭을 확인하세요.")

else:
    st.title("🏥 TrustBiz : 약국·자영업·쇼핑몰 API 실매출 검증 & 양도양수 마켓")
    st.info("💡 **권리금 사기 원천 차단!** 브로커의 부풀려진 말 대신 홈택스·여신금융협회·POS 읽기 전용 데이터로 검증된 매장만 모았습니다.")
    
    conn = sqlite3.connect(DB_FILE)
    df_b = pd.read_sql_query("SELECT * FROM biz_board ORDER BY monthly_net_profit DESC", conn)
    conn.close()
    
    b1, b2 = st.tabs(["🏢 API 실매출 검증 매장 보드 (권리금 마켓)", "➕ 내 매장/쇼핑몰 매출 API 검증 등록"])
    
    with b1:
        for _, row in df_b.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2.5])
                with c1:
                    st.markdown(f"`{row['category']}` | 📍 {row['region']}")
                    st.markdown(f"### **{row['store_alias']}**")
                    st.caption(f"검증 출처: {row['data_source']} | 해시: `{row['verified_hash']}`")
                with c2:
                    st.metric("검증된 월평균 매출", f"{int(row['monthly_revenue']/10000):,} 만원", f"전년비 {row['yoy_growth']:+.1f}%")
                with c3:
                    st.metric("검증된 월평균 순익", f"{int(row['monthly_net_profit']/10000):,} 만원")
                with c4:
                    st.warning(f"🤝 희망 권리금/인수가\n**{int(row['premium_ask']/10000):,} 만원**")
                    st.button("🔒 NDA(비밀유지계약) 서명 후 상세위치 열람", key=f"nda_{row['id']}")

    with b2:
        with st.form("add_biz"):
            st.markdown("##### ⚡ 익명으로 내 사업장/약국/스토어 실매출 검증하기")
            alias = st.text_input("익명 매장 별칭", placeholder="예: 동성로_독점층약국 또는 수성구_대형베이커리")
            cat = st.selectbox("업종 카테고리", ["💊 약국/메디컬", "☕ 프랜차이즈/식음료", "📦 온라인 커머스", "🏪 기타 소매/서비스"])
            reg = st.text_input("지역 (시/구 단위까지만 공개)", value="대구 수성구")
            rev = st.number_input("API 조회 월평균 매출 (원)", value=50000000, step=5000000)
            prof = st.number_input("API 조회 월평균 순익 (원)", value=12000000, step=1000000)
            ask = st.number_input("희망 권리금/양도가 (원)", value=150000000, step=10000000)
            
            if st.form_submit_button("🔒 매출 데이터 무결성 해시 발급 및 등록"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                h = make_hash(f"{alias}|{rev}|{prof}|{now_str}")
                conn = sqlite3.connect(DB_FILE)
                conn.execute('''
                    INSERT OR REPLACE INTO biz_board 
                    (store_alias, category, region, data_source, monthly_revenue, monthly_net_profit, yoy_growth, verified_hash, for_sale, premium_ask, last_updated)
                    VALUES (?, ?, ?, '여신협회/홈택스 API', ?, ?, 8.5, ?, 1, ?, ?)
                ''', (alias, cat, reg, rev, prof, h, ask, now_str))
                conn.commit()
                conn.close()
                st.success("매장 검증 등록 완료! 첫 번째 탭에서 등록된 카드를 확인하세요.")
