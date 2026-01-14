#!/usr/bin/env python3
"""
Script d'aide pour configurer Google OAuth dans Zakat360
Ce script vous guide pour obtenir et configurer vos credentials Google OAuth.
"""

import os
import webbrowser
from pathlib import Path

def main():
    print("🔧 Configuration Google OAuth pour Zakat360")
    print("=" * 50)
    
    # Vérifier si le fichier .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé!")
        return
    
    print("\n📋 Étapes à suivre:")
    print("1. Ouvrir Google Cloud Console")
    print("2. Créer/sélectionner un projet")
    print("3. Configurer OAuth 2.0")
    print("4. Obtenir les credentials")
    print("5. Mettre à jour le fichier .env")
    
    # Demander si l'utilisateur veut ouvrir Google Cloud Console
    response = input("\n🌐 Voulez-vous ouvrir Google Cloud Console? (o/n): ").lower()
    if response in ['o', 'oui', 'y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/")
        print("✅ Google Cloud Console ouvert dans votre navigateur")
    
    print("\n📝 Instructions détaillées:")
    print("1. Dans Google Cloud Console:")
    print("   - Créez un nouveau projet ou sélectionnez un existant")
    print("   - Allez dans 'APIs et services' > 'Bibliothèque'")
    print("   - Activez 'Google+ API' ou 'People API'")
    
    print("\n2. Configurez OAuth 2.0:")
    print("   - Allez dans 'APIs et services' > 'Identifiants'")
    print("   - Cliquez 'Créer des identifiants' > 'ID client OAuth 2.0'")
    print("   - Configurez l'écran de consentement si nécessaire")
    
    print("\n3. Créez le client OAuth:")
    print("   - Type d'application: Application Web")
    print("   - URIs de redirection autorisées:")
    print("     * http://127.0.0.1:5000/callback/google")
    print("     * http://localhost:5000/callback/google")
    
    print("\n4. Copiez vos credentials:")
    
    # Demander les credentials
    print("\n🔑 Entrez vos credentials Google OAuth:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if client_id and client_secret:
        # Lire le fichier .env actuel
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les valeurs de démo
        content = content.replace(
            'GOOGLE_CLIENT_ID=demo-client-id.apps.googleusercontent.com',
            f'GOOGLE_CLIENT_ID={client_id}'
        )
        content = content.replace(
            'GOOGLE_CLIENT_SECRET=demo-client-secret',
            f'GOOGLE_CLIENT_SECRET={client_secret}'
        )
        
        # Écrire le fichier mis à jour
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier .env mis à jour avec succès!")
        print("\n🚀 Prochaines étapes:")
        print("1. Redémarrez l'application: python wsgi.py")
        print("2. Testez la connexion Google sur http://127.0.0.1:5000/auth/login")
        
    else:
        print("❌ Credentials non fournis. Veuillez les ajouter manuellement dans le fichier .env")
    
    print("\n📚 Pour plus d'aide, consultez: GOOGLE_OAUTH_SETUP.md")

if __name__ == "__main__":
    main()