import os
import logging
import base64
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import re


def format_record(uid, msg):
  """Formats a record for dataframe

  Args:
      uid (_type_): email uid
      msg (_type_): fetched message

  Returns:
      dict: record dictionary
  """  
  regex_str = r"^(.+) <([a-zA-Z0-9\-_]+@\w+\.\w+)>"
  record = {}
  try:
    record['UID'] = int(uid.decode())
  except Exception:
    record['UID'] = -1
  try:
    record['Date'] = msg['Date']
  except Exception:
    record['Date'] = pd.to_datetime(0, unit='s')
  try:
    record['From'] = re.sub(regex_str, r"\1", msg['From'])
  except Exception:
    record['From'] = None
  try:
    record['From_email'] = re.sub(regex_str, r"\2", msg['From'])
  except Exception:
    record['From_email'] = None
  try:
    record['To'] = re.sub(regex_str, r"\1", msg['To'])
  except Exception:
    record['To'] = None
  try:
    record['To_email'] = re.sub(regex_str, r"\2", msg['To'])
  except Exception:
    record['To_email'] = None
  try:
    try:
      subj = decode_header(msg['Subject'])[0][0].decode()
    except Exception:
      subj = decode_header(msg['Subject'])[0][0]
    record['Subject'] = subj
  except Exception:
    record['Subject'] = None
  try:
    record['Multipart'] = msg.is_multipart()
  except Exception:
    record['Multipart'] = False
  return record


def get_msg_by_uid(uid, imap):
  """gets message from imap connector

  Args:
      uid (_type_): email uid
      imap (_type_): imap connector

  Returns:
      dict: fully formatted record
  """  
  try:
    _, msg = imap.uid('fetch', uid, '(RFC822)')
    try:
      msg = email.message_from_bytes(msg[0][1])
    except Exception:
      pass
    record = format_record(uid, msg)
    try:
      size = int(
        re.sub(
          r".+RFC822\.SIZE (\d+)\)",
          r"\1",
          imap.uid('fetch', uid, '(RFC822.SIZE)')[1][0].decode()
          )
        )
    except Exception:
      size = -1
    record['Size'] = size
    if msg.is_multipart():
      payload = ''
      for part in msg.walk():
        if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
          try:
            payload += base64.b64decode(part.get_payload()).decode()
          except Exception:
            payload += 'multipart decoding error\n'
    else:
      payload = base64.b64decode(msg.get_payload()).decode()
    soup = BeautifulSoup(payload, 'html.parser')
    payload = soup.get_text()
    record['Payload'] = payload
  except Exception:
    record['UID'] = int(uid.decode())
    record['Payload'] = 'Unable to fetch message'
  return record


logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')
load_dotenv()
username = os.getenv('EMAIL_IMAP_USERNAME')
password = os.getenv('EMAIL_IMAP_PASSWORD')
host = os.getenv('EMAIL_IMAP_HOST')
port = os.getenv('EMAIL_IMAP_PORT')
has_ssl = os.getenv('EMAIL_IMAP_SSL')
folder = os.getenv('EMAIL_IMAP_FOLDER')
datapath = os.getenv('EMAILS_DATA_PATH')
try:
  has_ssl = bool(has_ssl)
except Exception:
  logging.warning('EMAIL_IMAP_SSL is misconfigured, please check.')
  
if has_ssl:
  imap = imaplib.IMAP4_SSL(host, port)
else:
  imap = imaplib.IMAP4(host, port)
imap.login(username, password)
imap.select(folder)

uids = imap.uid('search', 'UNSEEN')[1][0].split()
print(f"Fetching {len(uids)} unread messages")

df = pd.DataFrame(
  [get_msg_by_uid(uid, imap) for uid in uids]
)
try:
  da = pd.read_json(f"{datapath}/emails.json")
except Exception:
  df = pd.DataFrame()
pd.concat([df, da])
df.to_json(f"{datapath}/emails.json", orient='records', indent=2)
df.to_html(f"{datapath}/emails.xlsx")
