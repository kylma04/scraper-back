from flask import Flask, jsonify
from flask_cors import CORS  # Importer la bibliothèque CORS
from scraper.scraper import scrape_educarriere, scrape_linkedin

app = Flask(__name__)
CORS(app) #pour rendre cela dans toutes

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Exposer une API pour récupérer les jobs."""
    # Choisir quelle plateforme scraper
    educarriere_jobs = scrape_educarriere()
    # linkedin_jobs = scrape_linkedin()
    
    # Fusionner les deux listes de jobs
    # all_jobs = educarriere_jobs + linkedin_jobs
    all_jobs = educarriere_jobs
    
    # Retourner la réponse sous forme de JSON
    return jsonify(all_jobs)

if __name__ == "__main__":
    app.run(debug=True)
