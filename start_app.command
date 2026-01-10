#!/bin/bash
cd "$(dirname "$0")"
echo "Installation des dépendances..."
pip3 install -r requirements.txt
echo "Lancement de l'application..."
streamlit run app.py
