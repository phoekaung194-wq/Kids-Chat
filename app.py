import streamlit as st
import os
from openai import OpenAI
from openai import APIError # FIXED: APIError ကို အစားထိုး import လုပ်ထားသည်

# ⚠️ အဆင့် ၁: API Key ကို သတ်မှတ်ခြင်း
# အရေးကြီးသည်: သင့်ရဲ့ OpenRouter Key အစစ်အမှန်ဖြင့် အစားထိုးပါ။ 
OPENROUTER_API_KEY = "st.secrets["openrouter_api_key"]

# OpenRouter အတွက် Base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# 🤖 ကလေးများအတွက် AI Assistant ရဲ့ လက္ခဏာရပ်များ
KIDS_ASSISTANT_PERSONA = (
    "You are Sparky, a very cheerful, kind, and safe assistant for young children "
    "(ages 5 to 8). Your main goal is to be a fun friend who tells simple stories, "
    "asks easy questions, and always encourages the child. "
    "Keep all your answers short and friendly, and use lots of emojis (🌟, ✨, 😄). "
    "Always respond in the language the child is using."
)

# ⭐️ OpenRouter Client (OpenAI ၏ Client ကို အသုံးပြု) ဖြင့် Chat Session ကို စတင်ခြင်း
if 'chat_client' not in st.session_state:
    try:
        # OpenRouter Key ကိုစစ်ဆေးပါ
        if OPENROUTER_API_KEY == "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":
            st.warning("⚠️ OpenRouter API Key ကို Key အစစ်အမှန်ဖြင့် အစားထိုးပေးပါ။")
        
        # OpenRouter နှင့်ချိတ်ဆက်ရန် OpenAI Client ကို အသုံးပြုခြင်း
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
        
        # Chat History များကို စတင်သတ်မှတ်ခြင်း
        st.session_state.chat_client = client
        st.session_state.model = "mistralai/mistral-7b-instruct:free" # OpenRouter တွင် အခမဲ့ သုံးနိုင်သော Model
        
        # Streamlit Chat History
        st.session_state.messages = [] 
        
        # စနစ်ညွှန်ကြားချက်ကို ပထမဆုံး Message အနေဖြင့် ထည့်သွင်းခြင်း
        st.session_state.messages.insert(0, {"role": "system", "content": KIDS_ASSISTANT_PERSONA})


    except Exception as e:
        st.error(f"❌ AI Client စတင်ရာတွင် အမှား: {e}")
        st.error("OpenRouter API Key သို့မဟုတ် ချိတ်ဆက်မှုကို စစ်ဆေးပါ။")
        st.stop()


# 💻 Streamlit Web Interface
st.set_page_config(page_title="Sparky - ကလေးသူငယ်ချင်း AI")
st.title("🌟 Sparky - ကလေးသူငယ်ချင်း AI ✨ (OpenRouter ဖြင့်)")
st.caption("ငါက စပါကီပါ။ မင်းနဲ့ စကားပြောရတာ ဝမ်းသာပါတယ်! (Gemini အတွက် Billing မလိုပါ)")

# System Message ကို ပြသရန် မလို၊ User/Assistant Message များကိုသာ ပြသမည်
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("စပါကီကို မေးခွန်းတစ်ခု မေးပါ..."):
    # User Message ကို History ထဲ ထည့်သွင်း
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
                    temperature=0.7, # ဖန်တီးမှုအားကောင်းစေရန်
                    max_tokens=256   # ကလေးများအတွက် တိုတိုသာ ဖြေရန်
                )
                
                ai_response_text = response.choices[0].message.content
                st.markdown(ai_response_text)

            except APIError as e: # FIXED: အခု APIError ကို ဖမ်းယူနိုင်ပြီ
                # APIError သည် Status code ကို တိုက်ရိုက်မပံ့ပိုးနိုင်သော်လည်း Error ကိုပြသနိုင်
                ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (API Key သို့မဟုတ် Server Error)"
                st.error(f"Error Details: {e}")
                st.markdown(ai_response_text)
            except Exception as e:
                 ai_response_text = "😥 စပါကီ စကားပြောဖို့ ခက်ခဲနေပါတယ်။ (ချိတ်ဆက်မှု စစ်ပါ)"
                 st.error(f"General Error: {e}")
                 st.markdown(ai_response_text)

    # Assistant Message ကို History ထဲ ထည့်သွင်း
    st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
