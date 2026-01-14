import sqlite3
import os

# Correct path per .env
db_path = os.path.join(os.getcwd(), 'zakat360/zakat360/zakat360_dev.db')
print(f"Connecting to database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

causes_data = [
    {
        'name': 'رعاية الأيتام',
        'name_fr': 'Soutien aux orphelins',
        'description': 'ندعم الأطفال الأيتام بتوفير التعليم والغذاء والرعاية الصحية.',
        'description_fr': 'Nous soutenons les enfants orphelins avec l’éducation, la nourriture et les soins.',
        'category': 'الطفولة',
        'category_fr': 'Enfance'
    },
    {
        'name': 'حفر الآبار',
        'name_fr': 'Forage de puits',
        'description': 'ننشئ آبار ماء صالحة للشرب في القرى الريفية لتحسين الوصول إلى المياه.',
        'description_fr': 'Nous construisons des puits d’eau potable dans les villages pour améliorer l’accès à l’eau.',
        'category': 'البنية التحتية',
        'category_fr': 'Infrastructure'
    },
    {
        'name': 'مساعدات غذائية عاجلة',
        'name_fr': 'Aides alimentaires urgentes',
        'description': 'نوفر وجبات وطرود غذائية للأسر المحتاجة.',
        'description_fr': 'Nous fournissons des repas et des colis alimentaires aux familles dans le besoin.',
        'category': 'طوارئ',
        'category_fr': 'Urgence'
    },
    {
        'name': 'التعليم للجميع',
        'name_fr': 'Éducation pour tous',
        'description': 'تمويل تعليم الأطفال المحرومين وبناء المدارس.',
        'description_fr': 'Financer l’éducation des enfants défavorisés et construire des écoles.',
        'category': 'التعليم',
        'category_fr': 'Éducation'
    },
    {
        'name': 'رعاية صحية مجانية',
        'name_fr': 'Soins de santé gratuits',
        'description': 'تقديم رعاية صحية وأدوية مجانية لغير القادرين.',
        'description_fr': 'Offrir des soins de santé et des médicaments gratuits aux personnes dans le besoin.',
        'category': 'الصحة',
        'category_fr': 'Santé'
    }
]

print("Updating French translations...")

for cause in causes_data:
    # Check if cause exists by Arabic name
    cursor.execute("SELECT id FROM causes WHERE name = ?", (cause['name'],))
    result = cursor.fetchone()
    
    if result:
        cause_id = result[0]
        print(f"Updating cause ID {cause_id} ({cause['name_fr']})...")
        cursor.execute("""
            UPDATE causes 
            SET name_fr = ?, description_fr = ?, category_fr = ?
            WHERE id = ?
        """, (cause['name_fr'], cause['description_fr'], cause['category_fr'], cause_id))
    else:
        print(f"Cause not found for: {cause['name']}")

conn.commit()
print("Update complete.")
conn.close()
