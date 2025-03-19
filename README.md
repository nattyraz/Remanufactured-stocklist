# Stockliste

Application de gestion de stock avec interface Streamlit, permettant de gérer et filtrer rapidement les stocks de produits remanufacturés.

![Logo](static/rf.logo.png)

## 🚀 Fonctionnalités

- 📊 Visualisation et filtrage des stocks en temps réel
- 🔍 Recherche avancée avec support des wildcards (*)
- 💰 Support multi-devises (EUR, DKK, GBP)
- 📱 Interface responsive et conviviale
- 📑 Export des données filtrées en Excel
- 🔎 Recherche intelligente Lenovo PSREF avec extraction PDF
- 👤 Système d'authentification admin
- 📈 Statistiques de stock en temps réel

## 🛠️ Installation

1. Clonez le repository :
```bash
git clone https://github.com/nattyraz/Remanufactured-stocklist.git
cd Remanufactured-stocklist
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement dans config.toml :
- Admin credentials
- OpenRouter API key
- SerpAPI key

## 📦 Dépendances

- streamlit - Interface utilisateur
- pandas - Manipulation des données
- openpyxl - Export Excel
- plotly - Visualisations (préparé pour futures fonctionnalités)
- matplotlib - Graphiques (préparé pour futures fonctionnalités)
- numpy - Calculs numériques
- openai - Intégration IA via OpenRouter
- geopy - Géolocalisation (préparé pour futures fonctionnalités)
- requests - Requêtes HTTP
- serpapi - Recherche Lenovo PSREF
- pdfplumber - Extraction de texte PDF
- pyarrow - Support format Parquet

## 🚦 Utilisation

1. Lancez l'application :
```bash
streamlit run appv3.py
```

2. Accédez à l'interface via votre navigateur (par défaut : http://localhost:8501)

3. Fonctionnalités utilisateur :
   - Filtrage par marque, catégorie, format, clavier et condition
   - Recherche textuelle avec wildcards
   - Sélection de la devise
   - Export des résultats en Excel
   - Recherche documentaire Lenovo

4. Fonctionnalités admin (nécessite authentification) :
   - Import de nouvelles données de stock
   - Mise à jour des données existantes

## 🔐 Sécurité

Les credentials admin et les clés API sont gérés de manière sécurisée via les secrets Streamlit.

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.