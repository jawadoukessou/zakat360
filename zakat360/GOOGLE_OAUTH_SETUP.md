# Configuration Google OAuth pour Zakat360

## Étapes pour configurer Google OAuth

### 1. Créer un projet Google Cloud
1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Notez l'ID de votre projet

### 2. Activer les APIs nécessaires
1. Dans le menu de navigation, allez à **APIs & Services** > **Library**
2. Recherchez et activez les APIs suivantes :
   - **Google+ API** (ou People API)
   - **Google OAuth2 API**

### 3. Créer les credentials OAuth 2.0
1. Allez à **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **OAuth 2.0 Client IDs**
3. Si c'est votre première fois, configurez l'écran de consentement OAuth :
   - Choisissez **External** pour les tests
   - Remplissez les champs obligatoires (nom de l'app, email de support)
   - Ajoutez votre email dans les utilisateurs de test

### 4. Configurer le client OAuth
1. Sélectionnez **Web application** comme type d'application
2. Donnez un nom à votre client (ex: "Zakat360 Local Dev")
3. Dans **Authorized redirect URIs**, ajoutez :
   ```
   http://127.0.0.1:5000/callback/google
   http://localhost:5000/callback/google
   ```

### 5. Récupérer les credentials
1. Une fois créé, copiez le **Client ID** et **Client Secret**
2. Ouvrez le fichier `.env` dans le projet
3. Remplacez les valeurs de démo :
   ```env
   GOOGLE_CLIENT_ID=votre-client-id-ici.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=votre-client-secret-ici
   ```

### 6. Redémarrer l'application
1. Arrêtez le serveur Flask (Ctrl+C)
2. Relancez avec `python wsgi.py`
3. Le bouton Google OAuth devrait maintenant fonctionner

## Test de l'authentification
1. Allez sur la page de connexion
2. Cliquez sur "Se connecter avec Google"
3. Vous devriez être redirigé vers Google pour l'authentification
4. Après autorisation, vous serez redirigé vers l'application et connecté automatiquement

## Dépannage
- **Erreur "redirect_uri_mismatch"** : Vérifiez que l'URI de redirection dans Google Cloud correspond exactement à celle utilisée par l'app
- **Erreur "access_blocked"** : Ajoutez votre email dans les utilisateurs de test de l'écran de consentement
- **Erreur "invalid_client"** : Vérifiez que le Client ID et Client Secret sont corrects dans le fichier `.env`

## Mode Production
Pour la production, vous devrez :
1. Configurer un domaine personnalisé
2. Mettre à jour les URIs de redirection
3. Publier l'application OAuth (sortir du mode test)
4. Utiliser des variables d'environnement sécurisées