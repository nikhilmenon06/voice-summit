import streamlit as st
from streamlit_chat import message
from streamlit_option_menu import option_menu
from utils import get_initial_message, get_chatgpt_response, update_chat
import os
from dotenv import load_dotenv
load_dotenv()
import openai
from io import StringIO

# streamlit_app.py

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
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
        
        if st.session_state.bug_flag == 1:
            st.warning("Oops, your previous message was sent to the model again", icon = "🤖")
        

        def submit():
            st.session_state.query = st.session_state.input
            st.session_state.input = ''

        #Uncomment the second line to have GPT4 option in the select box dropdown menu

        # model = st.selectbox(
        #     "Select a model",
        #     ("gpt-3.5-turbo",)
        #     #("gpt-3.5-turbo", "gpt-4")
        # )
        #model = "gpt-3.5-turbo"
        model = "gpt-4"

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
        
        st.markdown('Like it? Want to talk? Get in touch! <a href="mailto:leonid.sokolov@big-picture.com">Leonid Sokolov</a> // <a href="mailto:hello@streamlit.io">Imke Bewersdorf</a>', unsafe_allow_html=True)
                



    def editor():


        def filename_display(filename):
            filename = filename[:-4]
            split_filename = filename.split("_")
            mod_filename = ""
            for part in split_filename:
                mod_filename = mod_filename + part.capitalize() + " "
            
            mod_filename = mod_filename.strip()
            return mod_filename


        if 'generated' in st.session_state:
            st.session_state.bug_flag = 1
        else:
            st.session_state.bug_flag = 0

        
        
        if 'prompt' not in st.session_state:
            st.session_state.prompt = ""


        # uploaded_file = st.file_uploader("Choose a prompt file:")

        # if uploaded_file is not None:
        #     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        #     string_data = stringio.read()
        #     st.session_state.prompt = string_data

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to /prompts subdirectory
        prompts_dir = os.path.join(script_dir, 'prompts')

        # List all files in the /prompts directory
        files = [f for f in os.listdir(prompts_dir) if os.path.isfile(os.path.join(prompts_dir, f))]

        # Add a select box for all files
        selected_file = st.selectbox('Select a file:', files, format_func = filename_display)
        selected_file_path = os.path.join(prompts_dir,selected_file)

        with open(selected_file_path, "r") as file:
            selected_file_contents = file.read()


        st.session_state.prompt =  selected_file_contents
        

        prompt = st.text_area("Your prompt is here:", value=st.session_state.prompt, height=200)

        if st.button("Save Prompt"):
            st.session_state.prompt = prompt
            st.success("Prompt saved successfully!")
        
        st.markdown('Like it? Want to talk? Get in touch! <a href="mailto:leonid.sokolov@big-picture.com">Leonid Sokolov</a> // <a href="mailto:hello@streamlit.io">Imke Bewersdorf</a>', unsafe_allow_html=True)


    if __name__ == "__main__":
        main()
