from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import json

# clearly specify the scopes your app needs explicitly
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
credentials = flow.run_local_server(port=0)

output_path = Path('authorized_user.json')

credentials_data = {
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'refresh_token': credentials.refresh_token,
    'token': credentials.token
}

output_path.write_text(json.dumps(credentials_data), encoding='utf-8')
print("✅ authorized_user.json created explicitly cleanly and clearly!")

