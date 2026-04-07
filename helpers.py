import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def extract_offer_info(html_content) -> pd.DataFrame:
    soup = BeautifulSoup(html_content, 'html.parser')
    offer_data = {}
    
    title_tag = soup.select_one('.r01gCabeceraTitle h2 span')
    if title_tag: offer_data['Título Oferta'] = title_tag.text.strip()
    
    status_tag = soup.find('div', id='r01gContentState')
    if status_tag: offer_data['Estado'] = status_tag.text.strip()
    
    date_tag = soup.select_one('.r01gContetnSateDate b')
    if date_tag: offer_data['Fechas'] = " ".join(date_tag.text.split())
    
    location_tag = soup.select_one('.r01gEventPlace')
    if location_tag: offer_data['Ubicación'] = " - ".join(location_tag.stripped_strings)
    
    sections = soup.find_all('div', class_='r01gContentTabSeccion')
    for sec in sections:
        title_div = sec.find('div', class_='r01gContentSeccionTitulo')
        text_div = sec.find('div', class_='r01gContentSeccionTexto')
        if title_div and text_div:
            column_name = title_div.text.replace(':', '').strip()
            if column_name == 'Electrónica':
                links = text_div.find_all('a', href=True)
                urls = [link['href'] for link in links if link['href']]
                value = ", ".join(urls) if urls else text_div.get_text(separator=" ", strip=True)
            else:
                value = text_div.get_text(separator=" ", strip=True)
            offer_data[column_name] = value
            
    return pd.DataFrame([offer_data])

def format_offer_for_telegram(df: pd.DataFrame) -> str:
    row = df.iloc[0]
    title = row.get('Título Oferta', 'Nueva Oferta')
    msg = f"📣 <b>{title}</b>\n\n"
    for col in df.columns:
        if col == 'Título Oferta': continue
        val = row[col]
        if pd.isna(val) or not str(val).strip(): continue
        msg += f"<b>{col}:</b> {val}\n\n"
    return msg

def send_telegram_msg(msg_text):
    # Set these in Azure Function App Settings / Environment Variables
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': msg_text, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
    requests.post(url, data=payload)