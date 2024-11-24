import requests
from bs4 import BeautifulSoup
import csv
import urllib3
import time
import random

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Headers et cookies pour LinkedIn
HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
  ),
  "Accept-Language": "en-US,en;q=0.9",
}

COOKIES ={"AQEDAUute3kAWFQLAAABk1u3gvUAAAGTf8QG9U0AaqFPiht3MM_7YcOgabQARb0QdcTEjbeIR_25yNNUGhuoLA92CNX94VdjT1Dbmw8ehitGlYVF0Rg-1yWen8Y3_V9qcYL9T9qpXc6BztYRFA6Shn3h"}

# Créer une session pour améliorer les performances des requêtes HTTP
session = requests.Session()
session.headers.update(HEADERS)

def fetch_page(url, verify_ssl=False):
  """Récupère le contenu d'une page et gère les erreurs."""
  try:
    response = session.get(url, verify=verify_ssl)
    response.raise_for_status()  # Vérifier si la requête a échoué
    return response.text
  except requests.exceptions.RequestException as e:
    print(f"❌ Erreur lors de la requête HTTP : {e}")
    return None

def extract_job_info(job, platform="Educarriere"):
  """Extrait les informations des offres d'emploi, adaptable pour différentes plateformes."""
  job_info = {}

  if platform == "Educarriere":
    title_tag = job.find("h4", class_="post-title").find("a")
    job_info["title"] = title_tag.text.strip() if title_tag else "Titre non spécifié"
    job_info["link"] = title_tag["href"] if title_tag else "Lien non spécifié"
    
    code_tag = job.find("li", string=lambda t: t and "Code:" in t)
    job_info["code"] = code_tag.find("span").text.strip() if code_tag else "Code non spécifié"

    date_edition_tag = job.find("li", string=lambda t: t and "Date d'édition:" in t)
    job_info["date_edition"] = date_edition_tag.find("span").text.strip() if date_edition_tag else "Non spécifiée"

    date_limite_tag = job.find("li", string=lambda t: t and "Date limite:" in t)
    job_info["date_limite"] = date_limite_tag.find("span").text.strip() if date_limite_tag else "Non spécifiée"

    job_info["source"] = "Educarriere"

  elif platform == "LinkedIn":
    title_tag = job.find("h3", class_="base-search-card__title")
    job_info["title"] = title_tag.text.strip() if title_tag else "Titre non spécifié"

    company_tag = job.find("h4", class_="base-search-card__subtitle")
    job_info["company"] = company_tag.text.strip() if company_tag else "Entreprise non spécifiée"

    location_tag = job.find("span", class_="job-search-card__location")
    job_info["location"] = location_tag.text.strip() if location_tag else "Localisation non spécifiée"

    link_tag = job.find("a", class_="base-card__full-link")
    job_info["link"] = link_tag["href"] if link_tag else "Lien non spécifié"

    job_info["source"] = "LinkedIn"

  return job_info

def scrape_educarriere():
  print("🔍 Recherche sur Educarriere...")
  base_url = "https://emploi.educarriere.ci/emploi/page/all"
  jobs = []

  page_content = fetch_page(base_url, verify_ssl=False)
  if page_content:
    soup = BeautifulSoup(page_content, "html.parser")
    job_listings = soup.find_all("div", class_="rt-post post-md style-8")
    
    for job in job_listings:
      job_info = extract_job_info(job, platform="Educarriere")
      jobs.append(job_info)

  return jobs

def scrape_linkedin():
  print("🔍 Recherche sur LinkedIn...")
  base_url = "https://www.linkedin.com/jobs/search?keywords=emploi"
  jobs = []

  page_content = fetch_page(base_url, verify_ssl=False)
  if page_content:
    soup = BeautifulSoup(page_content, "html.parser")
    job_listings = soup.find_all("div", class_="base-search-card__info")
    
    for job in job_listings:
      job_info = extract_job_info(job, platform="LinkedIn")
      jobs.append(job_info)
      
  # Ajouter un délai aléatoire après chaque requête
  time.sleep(random.uniform(15, 30))  # Attendre entre 3 et 10 secondes

  return jobs

def save_to_csv(jobs, filename):
    """Sauvegarde la liste des jobs dans un fichier CSV."""
    if jobs:
        # Générer dynamiquement les noms de champs à partir des clés des jobs
        keys = set()
        for job in jobs:
            keys.update(job.keys())  # Ajouter toutes les clés présentes dans le job
        keys = list(keys)  # Convertir en liste

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(jobs)
        print(f"✅ {len(jobs)} offres d'emploi sauvegardées dans le fichier : {filename}")
    else:
        print("❌ Aucun emploi trouvé pour sauvegarde.")


def main():
  print("📋 Bienvenue dans le récupérateur d'offres d'emploi !\n")
  choice = ""
  
  while choice not in ["1", "2", "a"]:
    choice = input("📋 Veuillez choisir : \n (1) :  Pour les offres educarrieres \n (2) :  Pour les offres linkedin \n (a) :  Pour les deux \n")

  # Scraping des différentes plateformes
  educarriere_jobs = scrape_educarriere() if choice in ["1", "a"] else []
  
  # Ajouter un délai pour éviter le code HTTP 429 de LinkedIn
  linkedin_jobs = []
  if choice in ["2", "a"]:
    time.sleep(5)  # Attendre 2 secondes avant de scrapper LinkedIn a cause du temps de reponse qui m'affiche des erreurress
    linkedin_jobs = scrape_linkedin()

  # Fusionner les données
  all_jobs = educarriere_jobs + linkedin_jobs

  # Sauvegarder les données dans un fichier CSV
  save_to_csv(all_jobs, "jobs_combined.csv")

if __name__ == "__main__":
  main()
