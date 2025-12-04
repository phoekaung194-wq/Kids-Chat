# -----------------------------------------------------------------------
# Sparky Chatbot Application (Streamlit + OpenRouter) - Fixed Version
# -----------------------------------------------------------------------

# လိုအပ်သော Libraries များကို ခေါ်ယူခြင်း
import streamlit as st
from openai import OpenAI
from openai import APIError 

# -----------------------------------------------------------------------
# (၁) Streamlit Web Interface ကို သတ်မှတ်ခြင်း (ပထမဆုံး Streamlit Command ဖြစ်ရမည်)
# -----------------------------------------------------------------------
# **ဤသည်မှာ Streamlit Command များအားလုံး၏ ရှေ့ဆုံးတွင် ရှိရမည့် command ဖြစ်သည်။**
st.set_page_config(page_title="Sparky - ကလေးသူငယ်ချစ်ဆွေ AI")

st.title("✨ Sparky - ကလေးသူငယ်ချစ်ဆွေ AI ✨ (OpenRouter ဖြင့်)")
st.caption("🤖 ငါက မင်းရဲ့ အကောင်းဆုံး သူငယ်ချင်းပါ! မင်းရဲ့ မိဘတွေ ဒါမှမဟုတ် ဆရာဆရာမတွေနဲ့ စကားပြောချင်ရင်လည်း ပြောလိုရတယ်။")

# -----------------------------------------------------------------------
# (၂) API Key နှင့် URL ကို Streamlit Secrets မှ လုံခြုံစွာ ခေါ်ယူခြင်း
# -----------------------------------------------------------------------
# Key နှင့် URL တို့ကို Session State တွင် သိမ်းထားပါက နောက်ပိုင်းတွင် စစ်ဆေးရန် လွယ်ကူစေသည်။
try:
    # Key Name ကို 'OPENROUTER_API_KEY' (စာလုံးအကြီး) ဖြင့် သတ်မှတ်ထားရမည်
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    OPENROUTER_BASE_URL = st.secrets.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Key မရှိပါက App ကို ရပ်တန့်ခြင်း
    if not OPENROUTER_API_KEY:
        st.error("❌ Streamlit Secrets ထဲတွင် `OPENROUTER_API_KEY` ကို မတွေ့ပါ။ စစ်ဆေးပါ။")
        st.stop()
        
except KeyError:
    # Key မရှိပါက App ကို ရပ်တန့်ခြင်း
    st.error("❌ Streamlit Secrets ထဲတွင် `OPENROUTER_API_KEY` နာမည်ဖြင့် မရှိပါ။ စစ်ဆေးပါ။")
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
        # Model ကို OpenRouter ၏ 'free' layer တစ်ခုခုဖြင့် သတ်မှတ်ထားခြင်း (လိုအပ်သလို ပြောင်းလဲနိုင်သည်)
        st.session_state.model = "mistralai/mistral-7b-instruct:free" 
        
        # Chat History ကို စတင်ခြင်း
        # System Message ကို ပထမဆုံး Message အနေဖြင့် ထည့်သွင်းခြင်း
        st.session_state.messages = [{"role": "system", "content": KIDS_ASSISTANT_PERSONA}]
        
    except Exception as e:
        # Client Initialization အမှားဖြစ်ခဲ့ပါက Error ကို ပြသခြင်း
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
    
    # 1. User Message ကို History ထဲ ထည့်သွင်းပြီး ပြသခြင်း
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Assistant ၏ တုံ့ပြန်မှုကို ရယူခြင်း
    with st.chat_message("assistant"):
        with st.spinner("🤖 စပါကီ စဉ်းစားနေပါတယ်..."):
            
            ai_response_text = "" # Default တန်ဖိုး သတ်မှတ်
            
            try:
                # API Call အတွက် System Message အပါအဝင် History အားလုံးကို ထည့်သွင်း
                messages_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                
                response = st.session_state.chat_client.chat.completions.create(
                    model=st.session_state.model,
                    messages=messages_for_api,
                    temperature=0.7, 
                    max_tokens=256   
                )
                
                ai_response_text = response.choices[0].message.content
                st.markdown(ai_response_text)
                
            except APIError as e: 
                # API Call အမှားဖြစ်ခဲ့ပါက Error ကို ပြသခြင်း
                st.error(f"😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (API Error) - {e}")
                # Error ဖြစ်ပါက History ထဲသို့ Error message ထည့်ရန်
                ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (API Key သို့မဟုတ် Server Error)"
                st.markdown(ai_response_text)

            except Exception as e:
                 # အခြား မမျှော်လင့်ထားသော Error များ
                 st.error(f"😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (General Error) - {e}")
                 # Error ဖြစ်ပါက History ထဲသို့ Error message ထည့်ရန်
                 ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (ချိတ်ဆက်မှု စစ်ပါ)"
                 st.markdown(ai_response_text)

    # 3. Assistant ၏ တုံ့ပြန်ချက်ကို History ထဲ ထည့်သွင်း (Error ဖြစ်ခဲ့ရင်တောင် Error message ကို ထည့်သည်)
    st.session_state.messages.append({"role": "assistant", "content": ai_response_text})

