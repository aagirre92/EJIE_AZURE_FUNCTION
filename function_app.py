import os
import traceback
import logging
import requests
from bs4 import BeautifulSoup
import azure.functions as func
from helpers import extract_offer_info, format_offer_for_telegram, send_telegram_msg

app = func.FunctionApp()

# Run on startup true para testear...
@app.timer_trigger(schedule="%TIMER_SCHEDULE%", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')
        
    base_url = os.environ.get("BASE_URL", "https://www.ejie.euskadi.eus/")
    url = f"{base_url}webejie00-contqtit/es/?r01kPageContents=/webejie00-contqtit/es/&r01kPresentationThumbnail=miniatura-3&r01kQry=tC:euskadi;tF:rrhh;tT:empleo_publico;m:documentLanguage.EQ.es;cO:r01epd012cab7c3b2513bab5f2d1fd16f8b777a71;pp:r01PageSize.50&r01kSearchResultsHeader=1;p:Inter;"
    
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        job_items = soup.find_all('li', class_='r01srItem')

        for item in job_items:
            status_span = item.find('span', class_='r01srItemTypo_empleo_publico_abierto')
            if status_span:
                title_tag = item.find('em', class_='r01srItemDocName').find('a')
                link = title_tag['href']
                
                # Process Detail
                detail_url = base_url.strip("/") + link
                detail_resp = requests.get(detail_url)
                df = extract_offer_info(detail_resp.text)
                
                # Send to Telegram
                send_telegram_msg(format_offer_for_telegram(df))
                
        logging.info("Execution finished successfully.")
    except Exception as e:
        logging.error(f"Error during execution: {e}")
        send_telegram_msg(f"⚠️ Error in Azure Function: {e}")
        traceback.print_exc()
    logging.info('Python timer trigger function executed.')