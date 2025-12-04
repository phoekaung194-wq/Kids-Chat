# -----------------------------------------------------------------------
# Sparky Chatbot Application (Streamlit + OpenRouter)
# -----------------------------------------------------------------------
# လိုအပ်သော Libraries များကို ခေါ်ယူခြင်း
import streamlit as st
import os # သုံးထားခြင်းမရှိ၍ ဖယ်ရှားနိုင်သည်
from openai import OpenAI
from openai import APIError 

# -----------------------------------------------------------------------
# (၁) Streamlit Web Interface ကို သတ်မှတ်ခြင်း (ပထမဆုံး Command ဖြစ်ရမည်)
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Sparky - ကလေးသူငယ်ချစ်ဆွေ AI",
    layout="wide",
    # iPad (iOS) ၏ JavaScript Syntax Error ကို ဖြေရှင်းရန်အတွက်
    disable_safe_math_with_Katex=True 
)

st.title("✨ Sparky - ကလေးသူငယ်ချစ်ဆွေ AI ✨ (OpenRouter ဖြင့်)")
st.caption("🤖 ငါက မင်းရဲ့ အကောင်းဆုံး သူငယ်ချင်းပါ! မင်းရဲ့ မိဘတွေ ဒါမှမဟုတ် ဆရာဆရာမတွေနဲ့ စကားပြောချင်ရင်လည်း ပြောလိုရတယ်။")

# -----------------------------------------------------------------------
# (၂) API Key နှင့် URL ကို Streamlit Secrets မှ လုံခြုံစွာ ခေါ်ယူခြင်း
# -----------------------------------------------------------------------
# Key ကို မစတင်မီ စစ်ဆေးခြင်း
try:
    # Key Name ကို 'OPENROUTER_API_KEY' (စာလုံးအကြီး) ဖြင့် သတ်မှတ်ထားရမည်
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    OPENROUTER_BASE_URL = st.secrets["OPENROUTER_BASE_URL"]
    
    if not OPENROUTER_API_KEY or not OPENROUTER_BASE_URL:
        st.error("❌ Streamlit Secrets ထဲတွင် API Key (သို့မဟုတ်) Base URL ကို မတွေ့ပါ။")
        st.stop()
        
except KeyError:
    st.error("❌ Streamlit Secrets ထဲတွင် 'OPENROUTER_API_KEY' သို့မဟုတ် 'OPENROUTER_BASE_URL' နာမည်ဖြင့် မရှိပါ။ စစ်ဆေးပါ။")
    st.stop()


# -----------------------------------------------------------------------
# (၃) Chat Client နှင့် History ကို စတင်ခြင်း (Initialization)
# -----------------------------------------------------------------------

# 🤖 ကလေးများအတွက် AI Assistant ရဲ့ လက္ခဏာရပ်များ
KIDS_ASSISTANT_PERSONA = (
    "You are Sparky, a very cheerful, kind, and safe assistant for young children "
    "(ages 5 to 8). Your main goal is to be a fun friend who tells simple stories, "
    "asks easy questions, and always encourages the child. "
    "Keep all your answers short and friendly, and use lots of emojis (🌟, ✨, 😄). "
    "Always respond in the language the child is using."
)

if 'chat_client' not in st.session_state:
    try:
        # OpenRouter နှင့်ချိတ်ဆက်ရန် OpenAI Client ကို အသုံးပြုခြင်း
        client = OpenAI(
            api_key=OPENROUTER_API_KEY, # လုံခြုံစွာ ခေါ်ယူထားသော Key
            base_url=OPENROUTER_BASE_URL
        )
        
        # Session State တွင် Client, Model နှင့် History များကို သတ်မှတ်ခြင်း
        st.session_state.chat_client = client
        st.session_state.model = "mistralai/mistral-7b-instruct:free" 
        
        # Chat History ကို စတင်ခြင်း
        st.session_state.messages = [] 
        
        # စနစ်ညွှန်ကြားချက်ကို ပထမဆုံး Message အနေဖြင့် ထည့်သွင်းခြင်း
        st.session_state.messages.append({"role": "system", "content": KIDS_ASSISTANT_PERSONA})

    except Exception as e:
        st.error(f"❌ AI Client စတင်ရာတွင် အမှား: {e}")
        st.stop()


# -----------------------------------------------------------------------
# (၄) Chat History ကို ပြသခြင်း (Display)
# -----------------------------------------------------------------------

# System Message ကို ဖယ်ထားပြီး User/Assistant Message များကိုသာ ပြသမည်
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# -----------------------------------------------------------------------
# (၅) User Input ကို လက်ခံခြင်းနှင့် API Call
# -----------------------------------------------------------------------
if prompt := st.chat_input("စပါကီကို မေးခွန်းတစ်ခု မေးပါ..."):
    # User Message ကို History ထဲ ထည့်သွင်းပြီး ပြသခြင်း
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 စပါကီ စဉ်းစားနေပါတယ်..."):
            try:
                # OpenRouter API Call (Chat Completion ပုံစံ)
                response = st.session_state.chat_client.chat.completions.create(
                    model=st.session_state.model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    temperature=0.7, 
                    max_tokens=256   
                )
                
                ai_response_text = response.choices[0].message.content
                st.markdown(ai_response_text)
                
            except APIError as e: 
                # API Call အမှားဖြစ်ခဲ့ပါက Error ကို ပြသခြင်း
                ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (API Key သို့မဟုတ် Server Error)"
                st.error(f"Error Details: {e}")
                st.markdown(ai_response_text)
            
            except Exception as e:
                 # အခြား မမျှော်လင့်ထားသော Error များ
                 ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (ချိတ်ဆက်မှု စစ်ပါ)"
                 st.error(f"General Error: {e}")
                 st.markdown(ai_response_text)

    # Assistant Message ကို History ထဲ ထည့်သွင်း
    st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
