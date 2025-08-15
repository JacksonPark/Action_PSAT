import streamlit as st
import time
import google.generativeai as genai
import pandas as pd

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="실전 역량 평가 (P-SAT)",
    page_icon="🤖",
    layout="wide",
)

# --- Google Gemini API Key 설정 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("Google Gemini API 키를 설정해주세요! (.streamlit/secrets.toml)")
    st.stop()

# --- 상태 관리 변수 초기화 ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if "chat" not in st.session_state:
    system_instruction = """
    당신은 '행동뷰티' 회사의 친절하고 유능한 데이터 분석팀원입니다. 당신의 이름은 '김민준'입니다.
    당신은 신규 립스틱 라인 프로젝트와 관련된 모든 정형 및 비정형 데이터의 접근 권한을 가지고 있습니다.
   
    사용자가 묻는 데이터에 대하여 가상 데이터를 생성하고, 한번 생성된 데이터 내용은 바뀔 수 없다.
    데이터 자체만 제공할 뿐,추가적인 의견은 제공하지 않는다.
    모든 답변은 한국어로 해야 합니다.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.chat = model.start_chat(history=[
        {"role": "user", "parts": [system_instruction]},
        {"role": "model", "parts": ["네, 알겠습니다. 저는 '행동뷰티'의 데이터 분석팀원 김민준입니다. 신규 립스틱 프로젝트 관련 데이터를 바탕으로 질문에 답변해 드리겠습니다."]}
    ])
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 저는 데이터 분석팀원 김민준입니다. '행동뷰티' 신규 립스틱 라인 관련해서 궁금한 점이 있으시면 무엇이든 물어보세요."}]

if 'ceo_feedback' not in st.session_state:
    st.session_state.ceo_feedback = ""
if 'attack_start_time' not in st.session_state:
    st.session_state.attack_start_time = 0
if 'final_report' not in st.session_state:
    st.session_state.final_report = ""
if 'final_script' not in st.session_state:
    st.session_state.final_script = ""


# --- 행동주의자 대표 AI의 피드백을 생성하는 함수 ---
def generate_ceo_feedback(report, script):
    ceo_model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    당신은 매우 까다롭고 실행 중심적인 '행동주의자' 대표입니다. 
    당신은 지금 신입 PM이 제출한 보고서와 발표 스크립트를 검토하고 있습니다. 
    아래 두 결과물을 비판적으로 분석하여, 리더 및 경영진의 입장에서 보았을 때 부족한 점을 날카롭게 지적하세요. 
    그리고 새로운 제약 조건 (줄어든 가용 예산, 해당 플랜과 관련된 직원의 퇴사, 기존 거래처들과의 껄끄러운 역학관계 등등, 제약 조건은 앞에 작성한 3가지만 의미하지 않는다) 
    중 하나를 반드시 추가하여, 이 조건에 맞게 계획을 수정하라고 지시하는 피드백을 생성하세요.'보고서 및 발표의 치명적인 결점'에 대해서 언급하나, 수정된 계획 제출 요구 사항에 대해서는
    하나씩 친절하게 설명하지 않는다.
    

    ---
    [제출된 보고서]
    {report}

    ---
    [제출된 발표 스크립트]
    {script}
    ---
    """

    response = ceo_model.generate_content(prompt)
    return response.text

# 💡 [STEP 5] 제출 단계를 관리할 상태 변수 추가
if 'submission_phase' not in st.session_state:
    st.session_state.submission_phase = 0
if 'initial_report' not in st.session_state:
    st.session_state.initial_report = ""
if 'final_report' not in st.session_state:
    st.session_state.final_report = ""

# --- 메인 화면 구성 ---
st.title("🤖 실전 역량 평가 (Problem-Solving Ability Test)")
st.markdown("---")

if st.session_state.start_time == 0:
    # ... (준비 단계 UI - 변경 없음)
    with st.expander("⚠️ 평가 목적 및 방법에 대해 확인하세요", expanded=True):
        st.write("""
        - 이 평가는 정답이 정해진 문제를 푸는 능력이 아닌, **실제 업무 상황에서 문제를 해결하는 능력**을 측정하기 위해 설계되었습니다.
        - 당신은 주어진 비즈니스 시나리오의 담당자가 되어, AI 챗봇과 상호작용하며 과업을 수행하게 됩니다.
        - AI 챗봇은 데이터 분석가, 동료, 상사 등 다양한 역할을 수행하며 당신에게 정보를 제공하거나 피드백을 줄 수 있습니다.
        - 전체 평가 시간은 **60분**이며, 시간 내에 최종 결과물을 제출해야 합니다.
        """)
    st.markdown("---")
    st.header("당신에게 주어진 과업 시나리오")
    if st.button("과업 시작하기"):
        st.session_state.start_time = time.time()
        st.rerun()

