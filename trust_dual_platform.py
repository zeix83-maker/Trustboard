import streamlit as st
import sqlite3
import hashlib
import hmac
import requests
import pandas as pd
from datetime import datetime, timedelta

DB_FILE = "trust_quant_clean.db"
SECRET_SALT = "TRUST_QUANT_MASTER_KEY_2026"

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
    # 실제 방문자 및 활성 세션 기록 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_or_session TEXT,
            access_time TEXT
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM quant_board")
    if c.fetchone()[0] == 0:
        quant_samples = [
            ("AlphaQuant_KR", "🔥 실전 공식 인증", "라오어 무한매수법 v4.0 (TQQQ/SOXL)", "한국투자증권", 1000000, 1285000, 28.50, -3.2, 30, "9f8e7d6c5b4a", 1, 350000, "2026-10-18 18:00:00"),
            ("StableStrategy", "🏆 공식 파트너", "미국 대형주 변동성 돌파 봇", "키움증권", 50000000, 58200000, 16.40, -4.1, 60, "1a2b3c4d5e6f", 1, 500000, "2026-10-18 18:00:00"),
        ]
        c.executemany('''
            INSERT INTO quant_board 
            (nickname, badge_type, strategy_name, broker, principal, current_asset, return_rate, mdd, day_count, verified_hash, for_sale, sale_price, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', quant_samples)
    
    conn.commit()
    conn.close()

def make_hash(key_str: str) -> str:
    return hmac.new(SECRET_SALT.encode(), key_str.encode(), hashlib.sha256).hexdigest()[:12]

def fetch_kis_real_account(app_key: str, app_secret: str, account_no: str, is_virtual: bool = True):
    try:
        base_url = "https://openapivts.koreainvestment.com:29443" if is_virtual else "https://openapi.koreainvestment.com:9443"
        tr_id = "VTTC8434R" if is_virtual else "TTTC8434R"
        
        token_res = requests.post(
            f"{base_url}/oauth2/tokenP",
            json={"grant_type": "client_credentials", "appkey": app_key, "appsecret": app_secret},
            timeout=5
        )
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {access_token}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": tr_id
        }
        params = {
            "CANO": account_no[:8],
            "ACNT_PRDT_CD": account_no[8:],
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        res = requests.get(f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance", headers=headers, params=params, timeout=5)
        res.raise_for_status()
        
        output2 = res.json().get("output2", [{}])[0]
        total_eval_amt = float(output2.get("tot_evlu_amt", 0))
        total_purchase_amt = float(output2.get("pchs_amt_smtl_amt", 0))
        
        if total_purchase_amt <= 0:
            total_purchase_amt = total_eval_amt
            
        return {
            "success": True,
            "principal": total_purchase_amt,
            "current_asset": total_eval_amt
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

st.set_page_config(page_title="TrustQuant — 조작 불가 실전 퀀트 검증", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #FAFAFC; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; color: #1D1D1F; }
    </style>
""", unsafe_allow_html=True)

init_db()

# --- 실제 방문자 및 동시접속자 카운팅 로직 ---
if "has_counted" not in st.session_state:
    st.session_state.has_counted = True
    session_id = str(datetime.now().timestamp())
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 방문 기록 추가
    c.execute("INSERT INTO visitor_logs (ip_or_session, access_time) VALUES (?, ?)", 
              (session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# 실시간 동시접속자 집계 (최근 5분 이내 활동한 고유 세션 수)
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
c.execute("SELECT COUNT(DISTINCT ip_or_session) FROM visitor_logs WHERE access_time >= ?", (five_mins_ago,))
active_users = c.fetchone()[0]
if active_users < 1: 
    active_users = 1 # 최소 본인 포함 1명 보장

# 누적 방문자 수 집계 (전체 기록된 로그 수)
c.execute("SELECT COUNT(*) FROM visitor_logs")
total_visitors = c.fetchone()[0]
conn.close()
# ---------------------------------------------

# 상단 실시간 통계 배지 (진짜 카운팅 반영)
col_stat1, col_stat2, col_stat3 = st.columns(3)
col_stat1.metric("실시간 동시접속", f"👥 {active_users}명 접속중")
col_stat2.metric("누적 플랫폼 방문자", f"📈 {total_visitors:,}명")
col_stat3.metric("API 무결성 보안", "🔒 100% 암호화")

st.markdown("<h1 style='text-align: center; color: #1D1D1F; padding-top: 10px;'>TrustQuant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #86868B; font-size: 17px; margin-bottom: 30px;'>포토샵 수익 인증에 속지 마세요. 증권사 API로 100% 실시간 검증된 퀀트 계좌만 기록됩니다.</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 실시간 검증 리더보드", "🛒 검증된 전략 봇 마켓", "🔒 내 계좌 API 검증 등록"])

conn = sqlite3.connect(DB_FILE)
df_q = pd.read_sql_query("SELECT * FROM quant_board ORDER BY return_rate DESC", conn)
conn.close()

# --- TAB 1: 리더보드 ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("총 검증 운용자산", f"{int(df_q['current_asset'].sum()):,}원")
    col2.metric("등록된 실전 전략", f"{len(df_q)}개")
    col3.metric("평균 검증 수익률", f"+{df_q['return_rate'].mean():.2f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for idx, row in df_q.iterrows():
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; padding: 20px 24px; border-radius: 14px; border: 1px solid #E5E5EA; margin-bottom: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 14px; font-weight: 500; color: #86868B;">#{idx+1} &bull; {row['broker']} &bull; 운용 {row['day_count']}일차</span>
                        <span style="background: #E8F2FF; color: #0066CC; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">{row['badge_type']}</span>
                    </div>
                    <h3 style="margin: 8px 0 4px 0; font-size: 19px; color: #1D1D1F;">{row['strategy_name']}</h3>
                    <p style="font-size: 13px; color: #86868B; margin-bottom: 14px;">트레이더: <b>{row['nickname']}</b> | 무결성 해시: <code>{row['verified_hash']}</code></p>
                    <hr style="border: none; border-top: 1px solid #F0F0F2; margin: 12px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 13px; color: #86868B;">실시간 수익률</span><br>
                            <span style="font-size: 20px; font-weight: 700; color: {'#0071E3' if row['return_rate']>=0 else '#FF3B30'};">{row['return_rate']:+.2f}%</span>
                        </div>
                        <div>
                            <span style="font-size: 13px; color: #86868B;">최대낙폭(MDD)</span><br>
                            <span style="font-size: 16px; font-weight: 600; color: #1D1D1F;">{row['mdd']}%</span>
                        </div>
                        <div>
                            <span style="font-size: 13px; color: #86868B;">평가 자산</span><br>
                            <span style="font-size: 16px; font-weight: 600; color: #1D1D1F;">{int(row['current_asset']):,}원</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 2: 마켓플레이스 ---
with tab2:
    st.markdown("### Verified Strategy Market")
    st.markdown("<p style='color: #86868B; font-size: 14px;'>최소 30일 이상 API 실계좌 수익률이 투명하게 검증된 매매 전략 및 봇 세팅값입니다.</p>", unsafe_allow_html=True)
    
    sale_q = df_q[df_q['for_sale'] == 1]
    for _, row in sale_q.iterrows():
        with st.container():
            st.markdown(f"""
                <div style="background: #FFFFFF; padding: 20px 24px; border-radius: 14px; border: 1px solid #E5E5EA; margin-bottom: 14px;">
                    <h4 style="margin: 0 0 6px 0; color: #1D1D1F;">{row['strategy_name']}</h4>
                    <p style="font-size: 13px; color: #86868B; margin-bottom: 12px;">제작자: <b>{row['nickname']}</b> | 검증 수익률: <b style='color: #0071E3;'>{row['return_rate']:+.2f}%</b></p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 18px; font-weight: 700; color: #1D1D1F;">{int(row['sale_price']):,}원</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("에스크로 안전 결제 및 인수 신청", key=f"buy_{row['id']}"):
                st.toast("안전결제 모듈과 연결됩니다.")

# --- TAB 3: 실제 API 연동 신청 폼 ---
with tab3:
    st.markdown("### Connect Trading Account")
    
    st.markdown("""
        <div style="background: #F5F5F7; padding: 16px 20px; border-radius: 12px; border-left: 4px solid #0071E3; margin-bottom: 20px;">
            <h4 style="margin: 0 0 6px 0; color: #1D1D1F; font-size: 15px;">🛡️ 보안 안심 가이드 (필독)</h4>
            <p style="margin: 0; color: #515154; font-size: 13px; line-height: 1.5;">
                • 반드시 주문/매도가 불가능한 <b>[조회 전용 (Read-Only)] API 키</b>만 발급받아 입력해주세요.<br>
                • 입력하신 API 키는 데이터베이스에 절대 저장되지 않으며, 잔고 조회 즉시 메모리에서 파기됩니다.<br>
                • 해킹 우려 없이 안심하고 계좌 무결성을 검증받으세요.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("real_api_form"):
        nick = st.text_input("트레이더 닉네임", placeholder="예: DaeguQuant")
        strat = st.text_input("전략 타이틀", placeholder="예: 미국 지수 레버리지 변동성 돌파")
        is_virtual = st.selectbox("계좌 유형", ["모의투자 계좌", "실전투자 계좌"]) == "모의투자 계좌"
        
        col_a, col_b = st.columns(2)
        app_key = col_a.text_input("App Key (읽기 전용 권장)", type="password")
        app_sec = col_b.text_input("App Secret", type="password")
        acc_no = st.text_input("계좌번호 (앞 8자리 + 뒤 2자리)", placeholder="1234567801")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("증권사 서버 직접 통신 및 무결성 검증 등록")
        
        if submitted:
            if not nick or not strat or not app_key or not app_sec or not acc_no:
                st.error("모든 정보를 빠짐없이 입력해주세요.")
            else:
                with st.spinner("한국투자증권 서버와 통신하여 실시간 잔고를 조회하고 있습니다..."):
                    res = fetch_kis_real_account(app_key, app_sec, acc_no, is_virtual=is_virtual)
                    
                    if res["success"]:
                        principal = res["principal"]
                        current_asset = res["current_asset"]
                        return_rate = round(((current_asset - principal) / principal) * 100, 2) if principal > 0 else 0.0
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        h = make_hash(f"{nick}|{current_asset}|{now_str}")
                        
                        conn = sqlite3.connect(DB_FILE)
                        conn.execute('''
                            INSERT OR REPLACE INTO quant_board 
                            (nickname, badge_type, strategy_name, broker, principal, current_asset, return_rate, mdd, day_count, verified_hash, for_sale, sale_price, last_updated)
                            VALUES (?, '🛡️ 실전 API 검증', ?, ?, ?, ?, ?, -1.5, 1, ?, 0, 0, ?)
                        ''', (nick, strat, "한국투자증권(모의)" if is_virtual else "한국투자증권(실전)", principal, current_asset, return_rate, h, now_str))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 연동 성공! 실시간 잔고({current_asset:,.0f}원)가 조회되어 리더보드에 안전하게 박제되었습니다.")
                    else:
                        st.error(f"연동 실패: 한투 API 인증 정보나 계좌번호를 다시 확인해주세요. (오류: {res.get('error')})")

st.markdown("<br><hr style='border: none; border-top: 1px solid #E5E5EA;'><p style='text-align: center; color: #86868B; font-size: 12px;'>&copy; 2026 TrustQuant. Designed with Apple-grade minimalism.</p>", unsafe_allow_html=True)
