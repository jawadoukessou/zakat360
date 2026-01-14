# 🚀 Guide Rapide - Activer Google OAuth

## ⚡ Solution Rapide (5 minutes)

### 1. Exécuter le script d'aide
```bash
python setup_google_oauth.py
```
Ce script vous guidera étape par étape !

### 2. Configuration manuelle

#### A. Créer un projet Google Cloud
1. 🌐 Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. ➕ Créez un nouveau projet (ou sélectionnez un existant)
3. 📝 Notez le nom de votre projet

#### B. Activer les APIs
1. 📚 Menu → **APIs et services** → **Bibliothèque**
2. 🔍 Recherchez et activez : **Google+ API** (ou People API)

#### C. Configurer OAuth 2.0
1. 🔑 **APIs et services** → **Identifiants**
2. ➕ **Créer des identifiants** → **ID client OAuth 2.0**
3. ⚙️ Configurez l'écran de consentement si demandé :
   - Type : **External**
   - Nom de l'application : **Zakat360**
   - Email de support : votre email

#### D. Créer le client OAuth
1. 🖥️ Type d'application : **Application Web**
2. 📝 Nom : **Zakat360 Local Dev**
3. 🔗 **URIs de redirection autorisées** (ajoutez les deux) :
   ```
   http://127.0.0.1:5000/callback/google
   http://localhost:5000/callback/google
   ```

#### E. Récupérer les credentials
1. 📋 Copiez le **Client ID** (format: `123456-abc...apps.googleusercontent.com`)
2. 📋 Copiez le **Client Secret** (format: `GOCSPX-abc...xyz`)

#### F. Mettre à jour le fichier .env
1. 📝 Ouvrez le fichier `.env`
2. 🔄 Remplacez les lignes :
   ```env
   GOOGLE_CLIENT_ID=votre-client-id-ici
   GOOGLE_CLIENT_SECRET=votre-client-secret-ici
   ```

#### G. Redémarrer l'application
1. ⏹️ Arrêtez le serveur (Ctrl+C)
2. ▶️ Relancez : `python wsgi.py`
3. 🌐 Testez sur : http://127.0.0.1:5000/auth/login

## ✅ Test de fonctionnement

1. 🌐 Allez sur la page de connexion
2. 🔘 Cliquez sur **"Se connecter avec Google"**
3. 🔐 Vous devriez être redirigé vers Google
4. ✅ Après autorisation, retour automatique vers l'app

## 🆘 Dépannage

### Erreur "redirect_uri_mismatch"
- ✅ Vérifiez que les URIs dans Google Cloud correspondent exactement
- ✅ Utilisez `http://127.0.0.1:5000` au lieu de `localhost` si problème

### Erreur "access_blocked"
- ✅ Ajoutez votre email dans les utilisateurs de test
- ✅ Vérifiez que l'écran de consentement est configuré

### Erreur "invalid_client"
- ✅ Vérifiez le Client ID et Client Secret dans `.env`
- ✅ Pas d'espaces avant/après les valeurs

## 📞 Besoin d'aide ?

- 📖 Guide détaillé : `GOOGLE_OAUTH_SETUP.md`
- 🤖 Script automatique : `python setup_google_oauth.py`
- 🔧 Configuration actuelle visible dans le message d'alerte de l'app