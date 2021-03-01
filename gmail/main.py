import pickle 
import os.path
from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from pprint import pprint

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

GROUPS = [
  {
    'label': 'Languages',
    'label_id': 'Label_3701439483774182863',
    'query': 'from:(/(space|noreply)\@quora\.com$/)'
  },
  {
    'label': 'Computing',
    'label_id': 'Label_7390685802474619760',
    'query': 'from:(/\@(medium|refind|fauna|peterc|cooperpress|webopsweekly)\.(com|org)$/)'
  },
  {
    'label': 'Jobs',
    'label_id': 'Label_3245518887489694902',
    'query': 'from:(/(jobs\@producthunt|\@(linkedin|indeedemail|indeed|connectedcommunity|emails\.monster))\.(com|org)$/)'
  },
  {
    'label': 'MCAT',
    'label_id': 'Label_5445637480378699773',
    'query': 'from:(/\@jackwestin\.com$/)'
  },
  {
    'label': 'Articles',
    'label_id': 'Label_8',
    'query': 'from:(/(axios\.com|donotreply\@wordpress\.com|symmetrymagazine\.org|govdelivery\.nsf\.gov)/) '
  },
]

def get_service():
  # Retrieve credentials from pickled token
  creds = None

  if os.path.exists('/tmp/token.pickle'):
    with open('/tmp/token.pickle', 'rb') as token:
      creds = pickle.load(token)
  elif os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)

  # Initiate login for new valid credentials
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = Flow.from_client_secrets_file(
        'credentials.json', 
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob")
      auth_url, _ = flow.authorization_url(access_type='offline')
      print('Please go to this URL:', auth_url)
      code = input('Enter the auth code: ')
      flow.fetch_token(code=code)
      creds = flow.credentials

    # Save the credentials for the next run
    with open('/tmp/token.pickle', 'wb') as token:
      pickle.dump(creds, token)

  service = build('gmail', 'v1', credentials=creds)
  return service

def get_labels():
  service = get_service()
  labels = service.users().labels().list(userId='me').execute()
  pprint(labels)

def process_new_emails(*args, **kwargs):
  service = get_service()

  def list_messages(query, token=None):
    params = {'userId': 'me', 'q': query, 'maxResults': 200, 'labelIds': 'INBOX'}
    params = dict(params, newPageToken=token) if token else params
    return service.users().messages().list(**params).execute()

  def relabel_messages(inbox, label):
    reqBody = {
      'ids': [message['id'] for message in inbox['messages']],
      'addLabelIds': [label], 'removeLabelIds': ['INBOX']}
    return service.users().messages().batchModify(userId='me', body=reqBody).execute()
  
  responses = { 'responses': [] }
  for group in GROUPS:
    inbox = list_messages(group['query'])
    while token := inbox.get('nextPageToken', None):
      nextInbox = list_messages(group['query'], token)
      inbox = {
        'messages': inbox['messages'] + nextInbox['messages'],
        'nextPageToken': nextInbox['nextPageToken']}
    response = relabel_messages(inbox, group['label_id']) if 'messages' in inbox else {}
    responses['responses'].append(response)
  for label, response in zip([group['label'] for group in GROUPS], responses['responses']):
    print(f'Response ({}):', response)
  return responses

if __name__ == '__main__':
  get_labels()
  #process_new_emails()
  