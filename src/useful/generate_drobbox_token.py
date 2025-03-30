import dropbox

APP_KEY = "your-app-key"
APP_SECRET = "your-app-secret"

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')

authorize_url = auth_flow.start()
print("🔑 Authorization URL:", authorize_url)
print("➡️ Open the above URL in your browser, click 'Allow', then copy the code provided.")

auth_code = input("Paste authorization code here: ").strip()

oauth_result = auth_flow.finish(auth_code)
print("✅ Your refresh token is:", oauth_result.refresh_token)
print("ℹ️ Save this token securely!")
