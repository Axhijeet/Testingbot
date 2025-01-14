import logging
import os
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from bs4 import BeautifulSoup
import pysrt
from io import BytesIO
import re
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7627790175:AAF7OmcCCxYxOwv5jl1dPEJDkCJb8AOMe2I"  # Replace with your actual bot token

def google_search(query):
    """Performs a Google search to find a subscene search page."""
    search_query = f"{query} site:subscene.com"
    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
    try:
      headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      }
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      soup = BeautifulSoup(response.content, 'html.parser')
      search_results = soup.find_all('a', href=True)
      
      for result in search_results:
          link = result.get('href')
          if link.startswith('https://subscene.com/subtitles/') and not link.endswith("#"):
               return link
      
      return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Google search error: {e}")
        return None
    
    except Exception as e:
       logger.error(f"Unexpected error while searching on Google: {e}")
       return None
    
def extract_subtitle_download_link(search_url):
    """Extracts the download link of the first subtitle in English from the subscene page."""
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        response = requests.get(search_url,headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first English subtitle row
        subtitle_rows = soup.find_all('tr')
        for row in subtitle_rows:
           lang_td = row.find("td", class_="language")
           if lang_td and lang_td.get_text(strip=True).lower() == "english":
                link_anchor = row.find("a", href=True)
                if link_anchor:
                    subtitle_page_url = "https://subscene.com" + link_anchor['href']
                    return subtitle_page_url
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Subscene page error: {e}")
        return None

    except Exception as e:
       logger.error(f"Unexpected error while extracting subtitle link: {e}")
       return None

def get_subtitle_download_link_from_subtitle_page(subtitle_page_url):
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
         }
        response = requests.get(subtitle_page_url,headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        download_link = soup.find('a', id='downloadButton', href=True)
        if download_link:
           return "https://subscene.com" + download_link['href']
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Subscene download page error: {e}")
        return None
    
    except Exception as e:
       logger.error(f"Unexpected error while extracting subtitle download link: {e}")
       return None
    
def download_subtitle(subtitle_link):
    try:
      headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
       }
      response = requests.get(subtitle_link, headers=headers)
      response.raise_for_status()
      subtitle_content = response.content
      return subtitle_content, None
    
    except requests.exceptions.RequestException as e:
            return None, f"Error downloading subtitle file: {e}"
    
    except Exception as e:
        return None, f"Unexpected error while downloading subtitle: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info(f"Received message: {text}")

    # Use Google to find the subscene URL
    subscene_search_url = google_search(text)

    if not subscene_search_url:
      await update.message.reply_text("No subscene search results found")
      return
    
    # Extract the subtitle link from subscene search page
    subtitle_page_url = extract_subtitle_download_link(subscene_search_url)
    if not subtitle_page_url:
         await update.message.reply_text("No English subtitle download found on the subscene page.")
         return

    # Get the actual subtitle download link
    download_link = get_subtitle_download_link_from_subtitle_page(subtitle_page_url)

    if not download_link:
       await update.message.reply_text("No subtitle download link found on subtitle page")
       return

    #Download the subtitle file
    subtitle_content, error = download_subtitle(download_link)

    if error:
         await update.message.reply_text(error)
         return

    
    # Check if subtitle file has content
    if not subtitle_content:
      await update.message.reply_text("Failed to retrieve subtitle content.")
      return
    
    # Convert byte content to file
    subtitle_file = BytesIO(subtitle_content)
    
    try:
        await context.bot.send_document(chat_id=update.message.chat_id, document=subtitle_file, filename=f"{text}.srt")
    except Exception as e:
          await update.message.reply_text(f"Error while sending subtitle file: {e}")
          return

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm a subtitle bot. Just send me the name of a movie or show and I'll try to find the English subtitles for you.")

def main():
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
        logger.error("Please provide a valid BOT_TOKEN.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
