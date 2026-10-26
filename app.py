import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# OpenAI API 연동 준비 (필요시 키 입력)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key"))
except ImportError:
    client = None

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 Custom CSS (스크린샷 UI 스타일 반영)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="맞춤형 퇴원교육 시스템",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 화면 스타일링 (좌측 사이드바, 상단 탭, 대시보드 카드 디자인)
st.markdown("""
<style>
    /* 상단 헤더 영역 */
    .header-container {
        background-color: #0E6288;
        padding: 12px 20px;
        color: white;
        border-radius: 8px 8px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        font-size: 20px;
        font-weight: bold;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #DEE2E6;
    }
    .patient-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E9ECEF;
        margin-bottom: 15px;
    }
    .patient-card h4 {
        margin-top: 0;
        color: #0E6288;
        border-bottom: 2px solid #0E6288;
        padding-bottom: 5px;
    }
    .patient-info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 14px;
    }
    .signature-box {
        border: 1px solid #CED4DA;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
        background-color: #FFFFFF;
        margin-top: 10px;
    }
    
    /* 대시보드 카드 스타일 */
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        height: 100%;
    }
    .card-title {
        font-size: 16px;
        font-weight: bold;
        color: #1A365D;
        border-bottom: 2px solid #CBD5E0;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .badge-success {
        background-color: #C6F6D5;
        color: #22543D;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-danger {
        background-color: #FED7D7;
        color: #742A2A;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태 및 임시 데이터(EMR 연동 데이터) 초기화
# -----------------------------------------------------------------------------
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = {
        "name": "김수지",
        "id": "P261025",
        "gender": "F",
        "age": 52,
        "diagnosis": "Acute MI (급성 심근경색)",
        "admission": "2026-10-12",
        "discharge": "2026-10-25",
        "nurse": "김가천",
        "signed": True
    }

if 'personal_factors' not in st.session_state:
    st.session_state.personal_factors = {
        "education": "고등학교 졸업",
        "literacy": "Moderate (중급)",
        "language": "한국어",
        "sensory": "Non (없음)",
        "caregiver": "없음",
        "format": "글 중심"
    }

if 'generated_edu_content' not in st.session_state:
    st.session_state.generated_edu_content = {
        "disease": "심근경색이란? 심장으로 가는 핏줄이 갑자기 꽉 막히거나 문제가 발생해, 심장 근육이 숨을 못 쉬어 손상을 입는 질환",
        "precautions": ["처방 약물 정확히 복용하기", "격렬한 운동 금지", "금연 및 금주 하기"],
        "emergency": "가슴을 쥐어짜는 듯한 통증, 뻐근함, 압박감 시 모든 활동 중단 후 119 신고",
        "outpatient": "2026.11.02 16:00 Dr. 박지훈"
    }

# -----------------------------------------------------------------------------
# 3. 사이드바 (환자 기본 정보 & 담당간호사 확인)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📋 환자 정보")
    p = st.session_state.patient_info
    
    st.markdown(f"""
    <div class="patient-card">
        <div class="patient-info-row"><span><b>이름</b></span><span>{p['name']}</span></div>
        <div class="patient-info-row"><span><b>ID</b></span><span>{p['id']}</span></div>
        <div class="patient-info-row"><span><b>Gender/Age</b></span><span>{p['gender']} / {p['age']}</span></div>
        <div class="patient-info-row"><span><b>Diagnosis</b></span><span style="color:#D69E2E; font-weight:bold;">{p['diagnosis']}</span></div>
        <div class="patient-info-row"><span><b>Admission</b></span><span>{p['admission']}</span></div>
        <div class="patient-info-row"><span><b>Discharge</b></span><span>{p['discharge']}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 👩‍⚕️ 담당간호사")
    
    st.markdown(f"""
    <div class="signature-box">
        <span style="font-family: 'Brush Script MT', cursive; font-size: 24px; color: #1A365D;">M. Kim</span>
        <br><small>{p['nurse']} 간호사</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("확인완료 (서명)", use_container_width=True):
        st.session_state.patient_info['signed'] = True
        st.success("간호사 승인이 완료되었습니다.")
        
    st.caption("Contact: 1234-5678 | Help")

# -----------------------------------------------------------------------------
# 4. 메인 화면 헤더 및 탭 구성
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <div class="header-title">📋 맞춤형 퇴원교육 시스템</div>
    <div style="font-size:12px;">Saved successfully</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "메인 화면", 
    "상세 퇴원교육", 
    "복약 안내", 
    "생활관리", 
    "이해도 평가"
])

# =============================================================================
# TAB 1: 메인 화면
# =============================================================================
with tab1:
    st.write("")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">맞춤형 퇴원교육 생성</div>
            <p>• <b>질환 설명, 퇴원 후 주의사항, 응급상황 대처법, 외래 일정 안내</b></p>
            <p>• 약 설명, 용법 및 용량 설명, 부작용, 누락 대처 방법</p>
            <p>• 생활관리 안내 - 식단, 활동, 건강지표 측정 및 관리</p>
            <hr style="margin: 10px 0;">
            <small style="color: #4A5568;"><b>현재 설정:</b> 쉬운 의료용어 변환 / 글 중심 출력</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="dashboard-card" style="margin-top: 15px;">
            <div class="card-title">교육 기록 및 이해도 평가</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p>✅ <b>안전 핵심 항목</b> <span class="badge-success">3/3</span></p>
                    <p>✅ <b>일반 학습 문제</b> <span class="badge-success">1/2</span></p>
                    <p>❌ <b>음식 제한 관련 보충 필요</b> <span class="badge-danger">보충필요</span></p>
                </div>
                <div style="text-align: center; background: #EBF8FF; padding: 15px; border-radius: 50%;">
                    <h2 style="margin:0; color:#2B6CB0;">85%</h2>
                    <small style="color: #2B6CB0; font-weight:bold;">Very High</small>
                </div>
            </div>
            <hr>
            <small><b>Patient Feedback</b><br>Verbal: 이해했음 | Non-verbal: 긍정적</small>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">복약 안내</div>
            <table style="width:100%; font-size:14px; text-align:left;">
                <tr><td><b>아스피린 Aspirin</b></td><td>100mg (1정)</td></tr>
                <tr><td><b>리피토정 Atrovastatin</b></td><td>40mg (1정)</td></tr>
                <tr><td><b>콩코르정 Bisoprolol</b></td><td>2.5mg (1정)</td></tr>
                <tr><td><b>디오반정 Valsartan</b></td><td>80mg (1정)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="dashboard-card" style="margin-top: 15px;">
            <div class="card-title">생활관리 안내</div>
            <table style="width:100%; font-size:14px;">
                <tr><td width="30%"><b>식단</b></td><td>저염식, 채소 위주</td></tr>
                <tr><td><b>활동</b></td><td>가벼운 걷기 운동, 무리 금지</td></tr>
                <tr><td><b>모니터링</b></td><td>혈압 / 혈당 체크</td></tr>
                <tr><td><b>다음일정</b></td><td>2026.11.02 16:00 Dr. 박지훈</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: 상세 퇴원교육 생성 & 개인화 설정
# =============================================================================
with tab2:
    st.write("")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("상세 퇴원교육 내용")
        st.markdown("#### 개인화 요소 입력")
        
        edu_status = st.selectbox("교육상태", ["고등학교 졸업", "중학교 졸업", "대학교 졸업 이상", "초등학교 졸업 이하"])
        literacy = st.select_slider("헬스 리터러시 (건강 문해력)", options=["Low (초급)", "Moderate (중급)", "High (상급)"], value="Moderate (중급)")
        language = st.selectbox("선호 언어", ["한국어", "English", "中文", "Tiếng Việt"])
        sensory = st.multiselect("감각이상/제한", ["시력 저하", "청력 저하", "고령"], default=[])
        caregiver = st.radio("보호자 유무", ["있음", "없음"], index=1)
        
        output_format = st.radio(
            "출력 형태", 
            ["글 중심", "그림 + 아이콘 중심", "큰 글씨", "음성 (TTS)"],
            index=0
        )
        
        if st.button("🤖 LLM 기반 맞춤형 교육자료 생성/갱신"):
            st.info("LLM이 환자 프로필 및 EMR 데이터를 바탕으로 쉬운 의료용어 자료를 생성 중입니다...")
            st.success("교육자료 생성이 완료되었습니다!")

    with c2:
        st.subheader("교육자료 미리보기")
        st.markdown(f"""
        <div style="background-color: #FFF; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; height: 500px; overflow-y: auto;">
            <h4>1. 질환설명</h4>
            <p style="color: #C53030; font-weight: bold;">
                {st.session_state.generated_edu_content['disease']}
            </p>
            
            <h4>2. 퇴원 후 주의사항</h4>
            <ul>
                {"".join([f"<li>{item}</li>" for item in st.session_state.generated_edu_content['precautions']])}
            </ul>
            
            <h4>3. 응급 상황 대처 (Red Flag)</h4>
            <p style="color: #C53030; background: #FFF5F5; padding: 8px; border-radius: 4px;">
                ⚠️ {st.session_state.generated_edu_content['emergency']}
            </p>
            
            <h4>4. 외래 일정 안내</h4>
            <p>📅 {st.session_state.generated_edu_content['outpatient']}</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: 복약 안내
# =============================================================================
with tab3:
    st.write("")
    st.subheader("💊 복약 안내")
    
    med_data = {
        "복용 내용": ["항혈소판제", "지질대사개선제", "심장 부담 감소제", "혈관 확장제"],
        "약 이름": ["아스피린장용정\nAspirin", "리피토정\nAtorvastatin", "콩코르정\nBisoprolol", "디오반정\nValsartan"],
        "용법, 용량": ["100mg (1정)", "40mg (1정)", "2.5mg (1정)", "80mg (1정)"],
        "복용 시간": ["아침 식후 30분", "저녁 식후 또는 취침 전", "아침 식후 30분", "아침 식후 30분"],
        "부작용": ["멍, 잇몸 출혈, 속쓰림", "근육통, 쇠약감", "서맥, 어지럼증, 피로", "기립성 어지럼증"]
    }
    df_med = pd.DataFrame(med_data)
    st.table(df_med)
    
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">주요 약물 주의사항</div>
            <ul>
                <li><b>아스피린 & 클로피도그렐:</b> 병용 시 출혈 위험 증가 (멍, 잇몸 출혈 주의)</li>
                <li><b>자몽 주스 피하기:</b> 스타틴 계열 약물 복용 중 자몽 주스 섭취 금지</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_med2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">복약 누락 대처법</div>
            <p><b>환자 분이 처방받은 약:</b> 아스피린정, 리피토정, 콩코르정, 디오반정</p>
            <div style="background-color: #FEFCBF; padding: 10px; border-radius: 6px;">
                • 다음 복용 시간 12시간 이상 남은 경우: 생각난 즉시 복용<br>
                • 다음 복용 시간 12시간 미만 남은 경우: 이번 분량 생략<br>
                <b>⚠️ 절대 2회 용량을 한 번에 복용하지 마세요.</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: 생활관리
# =============================================================================
with tab4:
    st.write("")
    st.subheader("🏃‍♂️ 생활관리 지침")
    
    cols = st.columns(6)
    steps = [
        {"num": "1", "title": "저염식", "desc": "싱겁게 먹기, 소금 섭취 줄이기"},
        {"num": "2", "title": "저지방 식단", "desc": "저지방 및 저콜레스테롤 식단"},
        {"num": "3", "title": "수분/섬유소", "desc": "적절한 수분 및 채소 섭취"},
        {"num": "4", "title": "유산소 운동", "desc": "가벼운 걷기 운동, 무리 금지"},
        {"num": "5", "title": "무거운 물건 금지", "desc": "무거운 물건 들기 절대 금지"},
        {"num": "6", "title": "가벼운 샤워", "desc": "미온수 샤워, 통목욕은 당분간 금지"}
    ]
    
    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div style="border: 2px solid #3182CE; border-radius: 10px; padding: 10px; text-align: center; background: white;">
                <span style="background: #3182CE; color: white; border-radius: 50%; padding: 2px 8px; font-weight: bold;">{steps[idx]['num']}</span>
                <h5 style="margin-top: 10px; color: #2B6CB0;">{steps[idx]['title']}</h5>
                <p style="font-size: 12px; color: #4A5568;">{steps[idx]['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TAB 5: 이해도 평가 및 EMR 간호기록 자동 생성
# =============================================================================
with tab5:
    st.write("")
    eval_col1, eval_col2 = st.columns([1.2, 1])
    
    with eval_col1:
        st.subheader("이해도 평가 (환자용 Quiz)")
        
        st.markdown("#### 🚨 안전 핵심 항목 (100% 통과 필수)")
        q1 = st.radio("Q1. 퇴원 후 흉통(가슴 통증) 발생 시 대처법은?", ["쉬면 나아지므로 기다린다", "즉시 모든 활동을 중단하고 119에 신고한다"], index=1)
        q2 = st.radio("Q2. 처방받은 아스피린의 복용 목적은?", ["통증 완화", "혈전(피떡) 생성을 막아 심장혈관 막힘 예방"], index=1)
        q3 = st.radio("Q3. 약 복용을 잊었을 때 올바른 대처법은?", ["다음번에 2알을 한 번에 먹는다", "다음 복용 시간이 가까우면 이번 분량은 건너뛴다"], index=1)
        
        st.markdown("---")
        st.markdown("#### 📚 일반 학습 항목")
        q4 = st.radio("Q4. 다음 중 피해야 할 음식은?", ["저염 채소 식단", "짠 음식 및 지방이 많은 음식"], index=0)
        q5 = st.radio("Q5. 다음 외래 진료 일정은 언제인가요?", ["2026.11.02 16:00", "2026.12.01 10:00"], index=0)
        
        if st.button("이해도 평가 제출 및 채점"):
            st.success("평가가 완료되었습니다! 오답 항목에 대한 피드백이 자동 제공됩니다.")
            
    with eval_col2:
        st.subheader("교육 기록 및 간호 요약 (EMR 연동)")
        
        st.markdown("""
        <div class="dashboard-card" style="background-color: #F7FAFC;">
            <h4 style="color:#2B6CB0; margin-top:0;">📄 EMR 연동 간호기록 자동 정리</h4>
            <table style="width:100%; font-size:13px; line-height: 2;">
                <tr><td><b>교육 일시</b></td><td>2026.10.25 14:30</td></tr>
                <tr><td><b>교육 대상</b></td><td>환자 본인</td></tr>
                <tr><td><b>교육 내용</b></td><td>퇴원 후 주의사항, 응급상황 대처, 복약, 일상 생활 관리, 다음 외래 일정 등</td></tr>
                <tr><td><b>총점 / 이해도</b></td><td><b>85%</b> (이해도: 높음)</td></tr>
                <tr><td><b>안전항목 통과</b></td><td><span class="badge-success">3/3 통과</span></td></tr>
                <tr><td><b>대면 교육 여부</b></td><td>예</td></tr>
                <tr><td><b>재교육 내용</b></td><td>식이 제한 항목 보충 자료 제공 및 설명 완료</td></tr>
            </table>
            <hr>
            <div style="text-align: right;">
                <small>담당간호사: <b>김가천</b></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 최종 평가 완료 및 EMR 저장", type="primary", use_container_width=True):
            st.balloons()
            st.success("EMR(간호기록)에 성공적으로 저장되었습니다.")