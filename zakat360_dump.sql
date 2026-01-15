BEGIN TRANSACTION;
CREATE TABLE audit_logs (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	action VARCHAR(100) NOT NULL, 
	route VARCHAR(200) NOT NULL, 
	details TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE causes (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	category VARCHAR(50) NOT NULL, 
	target_amount NUMERIC(10, 2), 
	raised_amount NUMERIC(10, 2), 
	is_active BOOLEAN, 
	created_at DATETIME, name_fr TEXT, description_fr TEXT, category_fr TEXT, 
	PRIMARY KEY (id)
);
INSERT INTO "causes" VALUES(1,'رعاية الأيتام','ندعم الأطفال الأيتام بتوفير التعليم والغذاء والرعاية الصحية.','الطفولة',50000,15500,1,'2025-10-29 20:59:37.050373','Soutien aux orphelins','Nous soutenons les enfants orphelins avec l’éducation, la nourriture et les soins.','Enfance');
INSERT INTO "causes" VALUES(2,'حفر الآبار','ننشئ آبار ماء صالحة للشرب في القرى الريفية لتحسين الوصول إلى المياه.','البنية التحتية',25000,9870,1,'2025-10-29 20:59:37.050373','Forage de puits','Nous construisons des puits d’eau potable dans les villages pour améliorer l’accès à l’eau.','Infrastructure');
INSERT INTO "causes" VALUES(3,'مساعدات غذائية عاجلة','نوفر وجبات وطرود غذائية للأسر المحتاجة.','طوارئ',15000,17800,1,'2025-10-29 20:59:37.050373','Aides alimentaires urgentes','Nous fournissons des repas et des colis alimentaires aux familles dans le besoin.','Urgence');
INSERT INTO "causes" VALUES(4,'التعليم للجميع','تمويل تعليم الأطفال المحرومين وبناء المدارس.','التعليم',75000,23400,1,'2025-10-29 20:59:37.050373','Éducation pour tous','Financer l’éducation des enfants défavorisés et construire des écoles.','Éducation');
INSERT INTO "causes" VALUES(5,'رعاية صحية مجانية','تقديم رعاية صحية وأدوية مجانية لغير القادرين.','الصحة',40000,18910,1,'2025-10-29 20:59:37.050373','Soins de santé gratuits','Offrir des soins de santé et des médicaments gratuits aux personnes dans le besoin.','Santé');
CREATE TABLE donations (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	cause_id INTEGER, 
	amount NUMERIC(10, 2) NOT NULL, 
	donor_name VARCHAR(100), 
	status VARCHAR(20), 
	created_at DATETIME, proof_path VARCHAR(255), payment_method VARCHAR(50) DEFAULT 'card', 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(cause_id) REFERENCES causes (id)
);
INSERT INTO "donations" VALUES(1,NULL,1,100,'Ahmed Benali','completed','2025-10-29 21:59:37.060321',NULL,'card');
INSERT INTO "donations" VALUES(2,NULL,2,250,'Fatima Zahra','completed','2025-10-29 21:59:37.060321',NULL,'card');
INSERT INTO "donations" VALUES(3,NULL,3,50,'Anonyme','completed','2025-10-29 21:59:37.060321',NULL,'card');
INSERT INTO "donations" VALUES(4,NULL,4,500,'Omar Alami','pending','2025-10-29 21:59:37.060321',NULL,'card');
INSERT INTO "donations" VALUES(5,NULL,3,3600,'jawad','completed','2025-10-30 21:46:32.026014',NULL,'card');
INSERT INTO "donations" VALUES(6,2,1,2000,'chab l3arbi','completed','2025-10-30 21:47:05.071762',NULL,'card');
INSERT INTO "donations" VALUES(7,2,5,10,'Aissam grissag din','completed','2025-10-30 21:47:38.601812',NULL,'card');
INSERT INTO "donations" VALUES(8,NULL,1,500,NULL,'completed','2025-12-27 22:54:49.729131',NULL,'paypal');
INSERT INTO "donations" VALUES(9,NULL,2,500,NULL,'completed','2025-12-27 22:57:15.193270',NULL,'paypal');
INSERT INTO "donations" VALUES(10,NULL,2,20,'Anonyme','completed','2025-12-27 23:03:27.512773',NULL,'paypal');
INSERT INTO "donations" VALUES(11,NULL,2,500,'Anonyme','completed','2026-01-07 16:50:14.167725',NULL,'card');
INSERT INTO "donations" VALUES(12,5,1,500,'mohammed','completed','2026-01-14 11:43:24.164429',NULL,'card');
INSERT INTO "donations" VALUES(13,5,2,100,'jawad','completed','2026-01-14 11:44:36.084540','donation_13.pdf','bank_transfer');
CREATE TABLE price_cache (
	id INTEGER NOT NULL, 
	symbol VARCHAR(20) NOT NULL, 
	price_per_g NUMERIC(10, 4) NOT NULL, 
	currency VARCHAR(10), 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "price_cache" VALUES(1,'GOLD',700,'MAD','2025-10-30 12:41:27.767492');
INSERT INTO "price_cache" VALUES(2,'SILVER',8,'MAD','2025-10-30 12:41:27.774618');
CREATE TABLE scheduled_donations (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	cause_id INTEGER NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	frequency VARCHAR(20) NOT NULL, 
	next_execution DATETIME NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(cause_id) REFERENCES causes (id)
);
CREATE TABLE subscriptions (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	plan_type VARCHAR(20), 
	amount NUMERIC(10, 2), 
	currency VARCHAR(10), 
	status VARCHAR(20), 
	start_date DATETIME, 
	end_date DATETIME NOT NULL, 
	auto_renew BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO "subscriptions" VALUES(1,4,'pro',20,'MAD','active','2025-12-28 22:52:19.398912','2026-12-28 22:52:19.395829',1,'2025-12-28 22:52:19.398921');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	oauth_provider VARCHAR(50), 
	oauth_sub VARCHAR(255), 
	is_pro BOOLEAN, 
	created_at DATETIME, is_admin BOOLEAN DEFAULT 0, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email), 
	UNIQUE (oauth_sub)
);
INSERT INTO "users" VALUES(1,'testuser','test@zakat360.com','pbkdf2:sha256:600000$MSsaQuRlgQwRWa3R$d1040fa35dd8b1499bb193156bf6c2d2b6f972550ea381920323479c8d6470c8',NULL,NULL,0,'2025-10-29 20:59:37.053450',0);
INSERT INTO "users" VALUES(2,'Mohamed','mohakach7@gmail.com','pbkdf2:sha256:600000$14BpX7uTUnciYqaD$61544ec06c27c9b62b3bd56e873f9ed21931011971b4221d2e2cd62d04214639',NULL,NULL,0,'2025-10-29 21:28:36.281435',0);
INSERT INTO "users" VALUES(3,'JAWAD.OUKESSOU','test@gmail.com','pbkdf2:sha256:600000$shlAQR2hfC123YOO$f1fcaacfa8dcc82f6565984a13c6bf3cee2170c83ddf61d2db2b8f20bf232cb1',NULL,NULL,0,'2025-12-28 22:24:48.845579',0);
INSERT INTO "users" VALUES(4,'admin','admin@zakat360.com','pbkdf2:sha256:600000$slWUMbuX4KQCTHTX$3140be2c9c547f3ce994ab1f689d1c53293a253db6f69203ee4212ee9a96bcb6',NULL,NULL,1,'2025-12-28 22:48:19.398689',1);
INSERT INTO "users" VALUES(5,'test','test5@gmail.com','pbkdf2:sha256:600000$MnZrosVVyNqbu2Ru$c6ec4d03dda3340d0f7f2b1a398917121dbc732e4663f1b70a7a04abbc32f4e9',NULL,NULL,0,'2026-01-14 11:38:32.802648',0);
COMMIT;
