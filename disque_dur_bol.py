from lxml import html
from tqdm import tqdm
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# Fonction pour scraper les données d'une page
def scrape_product_page(url):
    # Initialiser le navigateur Selenium
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Mode headless (facultatif)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection d'automatisation
    options.add_argument("--no-sandbox")  # Utile pour GitHub Actions
    options.add_argument("--disable-dev-shm-usage")  # Évite les erreurs de mémoire partagée
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    html_content = driver.page_source
    # print(html_content)
    driver.quit()  # Fermer le navigateur après avoir obtenu le contenu

    # Parser le contenu HTML avec lxml
    tree = html.fromstring(html_content)

    # Initialiser un dictionnaire pour stocker les données
    general_data = {}

    # Liste des clés statiques à rechercher
    static_keys = [
        "Nom du produit",
        "Catégorie",
        "Prix",
        "Site web",
        "Marque",
        "Référence",
        "Capacité",
        "Type de disque",
    ]

    general_data['Nom du produit'] = tree.xpath("//*[@id='product_title']/h1/span/text()")[0].strip() if tree.xpath("//*[@id='product_title']/h1/span") else None
    
    
    general_data['Marque'] = tree.xpath("//div[dt[contains(text(),'Marque')]]/dd/a/text()")[0].strip() if tree.xpath("//div[dt[contains(text(),'Marque')]]/dd/a/text()") else None
    general_data["Capacité"] = tree.xpath("//div[dt[contains(text(),'Capacité de stockage')]]/dd/text()")[0].strip() if tree.xpath("//div[dt[contains(text(),'Capacité de stockage')]]/dd/text()") else None
    general_data['Référence'] = tree.xpath("//div[dt[contains(text(),'NPP (numéro de pièce du fabricant)')]]/dd/text()")[0].strip() if tree.xpath("//div[dt[contains(text(),'NPP (numéro de pièce du fabricant)')]]/dd/text()") else None
    general_data["Type de disque"] = tree.xpath("//div[dt[contains(text(),'Type de disque dur')]]/dd/text()")[0].strip() if tree.xpath("//div[dt[contains(text(),'Type de disque dur')]]/dd/text()") else None
        
    general_data['Prix'] = tree.xpath("//span[@class='promo-price']/text()")[0].strip() if tree.xpath("//span[@class='promo-price']/text()") else np.nan
    general_data['Site web'] = "bol.com"
    general_data['Catégorie'] = "DISQUE DUR"

    # Vérifier si une valeur est vide ou None, et la remplir par np.nan
    for key in static_keys:
        if not general_data.get(key):
            general_data[key] = np.nan
    time.sleep(20)
    return general_data

# Fonction principale pour lire les liens, scraper les données et sauvegarder les résultats
def scrape_and_save(input_csv, output_csv):
    # Lire les liens depuis le fichier CSV
    df_links = pd.read_csv(input_csv)
    links = df_links['Disque_dur'].tolist()  # Supposons que la colonne s'appelle "lien"

    # Initialiser une liste pour stocker les données de tous les produits
    all_data = []

    # Scraper chaque lien
    for link in tqdm(links, desc="Scraping progress"):
        # print(f"Scraping {link}...")
        try:
            product_data = scrape_product_page(link)
            all_data.append(product_data)

        except Exception as e:
            print(f"Erreur lors du scraping de {link}: {e}")

    # Convertir la liste de dictionnaires en DataFrame
    df_results = pd.DataFrame(all_data)

    # Sauvegarder les résultats dans un fichier CSV
    df_results.to_csv(output_csv, index=False)
    print(f"Les résultats ont été sauvegardés dans {output_csv}")

today_date = datetime.today().strftime('%Y-%m-%d')

input_csv = f"Links/Bol_Liens_{today_date}.csv"
output_csv = f"Data/Disque_dur_Data_Bol_{today_date}.csv"
scrape_and_save(input_csv, output_csv)