# --- Phase 3: 최종 제출 완료 시 평가 완료 화면 표시 ---
elif st.session_state.submission_phase == 3:
    st.success("## 평가가 성공적으로 완료되었습니다!")
    st.write("수고하셨습니다. 아래는 제출하신 보고서 내용입니다.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 최초 제출안")
        st.text_area("보고서 초안", value=st.session_state.initial_report, height=150, disabled=True)
        st.text_area("스크립트 초안", value=st.session_state.initial_script, height=150, disabled=True)
    with col2:
        st.subheader("📝 최종 제출안")
        st.text_area("수정된 보고서", value=st.session_state.final_report, height=150, disabled=True)
        st.text_area("수정된 스크립트", value=st.session_state.final_script, height=150, disabled=True)

    # --- 데이터 정리 ---
    final_data_string = f"""
    # [실전 역량 평가 결과]

    ## 1. 최초 제출안
    ### 보고서
    {st.session_state.initial_report}

    ### 스크립트
    {st.session_state.initial_script}

    ## 2. 최종 제출안
    ### 보고서
    {st.session_state.final_report}

    ### 스크립트
    {st.session_state.final_script}

    ## 3. AI 대화 로그
    {"-" * 20}
    """
    for message in st.session_state.messages:
        final_data_string += f"{message['role']}: {message['content']}\n"

    st.markdown("---")

    # --- 다운로드 버튼 ---
    st.download_button(
        label="📋 평가 결과 전체 내용 다운로드 (.txt)",
        data=final_data_string,
        file_name="evaluation_result.txt",
        mime="text/plain"
    )


# --- 과업 수행 중 화면 ---
else:
    # --- Phase 2: 15분 타임 어택 ---
    if st.session_state.submission_phase == 2:
        # 15분 타이머 계산
        elapsed = time.time() - st.session_state.attack_start_time
        remaining = max(0, 900 - elapsed)  # 15분 = 900초
        mins, secs = divmod(int(remaining), 60)

        # 타이머 UI (크고 굵게)
        st.markdown(f"<h2 style='text-align: center; color: red;'>남은 시간: {mins:02d}:{secs:02d}</h2>",
                    unsafe_allow_html=True)

        final_report_text = st.text_area("📄 수정된 보고서", value=st.session_state.initial_report, height=300)
        final_script_text = st.text_area("🎙️ 수정된 스크립트", value=st.session_state.initial_script, height=200)

        if st.button("최종 제출하기"):
            st.session_state.final_report = final_report_text
            st.session_state.final_script = final_script_text
            st.session_state.submission_phase = 3  # 최종 완료 단계로 이동
            st.rerun()

    # --- Phase 0 & 1: 기본 과업 수행 ---
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("""
            **배경:** "당신은 '행동뷰티' 회사의 신규 립스틱 라인 PM (Project Manager) 입니다. 신규 립스틱 라인 런칭 3개월 후, 목표 매출의 60%만 달성하여 비상입니다."
            **초기 정보:** 아래는 현재까지의 월별 매출 현황표입니다.
            """)
            sales_data = {'월': ['1월', '2월', '3월'], '목표 매출': ['1억 원', '1억 원', '1억 원'],
                          '실제 매출': ['7,000만 원', '6,000만 원', '5,000만 원']}
            sales_df = pd.DataFrame(sales_data)
            st.table(sales_df.set_index('월'))
            st.success(
                "**당신의 미션:** 원인을 분석하고, 2주 안에 실행할 수 있는 구체적인 개선안을 담아 '행동주의자 대표'에게 보고할 1페이지 분량의 보고서와 3분 발표 스크립트를 작성하세요.")
            st.markdown("---")
            st.subheader("🤖 데이터 분석팀원과의 대화")
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            if prompt := st.chat_input("질문을 입력하세요..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("AI가 답변을 생성중입니다..."):
                        response = st.session_state.chat.send_message(prompt)
                        ai_response = response.text
                        st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

        with col2:
            # --- Phase 0: 최초 초안 작성 ---
            if st.session_state.submission_phase == 0:
                st.subheader("결과물 작성 및 제출")
                report_text = st.text_area("📄 1페이지 보고서 초안", height=250, key="report_area")
                script_text = st.text_area("🎙️ 3분 발표 스크립트 초안", height=150, key="script_area")

                if st.button("보고서 및 스크립트 제출하기"):
                    st.session_state.initial_report = report_text
                    st.session_state.initial_script = script_text
                    with st.spinner("대표님께서 보고서를 검토중입니다... 잠시만 기다려주세요."):
                        st.session_state.ceo_feedback = generate_ceo_feedback(report_text, script_text)
                    st.session_state.submission_phase = 1
                    st.rerun()

            # --- Phase 1: AI 피드백 확인 및 타임어택 시작 ---
            elif st.session_state.submission_phase == 1:
                st.subheader("대표님 피드백")
                st.error(st.session_state.ceo_feedback)
                st.markdown("---")
                st.info("""
                **안내:** 대표님의 피드백을 확인하셨나요? 
                지금부터 **15분** 동안 이 피드백을 반영하여 결과물을 수정해야 합니다. 
                압박 상황에서의 문제 해결 능력을 평가하기 위한 과정입니다.
                """)
                if st.button("🚨 15분 수정 시작하기"):
                    st.session_state.attack_start_time = time.time()
                    st.session_state.submission_phase = 2
                    st.rerun()