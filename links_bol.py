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

# Configuration de Selenium
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Mode headless (facultatif)
options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection d'automatisation
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)

# Liste pour stocker les href
hrefs = []

# Nombre total de href à scraper
target_hrefs = 500

# Page initiale
page = 1

categories = {
    "Smartphone": "smartphone",
    "Ordinateur": "ordinateur+portable",
    "Moniteur": "moniteur",
    "Disque_dur": "disque+dur"
}
df = pd.DataFrame()

def scrape_hrefs(request, target_hrefs):
    hrefs = []
    page = 1 
    while len(hrefs) < target_hrefs:
        # Ouvrir la page
        url = f"https://www.cdiscount.com/search/10/{request}.html?&page={page}"
        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(1)
        # Attendre que les éléments soient chargés
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lpBloc > li.abLabel > div > div > form > div.prdtBILDetails > a"))
            )
        except Exception as e:
            print(f"Erreur lors du chargement de la page {page}: {e}")
            break
    
        # Trouver tous les éléments correspondant au sélecteur CSS
        elements = driver.find_elements(By.CSS_SELECTOR, "#lpBloc > li.abLabel > div > div > form > div.prdtBILDetails > a")
        # Extraire les attributs href
        for element in elements:
            href = element.get_attribute("href")
            if href and href not in hrefs:  # Éviter les doublons
                hrefs.append(href)
                if len(hrefs) >= target_hrefs:
                    break
        try:
            next_button = driver.find_element(By.XPATH, "//div[@class='pgLightPrevNext']/input[@value='Page suivante']")
        except NoSuchElementException:
            print("Bouton suivant introuvable. Arrêt du scraping.")
            break
    
        # Passer à la page suivante
        page += 1

        # Attendre avant de charger la page suivante (pour éviter de surcharger le serveur)
        time.sleep(3)
    time.sleep(6)
    return hrefs


# Scraper toutes les catégories et stocker les résultats dans le DataFrame
for category, request in categories.items():
    print(f"Scraping {category}...")
    hrefs = scrape_hrefs(request, target_hrefs)
    df[category] = pd.Series(hrefs)  # Ajouter les liens dans la colonne correspondante
    df.to_csv(f"{category}_Hrefs.csv", index=False)  # Sauvegarde individuelle pour chaque catégorie
    print(f"{len(hrefs)} liens trouvés pour {category}.")

today_date = datetime.today().strftime('%Y-%m-%d')

df.to_csv(f"Links/Cdiscount_Liens_{today_date}.csv", index=False)
print("Scraping terminé, toutes les catégories enregistrées.")

driver.quit()
