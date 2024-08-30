import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

criar_tabela = '''CREATE TABLE IF NOT EXISTS hoteis
(hotel_id TEXT PRIMARY KEY,
nome TEXT,
estrelas REAL,
diaria REAL,
cidade TEXT)'''


cria_hotel = "INSERT INTO hoteis VALUES ('alpha', 'Alpha Hotel', 4.3, 200, 'Campinas')"

cursor.execute(criar_tabela)
cursor.execute(cria_hotel)

connection.commit()
connection.close()