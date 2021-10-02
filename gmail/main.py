import pickle 
import os
import sys
import json
from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()


MAX_RESULTS = 500
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

GROUPS = [
  {
    'label': 'Languages',
    'label_id': 'Label_3701439483774182863',
    'query': 'from:(/((space|.*noreply|.*-personalized-digest)\@quora\.com|(johan|admin)\@francaisauthentique\.com)$/)'
  },
  {
    'label': 'Computing',
    'label_id': 'Label_7390685802474619760',
    'query': 'from:(/(medium|refind|fauna|peterc|cooperpress|webopsweekly|educative|digest\.producthunt|netlify|codepen|sia|altium|coiled|dataelixir|news\@unrealengine|blackfire|peter\@golangweekly|hello\@srenewsletter|mongodbteam\@mongodb|windowsinsiderprogram\@e-mail\.microsoft|hello\@stackshare|no-reply\@heroku|admin\@pycoders|newsletter\@torproject|tyler\@ui|yo\@dev|hello\@faveeo)\.(com|org|io|tech|dev|to)$/)'
  },
  {
    'label': 'Jobs',
    'label_id': 'Label_3245518887489694902',
    'query': 'from:(/(jobs\@producthunt|\@(linkedin|indeedemail|indeed|connectedcommunity|emails\.monster)|demi\@careervault|alerts\@ziprecruiter|jobs\@my\.theladders|alert\@trendingjobsmail|jobs\@techfetch|noreply\@jobvertise|(aggregated|jobalert|lensa24)\@lensa|Alerts\@alerts\.matchedjobs|JobAlerts\@alerts\.careerbliss|jobseekers\@email\.ihire)\.(com|org|io)$/)'
  },
  {
    'label': 'MCAT',
    'label_id': 'Label_5445637480378699773',
    'query': 'from:(/\@jackwestin\.com$/)'
  },
  {
    'label': 'Articles',
    'label_id': 'Label_8',
    'query': 'from:(/(axios\.com|donotreply\@wordpress\.com|symmetrymagazine\.org|govdelivery\.nsf\.gov|email\.crunchbase\.com|pandaily\@substack\.com|info\@ballotpedia\.org|hello\@candor\.co|bill\@sinocism\.com|NEH\@public\.govdelivery\.com|nytdirect\@nytimes\.com)/)'
  },
  {
    'label': 'Articles/Music',
    'label_id': 'Label_1303675674237642848',
    'query': 'from:(/noreply\@bandcamp\.com$/)'
  },
  {
    'label': 'Articles/Quickscope',
    'label_id': 'Label_6885070076085272825',
    'query': 'from:(/(owls\@belowthefold\.news|dan\@tldrnewsletter\.com|daily\@chartr\.co)$/)'
  },
  {
    'label': 'Gaming',
    'label_id': 'Label_645926700005296137',
    'query': 'from:(/(playstationemail\.com|email\.playstation\.com|nintendo\.net|twitch\.tv|thegeekweekly\@boardgamegeek\.com)$/)'
  },
  {
    'label': 'Social Media',
    'label_id': 'Label_3104397777559160928',
    'query': 'from:(/((inspire|explore|ideas)\.pinterest\.com|noreply\@redditmail\.com|info\@twitter\.com)$/)'
  },
  {
    'label': 'Activity',
    'label_id': 'Label_8393204498050519236',
    'query': 'from:(/(send\.grammarly\.com|activity\@notifications\.pinterest\.com|postman-team\@email\.postman\.com|(support|noreply)\@wakatime\.com)$/)'
  },
  {
    'label': 'TRASH',
    'label_id': 'TRASH',
    'query': 'from:(/(NNSSNews\@public\.govdelivery\.com|hulu\@hulumail\.com)$/)'
  },
  {
    'label': 'Traveling',
    'label_id': 'Label_5675453185536797984',
    'query': 'from:(/atlasobscura\.com$/)'
  },
  {
    'label': 'Academic',
    'label_id': 'Label_8186468162443368305',
    'query': 'from:(/(email\.researcher-app\.com|mail\.medscape\.com|ioppublishing\.org|Clinical_Update\@mail\.webmdprofessional\.com|briefing\@nature\.com|scholarcitations-noreply\@google\.com|info\@physicsworld\.com)$/)'
  },
  {
    'label': 'Courses',
    'label_id': 'Label_1103402445307008067',
    'query': 'from:(/(team\@datacamp\.com|jason\@machinelearningmastery\.com|adrian\@pyimagesearch\.com|quincy\@freecodecamp\.org)$/)'
  },
  {
    'label': 'Courses/Questions',
    'label_id': 'Label_2960401731790626460',
    'query': 'from:(/(info\@codewars\.com|no-reply\@hackerrankmail\.com|info\@step1daily\.com)$/)'
  },
  {
    'label': 'Non-Profits',
    'label_id': 'Label_3587034014658743945',
    'query': 'from:(/(stuart\@citiesandmemory\.com|marketing\@hotelcongress\.com)$/)'
  },
  {
    'label': 'Shopping',
    'label_id': 'Label_3096048769747177215',
    'query': 'from:(/(me\.kickstarter\.com|email\@email\.etsy\.com)$/)'
  },
  {
    'label': 'Computing/Projects',
    'label_id': 'Label_6075144401056958575',
    'query': 'from:(/notifications\@github\.com$/)'
  },
  {
    'label': 'Computing/Forums',
    'label_id': 'Label_577614494869029147',
    'query': 'from:(/gitlab\@discoursemail\.com$/)'
  }
]

def get_service(account='client'):
  # Retrieve credentials from pickled token
  creds = None

  if account != 'service':
    if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
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
      with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
  
  else:
    # do service accounts not work???
    creds = service_account.Credentials.from_service_account_file(
      os.environ['GOOGLE_SERVICE_ACCT_FILE'], scopes=SCOPES
    ).with_subject('schrader.tristan@gmail.com')

  service = build('gmail', 'v1', credentials=creds)
  return service

def get_labels():
  service = get_service()
  labels = service.users().labels().list(userId='me').execute()
  with open('labels.json', 'w') as f:
    json.dump(labels, f, indent=4)
  #pprint(labels)

def process_new_emails(*args, **kwargs):
  service = get_service()

  def list_messages(query, token=None):
    params = {'userId': 'me', 'q': query, 'maxResults': MAX_RESULTS, 'labelIds': 'INBOX'}
    params = { 'newPageToken': token, **params } if token else params
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
        'nextPageToken': nextInbox['nextPageToken']
      }
    response = relabel_messages(inbox, group['label_id']) if 'messages' in inbox else {}
    responses['responses'].append(response)
  for label, response in zip([group['label'] for group in GROUPS], responses['responses']):
    print(f'Response ({label}):', response)
  return responses

if __name__ == '__main__':
  if sys.argv[1] == 'label':
    get_labels()
  elif sys.argv[1] == 'process':
    process_new_emails()
  else:
    print('Doing nothing')
  