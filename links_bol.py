import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import random
import os

# Configuration de Selenium
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Mode headless (facultatif)
options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection d'automatisation
options.add_argument("--no-sandbox")  # Utile pour GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # Évite les erreurs de mémoire partagée
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(5)

# Liste pour stocker les href
hrefs = []

# Nombre total de href à scraper
target_hrefs = 500

# Page initiale
page = 1

categories = {
    "Smartphone": "smartphones/4010",
    "Ordinateur": "ordinateurs-portables/4770",
    "Moniteur": "moniteurs/10460",
    "Disque_dur": "disques-durs/38835"
}
df = pd.DataFrame()

def scrape_hrefs(request, target_hrefs):
    hrefs = []
    page = 1 
    retries = 3  # Nombre d'essais en cas d'erreur

    while len(hrefs) < target_hrefs:
        # Ouvrir la page
        url = f"https://www.bol.com/nl/fr/l/{request}/?page={page}"
        driver.get(url)
        time.sleep(1)
        # Attendre que les éléments soient chargés
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@id='js_items_content']/li/div[2]/div/div[1]/wsp-analytics-tracking-event/a"))
            )
        except (TimeoutException, Exception) as e:
            print(f"Erreur lors du chargement de la page {page} pour {request}: {e}")
            if retries > 0:
                print(f"Tentative de rechargement ({retries} essais restants)...")
                retries -= 1
                time.sleep(random.uniform(3, 6))
                continue  
            else:
                print(f"Passage forcé à la page suivante après plusieurs échecs ({page}).")
                page += 1
                retries = 3  # Réinitialiser pour la page suivante
                continue  
            ########################
    
        # Trouver tous les éléments correspondant au sélecteur CSS
        elements = driver.find_elements(By.XPATH, "//*[@id='js_items_content']/li/div[2]/div/div[1]/wsp-analytics-tracking-event/a") 
        # Extraire les attributs href
        for element in elements:
            href = element.get_attribute("href")
            if href and href not in hrefs:  # Éviter les doublons
                hrefs.append(href)
                if len(hrefs) >= target_hrefs:
                    break
        try:
            next_button = driver.find_element(By.XPATH, "//*[@id='js_pagination_control']/nav/ul/li/a[@aria-label='suivant']")
        except NoSuchElementException:
            print("Bouton suivant introuvable. Arrêt du scraping.")
            break
    
        # Passer à la page suivante
        page += 1

        # Attendre avant de charger la page suivante (pour éviter de surcharger le serveur)
        time.sleep(random.uniform(3, 6))
    time.sleep(random.uniform(3, 6))
    return hrefs


# Scraper chaque catégorie et sauvegarder séparément
today_date = datetime.today().strftime('%Y-%m-%d')

for category, request in categories.items():
    print(f"Scraping {category}...")
    hrefs = scrape_hrefs(request, target_hrefs)

    if hrefs:
        df = pd.DataFrame(hrefs, columns=["Lien"])
        filename = f"Links/Bol_Liens_{category}_{today_date}.csv"
        df.to_csv(filename, index=False)
        print(f"{len(hrefs)} liens sauvegardés dans {filename}.")
    else:
        print(f"Aucun lien trouvé pour {category}.")

# Fermer Selenium
driver.quit()
print("Scraping terminé pour toutes les catégories.")
