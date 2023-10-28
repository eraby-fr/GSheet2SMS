from __future__ import print_function

import os.path
import logging
import datetime
import subprocess
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1S15akfuN49XjfhbhL27W8_QoeGZQk8-hj5uKvW3Z8NI' #Test SMS
SAMPLE_RANGE_NAME = 'synthèse des commandes!E3:J255'

def google_login():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def isInCurrentWeek(date_string):
    current_day = datetime.date.today().weekday() #(0 = lundi, 6 = dimanche)

    # Compute start/end date of the week
    start_week = datetime.date.today() - datetime.timedelta(days=current_day)
    end_week = start_week + datetime.timedelta(days=6)
    
    date_format = "%d/%m/%Y"
    date = datetime.datetime.strptime(date_string, date_format).date()

    return start_week <= date <= end_week

def sendSms(person, number, collect_date, code):
    message=str(f"Bonjour, votre commande raclette APE Saint Agathon est à retirer à FromEpiFruit le {collect_date}. Votre code:{code}.")
    message = message.replace(" ", "\\ ")

    cmd = f"adb shell service call isms 5 i32 1 s16 \"com.android.mms\" s16 \"null\" s16 \"{number}\" s16 \"null\" s16 \"{message}\" s16 \"null\" s16 \"null\" i32 0 i64 0"
    logging.debug(f"Subprocess run : {cmd}")
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if not result.returncode == 0:
        logging.error(f"Issue on sms for {number} : {result.stderr}")
    else:
        logging.debug(f"{number} : {result.stdout}")
    
    return result.returncode == 0

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    creds = google_login()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            logging.critical('No value from sheet : exit')
        
        listOfSucces = []
        listOfFail = []

        for row in values:
            collect_date=row[5]
            if isInCurrentWeek(collect_date):
                person=str(f"{row[0]} {row[1]}")
                number=row[2].replace(" ", "")
                code=row[3]
                if sendSms(person, number, collect_date, code):
                    listOfSucces.append(number)
                else:
                    listOfFail.append(number)
                time.sleep(3)


        logging.info(f"End of process {len(listOfSucces)} SMS sent succesfully. {len(listOfFail)} SMS sent failled")
        if len(listOfFail) > 0:
            print(" ")
            logging.warning(f"List of sent failled :")
            logging.warning(listOfFail)
        if len(listOfSucces) > 0:
            print(" ")
            logging.debug(f"List of sent ok :")
            logging.debug(listOfSucces)


    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()