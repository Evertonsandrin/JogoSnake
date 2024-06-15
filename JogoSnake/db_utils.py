import sqlite3

def conectar_bd():
    conn = sqlite3.connect('recordes.db')
    c = conn.cursor()
    return conn, c

def criar_tabela(c):
    c.execute('''
    CREATE TABLE IF NOT EXISTS recordes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        pontuacao INTEGER NOT NULL
    )
    ''')

def inserir_recorde(c, conn, nome, pontuacao):
    c.execute("INSERT INTO recordes (nome, pontuacao) VALUES (?, ?)", (nome, pontuacao))
    conn.commit()

def obter_melhores_recordes(c):
    c.execute("SELECT nome, pontuacao FROM recordes ORDER BY pontuacao DESC LIMIT 10")
    return c.fetchall()
