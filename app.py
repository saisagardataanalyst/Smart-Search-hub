import streamlit as st 
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
import os
from dotenv import load_dotenv

## Arxiv and Wikipedia tools
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=2500)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)

api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=2500)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

search = DuckDuckGoSearchRun(name="Search")

st.title("🌐 SmartSearch Hub: AI-Powered Knowledge Assistant")

## Slider for setting
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq API key:", type="password")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Check if API key is provided
if not api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.", icon="⚠️")
else:
    if prompt := st.chat_input(placeholder="What is machine learning?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="mixtral-8x7b-32768",  # Updated to use a valid Groq model
            streaming=True
        )
        tools = [search, arxiv, wiki]

        search_agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            verbose=True
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
            response = search_agent.run(prompt, callbacks=[st_cb])
            st.session_state.messages.append({'role': 'assistant', "content": response})
            st.write(response)
