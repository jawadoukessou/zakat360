from zakat360 import create_app
from flask_babel import force_locale, gettext

app = create_app()

with app.app_context():
    with force_locale('ar'):
        translated = gettext('Calculateur de Zakat')
        print(f"Original: Calculateur de Zakat")
        print(f"Translated: {translated}")
        
        if translated == 'حاسبة الزكاة':
            print("SUCCESS: Translation is correct.")
        else:
            print("FAILURE: Translation is incorrect.")
