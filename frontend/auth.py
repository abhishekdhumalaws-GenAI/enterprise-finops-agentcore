import os

import boto3
import streamlit as st

COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def _client():
    return boto3.client("cognito-idp", region_name=AWS_REGION)


def login_form():
    st.subheader("Sign in")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        try:
            response = _client().initiate_auth(
                ClientId=COGNITO_APP_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password
                }
            )

            # Cognito may return a challenge instead of tokens
            if "ChallengeName" in response:
                st.error(f"Cognito challenge: {response['ChallengeName']}")
                st.json(response)
                return

            auth_result = response.get("AuthenticationResult", {})

            access_token = auth_result.get("AccessToken")
            id_token = auth_result.get("IdToken")
            refresh_token = auth_result.get("RefreshToken")

            if not access_token or not id_token:
                st.error("Authentication succeeded but no tokens were returned.")
                st.json(response)
                return

            st.session_state["access_token"] = access_token
            st.session_state["id_token"] = id_token
            st.session_state["refresh_token"] = refresh_token
            st.session_state["authenticated"] = True
            st.session_state["username"] = email

            st.success("Login successful.")
            st.rerun()

        except Exception as e:
            st.error(f"Login failed: {e}")

def require_login():
    if not st.session_state.get("authenticated"):
        st.title("Enterprise AI FinOps Platform")
        st.caption("Secure login powered by Amazon Cognito.")
        login_form()
        st.stop()


def logout_button():
    with st.sidebar:
        st.write(f"Signed in as: `{st.session_state.get('username')}`")

        st.write("Access token:", "Yes" if st.session_state.get("access_token") else "No")
        st.write("ID token:", "Yes" if st.session_state.get("id_token") else "No")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def auth_headers():
    token = st.session_state.get("id_token") or st.session_state.get("access_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }
