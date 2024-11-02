import streamlit as st
from models.about_users import User, Passkey
from tools.db_init import get_engine
from tools.passkey_auth import create_user, options_to_json

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = 'before_login'

engine, SessionLocal = get_engine()

st.title("Hejminformoj")
st.markdown(
"""
Hejminformoj estas programo por multaj funkcioj.
Ekzemple, hejma buĝeto, todo-listo, kaj panelo por regi inteligentan hejmon.
Ĝi estas tre utila, ĉu ne?
## Funkcioj
- todo
- Kalkulilo de hejma buĝeto
    - Aldoni
    - Montri
- Panelo por regi inteligentan hejmon
"""
)

# # create account and add passkey
# with st.expander("Create Account"):
#     st.write("To get started, please create an account.")
#     username = st.text_input("ID")
#     name = st.text_input("Name")
#     submit_button = st.button("Create Account")
#     if submit_button:
#         if st.session_state['logged_in'] == 'before_login':
#             st.session_state['logged_in'] = 'adding_passkey'
#             credential_creation_options = create_user(SessionLocal, username, name)
#             st.session_state['credential_creation_options'] = credential_creation_options
#             # st.markdown(f"<script>console.log(st.session_state {st.session_state['logged_in']})</script>", unsafe_allow_html=True)
        
#         if 'credential_creation_options' in st.session_state:
#             credential_creation_options = st.session_state['credential_creation_options']
#             st.markdown(
#                 f"""
#                 <p>debug</p>
#                 <script src="./app/static/js/webauthn.js"></script>
#                 <script>
#                     const options = JSON.parse(`{options_to_json(credential_creation_options)}`);
#                     const regRes = startRegistration(options);
#                     const servRes = sendRegistrationResponse(regRes);
#                     console.log(servRes);
#                 </script>
#                 """,
#                 unsafe_allow_html=True,
#             )

# with st.expander("Add Passkey"):
#     st.write("To secure your account, please add a passkey.")
#     submit_button = st.button("Start Adding Passkey")
