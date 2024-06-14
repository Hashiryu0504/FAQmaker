# FAQmaker

環境変数、projectidはenvi下に置いてるjsonを参照
```
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\envi\\credentials-file.json'

# Load the credentials file to get the project ID
credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
with open(credentials_path, 'r') as file:
    credentials = json.load(file)

project_id = credentials.get('project_id')
```