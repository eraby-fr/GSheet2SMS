# GSheet2SMS
Tool to send sms thanks to ADB (Android 12) from Google Sheet

![Screenshot of the output of the tool](assets\images\img_bash.png)

# Use it
## Configure android ADB
In your phone, you have to :
- Enable developer mode
- Enable USB debugging
- Remove permission check on debugging

## Configuration to load Google Sheet
First run, the app will request credential from you

In the source code, you have to adapt:
- SAMPLE_SPREADSHEET_ID : must be extacted from document URL : https://docs.google.com/spreadsheets/d/[HERE IS THE ID]/edit
- SAMPLE_RANGE_NAME : depend which row/col you need to parse.