import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import pickle

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    logger.debug("Starting Gmail service initialization")
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        logger.debug("Found existing token.pickle file")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            logger.debug("Loaded credentials from token.pickle")
    else:
        logger.debug("No token.pickle file found")
    
    # If credentials are not valid or don't exist
    if not creds or not creds.valid:
        logger.debug("Credentials are invalid or missing")
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            logger.debug("Initiating OAuth2 flow")
            if not os.path.exists('credentials.json'):
                logger.error("credentials.json file not found!")
                raise FileNotFoundError("credentials.json is required for Gmail authentication")
            
            # Configure the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 
                SCOPES,
                redirect_uri='http://ccrbraga.ddns.net'  # Production redirect URI
            )
            
            # For local development, uncomment this line and comment the production one above
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     'credentials.json', 
            #     SCOPES,
            #     redirect_uri='http://localhost:8080'
            # )
            
            creds = flow.run_local_server(
                port=8080,
                success_message='The authentication flow has completed. You may close this window.',
                open_browser=True
            )
            logger.debug("OAuth2 flow completed successfully")
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            logger.debug("Saved new credentials to token.pickle")

    logger.debug("Gmail service initialization completed")
    return build('gmail', 'v1', credentials=creds)

def send_completion_email(to_email, video_url):
    try:
        logger.debug(f"Preparing to send email to: {to_email}")
        logger.debug(f"Video URL to be included: {video_url}")
        
        service = get_gmail_service()
        logger.debug("Gmail service obtained successfully")
        
        # Prepare email content
        email_body = f'''
        Olá!

        O processamento do seu vídeo foi concluído com sucesso!
        URL do vídeo: {video_url}

        Você já pode acessar os resultados no sistema.

        Atenciosamente,
        Sistema CCR
        '''
        
        message = MIMEText(email_body)
        message['to'] = to_email
        message['subject'] = 'Processamento de Vídeo Concluído'
        logger.debug("Email message created with subject and recipient")
        
        # Encode the message
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        logger.debug("Email message encoded successfully")
        
        # Send the email
        logger.debug("Attempting to send email...")
        send_result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        logger.debug(f"Email sent successfully. Message ID: {send_result.get('id', 'unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return False

# Add a test function for debugging
def test_email_sending(test_email):
    """
    Test function to verify email sending functionality
    Usage: test_email_sending("your.email@example.com")
    """
    logger.info(f"Starting email sending test to: {test_email}")
    
    test_video_url = "https://example.com/test-video"
    logger.debug("Using test video URL: " + test_video_url)
    
    result = send_completion_email(test_email, test_video_url)
    
    if result:
        logger.info("Test email sent successfully!")
    else:
        logger.error("Failed to send test email")
    
    return result
