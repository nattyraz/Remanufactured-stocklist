from openai import OpenAI
import requests
import pdfplumber
import os
from typing import Dict, Any, Optional, List
import json

from src.config import OPENROUTER_CONFIG, SEARCH_CONFIG

class APIClient:
    def __init__(self):
        """Initialise les clients API."""
        self.openai_client = OpenAI(
            api_key=OPENROUTER_CONFIG["api_key"],
            base_url=OPENROUTER_CONFIG["base_url"]
        )

    def get_llm_response(self, prompt: str) -> str:
        """Obtient une réponse du LLM via OpenRouter."""
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENROUTER_CONFIG["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=OPENROUTER_CONFIG["max_tokens"]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur lors de l'appel à OpenRouter : {str(e)}"

    def search_lenovo_psref(self, query: str) -> Dict[str, Any]:
        """Recherche des documents Lenovo PSREF via SerpAPI."""
        try:
            # Utilisation directe de SerpAPI comme dans le code original
            params = {
                "q": f"site:psref.lenovo.com {query} filetype:pdf",
                "api_key": SEARCH_CONFIG["api_key"],
                "num": SEARCH_CONFIG["num_results"]
            }
            url = "https://serpapi.com/search"
            
            print(f"DEBUG: Recherche SerpAPI pour '{query}'")
            print(f"DEBUG: URL: {url}, Params: {params}")
            
            response = requests.get(url, params=params)
            
            print(f"DEBUG: Statut de la réponse: {response.status_code}")
            
            if response.status_code == 200:
                search_data = response.json()
                
                # Création du format de réponse attendu
                response_data = {
                    "success": True,
                    "data": search_data,
                    "message": ""
                }
            else:
                response_data = {
                    "success": False,
                    "data": None,
                    "message": f"Erreur SerpAPI: {response.status_code}"
                }
                
            return response_data
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Erreur lors de la recherche : {str(e)}"
            }

    def extract_pdf_text(self, pdf_url: str) -> str:
        """Extrait le texte d'un PDF à partir d'une URL."""
        try:
            # Télécharge le PDF
            response = requests.get(
                pdf_url, 
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code != 200:
                return f"Erreur lors du téléchargement du PDF : {response.status_code}"

            # Sauvegarde temporaire du PDF
            temp_pdf = "temp.pdf"
            with open(temp_pdf, "wb") as f:
                f.write(response.content)

            # Extraction du texte
            with pdfplumber.open(temp_pdf) as pdf:
                text = "".join(
                    page.extract_text() or "" 
                    for page in pdf.pages
                )

            # Nettoyage
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

            return text
        except Exception as e:
            return f"Erreur lors de l'extraction du PDF : {str(e)}"

    def process_lenovo_search(
        self, 
        query: str,
        search_mode: str
    ) -> Dict[str, Any]:
        """Traite une recherche Lenovo complète avec extraction détaillée des spécifications."""
        result = {
            "success": False,
            "data": None,
            "message": ""
        }

        # Recherche initiale
        search_results = self.search_lenovo_psref(query)
        if not search_results["success"]:
            return search_results

        # Traitement des résultats
        search_data = search_results["data"]
        if not search_data:
            return {
                "success": False,
                "data": None,
                "message": "Aucun résultat de recherche"
            }

        # Extraction des résultats organiques
        organic_results = search_data.get("organic_results", [])
        pdf_links = [
            result["link"]
            for result in organic_results
            if result["link"].endswith(".pdf")
        ]

        if not pdf_links:
            result["message"] = "Aucun PDF trouvé"
            result["data"] = {
                "results": [
                    {
                        "title": r["title"],
                        "snippet": r.get("snippet", "")
                    }
                    for r in organic_results
                ]
            }
            return result

        # Extraction et analyse du premier PDF
        pdf_url = pdf_links[0]
        pdf_text = self.extract_pdf_text(pdf_url)
        
        # Création d'un prompt plus détaillé pour le LLM
        llm_prompt = f"""
        Analyse ce texte PDF pour le modèle Lenovo '{query}' et extrait les spécifications techniques détaillées.
        
        Concentre-toi sur les informations suivantes:
        1. Processeur (modèle, génération, vitesse)
        2. Mémoire RAM (capacité, type, vitesse)
        3. Stockage (type, capacité)
        4. Écran (taille, résolution, technologie)
        5. Carte graphique
        6. Connectivité (ports, WiFi, Bluetooth)
        7. Batterie
        8. Système d'exploitation
        9. Dimensions et poids
        10. Autres caractéristiques importantes
        
        Format de réponse: Retourne un JSON avec les spécifications structurées comme ceci:
        [
            {{
                "category": "Processeur",
                "value": "Intel Core i7-1165G7, 11ème génération, 2.8 GHz (jusqu'à 4.7 GHz)"
            }},
            {{
                "category": "Mémoire RAM",
                "value": "16 Go DDR4 3200 MHz"
            }},
            ...
        ]
        
        Voici le texte du PDF:
        {pdf_text[:5000]}...
        """
        
        # Mode de recherche: ajuster le prompt en fonction du mode
        if search_mode == "Focus sur le détail":
            llm_prompt += "\nConcentre-toi sur les détails techniques précis et les numéros de modèle exacts."
        else:  # Mode "Général"
            llm_prompt += "\nFournis une vue d'ensemble des spécifications principales sans trop de détails techniques."
        
        # Obtention de la réponse du LLM
        llm_response = self.get_llm_response(llm_prompt).strip()

        try:
            # Tentative de parsing JSON
            results_json = json.loads(llm_response)
            if isinstance(results_json, list) and results_json:
                result["success"] = True
                result["data"] = {
                    "pdf_url": pdf_url,
                    "results": results_json,
                    "mode": search_mode,
                    "model": query
                }
            else:
                result["message"] = f"Aucune donnée structurée trouvée pour '{query}'"
                result["data"] = {"raw_response": llm_response}
        except json.JSONDecodeError as e:
            # Si le parsing JSON échoue, essayons d'extraire un JSON valide de la réponse
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', llm_response, re.DOTALL)
            
            if json_match:
                try:
                    extracted_json = json.loads(json_match.group(0))
                    result["success"] = True
                    result["data"] = {
                        "pdf_url": pdf_url,
                        "results": extracted_json,
                        "mode": search_mode,
                        "model": query
                    }
                except:
                    result["message"] = f"Erreur de parsing JSON : {str(e)}"
                    result["data"] = {"raw_response": llm_response}
            else:
                # Créer un JSON structuré à partir du texte brut
                lines = llm_response.split('\n')
                structured_results = []
                
                current_category = None
                current_value = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Détection d'une nouvelle catégorie
                    if ':' in line and len(line.split(':')[0]) < 30:
                        # Sauvegarder la catégorie précédente si elle existe
                        if current_category and current_value:
                            structured_results.append({
                                "category": current_category,
                                "value": ' '.join(current_value)
                            })
                            
                        parts = line.split(':', 1)
                        current_category = parts[0].strip()
                        current_value = [parts[1].strip()] if len(parts) > 1 else []
                    else:
                        if current_category:
                            current_value.append(line)
                
                # Ajouter la dernière catégorie
                if current_category and current_value:
                    structured_results.append({
                        "category": current_category,
                        "value": ' '.join(current_value)
                    })
                
                if structured_results:
                    result["success"] = True
                    result["data"] = {
                        "pdf_url": pdf_url,
                        "results": structured_results,
                        "mode": search_mode,
                        "model": query
                    }
                else:
                    result["message"] = f"Impossible de structurer la réponse pour '{query}'"
                    result["data"] = {"raw_response": llm_response}

        return result