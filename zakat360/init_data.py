#!/usr/bin/env python3
"""
Script d'initialisation des données de base pour Zakat360
"""

import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour importer zakat360
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zakat360 import create_app
from zakat360.extensions import db
from zakat360.models import Cause, Donation, User
from werkzeug.security import generate_password_hash

def init_sample_data():
    """Initialise la base de données avec des données d'exemple"""
    
    app = create_app()
    
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
        # Vérifier si des causes existent déjà
        if Cause.query.first():
            print("Des données existent déjà. Suppression et recréation...")
            # Supprimer toutes les données existantes
            Donation.query.delete()
            Cause.query.delete()
            User.query.delete()
            db.session.commit()
        
        # Créer des causes d'exemple en arabe et en français
        causes = [
            {
                'name': 'رعاية الأيتام',
                'name_fr': 'Soutien aux orphelins',
                'description': 'ندعم الأطفال الأيتام بتوفير التعليم والغذاء والرعاية الصحية.',
                'description_fr': 'Nous soutenons les enfants orphelins avec l’éducation, la nourriture et les soins.',
                'category': 'الطفولة',
                'category_fr': 'Enfance',
                'target_amount': 50000.0,
                'raised_amount': 12500.0,
                'is_active': True
            },
            {
                'name': 'حفر الآبار',
                'name_fr': 'Forage de puits',
                'description': 'ننشئ آبار ماء صالحة للشرب في القرى الريفية لتحسين الوصول إلى المياه.',
                'description_fr': 'Nous construisons des puits d’eau potable dans les villages pour améliorer l’accès à l’eau.',
                'category': 'البنية التحتية',
                'category_fr': 'Infrastructure',
                'target_amount': 25000.0,
                'raised_amount': 8750.0,
                'is_active': True
            },
            {
                'name': 'مساعدات غذائية عاجلة',
                'name_fr': 'Aides alimentaires urgentes',
                'description': 'نوفر وجبات وطرود غذائية للأسر المحتاجة.',
                'description_fr': 'Nous fournissons des repas et des colis alimentaires aux familles dans le besoin.',
                'category': 'طوارئ',
                'category_fr': 'Urgence',
                'target_amount': 15000.0,
                'raised_amount': 14200.0,
                'is_active': True
            },
            {
                'name': 'التعليم للجميع',
                'name_fr': 'Éducation pour tous',
                'description': 'تمويل تعليم الأطفال المحرومين وبناء المدارس.',
                'description_fr': 'Financer l’éducation des enfants défavorisés et construire des écoles.',
                'category': 'التعليم',
                'category_fr': 'Éducation',
                'target_amount': 75000.0,
                'raised_amount': 23400.0,
                'is_active': True
            },
            {
                'name': 'رعاية صحية مجانية',
                'name_fr': 'Soins de santé gratuits',
                'description': 'تقديم رعاية صحية وأدوية مجانية لغير القادرين.',
                'description_fr': 'Offrir des soins de santé et des médicaments gratuits aux personnes dans le besoin.',
                'category': 'الصحة',
                'category_fr': 'Santé',
                'target_amount': 40000.0,
                'raised_amount': 18900.0,
                'is_active': True
            }
        ]
        
        # Insérer les causes
        for cause_data in causes:
            cause = Cause(**cause_data)
            db.session.add(cause)
        
        # Créer des utilisateurs de test (admin et standard)
        admin_user = User(
            username='admin',
            email='admin@zakat360.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True,
            is_pro=True,
        )
        test_user = User(
            username='testuser',
            email='test@zakat360.com',
            password_hash=generate_password_hash('test'),
            is_pro=True,
        )
        db.session.add_all([admin_user, test_user])
        
        # Sauvegarder les changements
        db.session.commit()
        
        # Créer des dons répartis sur les 12 derniers mois
        causes_list = Cause.query.all()
        now = datetime.utcnow()
        sample_donations = []
        for i in range(12):
            when = now - timedelta(days=30 * i)
            sample_donations.append({
                'cause_id': causes_list[i % len(causes_list)].id,
                'amount': 100.0 + (i * 10.0),
                'donor_name': 'Donateur %d' % (i + 1),
                'status': 'completed',
                'created_at': when,
            })
        for d in sample_donations:
            db.session.add(Donation(**d))
        
        db.session.commit()
        
        print("✅ تم إنشاء بيانات المثال بنجاح!")
        print(f"📊 تم إنشاء {len(causes)} قضايا")
        print(f"💰 تم إنشاء {len(sample_donations)} تبرعات تجريبية")
        print("👤 تم إنشاء مستخدمين: admin@zakat360.com (مسؤول) و test@zakat360.com (اختبار)")

if __name__ == '__main__':
    init_sample_data()
