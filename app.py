import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import streamlit.components.v1 as components


# Load API key from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI LLM
llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini", temperature=0.5)

# Define custom prompt template
prompt_template = PromptTemplate(
    input_variables=["tasks"],
    template="""
You are a productivity assistant. Categorize and prioritize the following tasks.

Instructions:
1. Group each task under a relevant category like: Work, Personal, Health, Learning, Finance, etc.
2. For each task, assign a priority level: High, Medium, or Low.
3. do not use the word priority in the output. just show the priority level

Output format:
-- Category Name
- Priority: Task

Tasks:
{tasks}
"""
)

# Create a LangChain chain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Streamlit UI
st.set_page_config(page_title="AI Task Categorizer", layout="centered")
st.title("🧠 AI Task Categorizer & Prioritizer")
st.write("Paste your tasks below. The assistant will group them by category and assign priorities.")

user_input = st.text_area("✍️ Enter your tasks:", height=200)

checked_items_state = {}
final_output_lines = []

if "organized_tasks" not in st.session_state:
    st.session_state.organized_tasks = []
    st.session_state.raw_response_lines = []

if st.button("Categorize & Prioritize"):
    if not user_input.strip():
        st.warning("⚠️ Please enter some tasks.")
    else:
        with st.spinner("Organizing your tasks..."):
            try:
                response = chain.run(tasks=user_input.strip())
                st.session_state.raw_response_lines = response.split("\n")
                st.success("✅ Organized Task List:")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if st.session_state.raw_response_lines:
    current_category = ""
    category_to_tasks = {}

    for line in st.session_state.raw_response_lines:
        if line.startswith("--"):
            current_category = line.strip()
            st.markdown(f"**{current_category}**")
            category_to_tasks[current_category] = []
        elif line.strip().startswith("- "):
            task_line = line.strip()[2:]
            task_key = f"{current_category}::{task_line}"
            checked = st.checkbox(task_line, key=task_key)
            category_to_tasks[current_category].append((task_line, checked))
        elif line.strip():
            st.markdown(line.strip())

    if st.button("Copy Selected Tasks"):
        copied_text = ""
        for cat, tasks in category_to_tasks.items():
            selected = [f"- {t[0]}" for t in tasks if t[1]]
            if selected:
                copied_text += f"{cat}\n" + "\n".join(selected) + "\n\n"

        if copied_text:
            st.text_area("📋 Copied Tasks (Read-only)", value=copied_text.strip(), height=200, key="copied_area")
        
            # Inject JS to copy text from the textarea to clipboard
            components.html(f"""
                <script>
                function copyToClipboard() {{
                    const textarea = window.parent.document.querySelector('textarea[key="copied_area"]');
                    if (textarea) {{
                        textarea.select();
                        document.execCommand('copy');
                        alert("✅ Tasks copied to clipboard!");
                    }}
                }}
                </script>
                <button onclick="copyToClipboard()">📋 Copy to Clipboard</button>
            """, height=50)
        else:
            st.warning("⚠️ No tasks selected to copy.")
