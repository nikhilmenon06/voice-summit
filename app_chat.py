import streamlit as st
from streamlit_chat import message
from streamlit_option_menu import option_menu
from utils import get_initial_message, get_chatgpt_response, update_chat
import os
from dotenv import load_dotenv
load_dotenv()
import openai

#openai.api_key = os.getenv('OPENAI_API_KEY')

# For streamlit deployment, the api key is added to streamlit-secrets in the app settings (during/after delpoyment)
openai.api_key = st.secrets["OPEN_API_KEY"]


def main():
    st.set_page_config(page_title="Chatbot Application", page_icon=":robot_face:", layout="centered")
    st.image('assets/bp_chat_logo.png', width=600)


    # st.image('path/to/your/header_image.png', width=700)

    selected_page = option_menu(None, ["Editor", "Chat"], icons=['edit', 'comments'], menu_icon="bars", default_index=0,
                                orientation="horizontal", styles={"nav-link-selected": {"background-color": "#7D9338"}})

    if selected_page == "Editor":
        editor()
    elif selected_page == "Chat":
        chat()




def chat():

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    if 'query' not in st.session_state:
        st.session_state.query = ''

    def submit():
        st.session_state.query = st.session_state.input
        st.session_state.input = ''

    #Uncomment the second line to have GPT4 option in the select box dropdown menu

    model = st.selectbox(
        "Select a model",
        ("gpt-3.5-turbo",)
        #("gpt-3.5-turbo", "gpt-4")
    )

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    #if st.session_state['generated']:

        # for i in range(len(st.session_state['generated'])-1, -1, -1):
        #     message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        #     message(st.session_state["generated"][i], key=str(i))
    
    def display():

        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

        #with st.expander("Show Messages"):
         #   st.write(st.session_state['messages'])


    st.text_input("Query: ", key="input", on_change=submit)
    #st.text_input("Query: ", key="input", on_change=submit)

    if 'messages' not in st.session_state:
        st.session_state['messages'] = get_initial_message()
        st.session_state['messages'] = update_chat(st.session_state['messages'],"system", st.session_state['prompt'])
    

    if st.session_state.query:
        with st.spinner("generating..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", st.session_state.query)
            # st.write("Before  making the API call")
            # st.write(messages)
            response = get_chatgpt_response(messages,model)
            messages = update_chat(messages, "assistant", response)
            st.session_state.past.append(st.session_state.query)
            st.session_state.generated.append(response)
            display()
            #st.experimental_rerun()
            



def editor():

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    prompt = st.text_area("Write your prompt here:", value=st.session_state.prompt, height=200)

    if st.button("Save Prompt"):
        st.session_state.prompt = prompt
        st.success("Prompt saved successfully!")


if __name__ == "__main__":
    main()