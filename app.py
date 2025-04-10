from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

def leggi_utenti():
    if not os.path.exists('Utenti.csv'):
        pd.DataFrame(columns=['id', 'nome', 'email', 'password']).to_csv('Utenti.csv', index=False)
    return pd.read_csv('Utenti.csv').dropna()

def leggi_dati_utente():
    if not os.path.exists('DatiUtente.csv'):
        pd.DataFrame(columns=['id', 'citta', 'nazione']).to_csv('DatiUtente.csv', index=False)
    return pd.read_csv('DatiUtente.csv').dropna()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']

        utenti = leggi_utenti()
        
        if not utenti.empty and email in utenti['email'].values:
            return render_template('/signup.html', error='Email già registrata. Usa un\'altra email.')
        
        nuovo_utente = pd.DataFrame({'id': [len(utenti)], 'nome': [nome], 'email': [email], 'password': [password]})
        nuovi_dati = pd.DataFrame({'id': [len(utenti)], 'citta': [None], 'nazione': [None]})
        
        pd.concat([utenti, nuovo_utente], ignore_index=True).to_csv('Utenti.csv', index=False)
        pd.concat([leggi_dati_utente(), nuovi_dati], ignore_index=True).to_csv('DatiUtente.csv', index=False)

        return redirect(url_for('index'))

    return render_template('/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        utenti = leggi_utenti()
        utente = utenti[(utenti['email'] == email) & (utenti['password'] == password)]
        
        if not utente.empty:
            utente_id = int(utente['id'].values[0])
            nome_utente = utente['nome'].values[0]
            return redirect(url_for('utente', utente_id=utente_id, nome_utente=nome_utente))

        return render_template('login.html', error='Credenziali non valide')

    return render_template('login.html')

@app.route('/user')
def utente():
    utente_id = request.args.get('utente_id')
    nome_utente = request.args.get('nome_utente')
    
    if not utente_id or not nome_utente:
        return redirect(url_for('login'))
    
    utente_id = int(utente_id)
    dati_utente = leggi_dati_utente()
    dati_personali = dati_utente[dati_utente['id'] == utente_id]
    
    citta = ""
    nazione = ""
    if not dati_personali.empty:
        if pd.notna(dati_personali['citta'].values[0]):
            citta = dati_personali['citta'].values[0]
        if pd.notna(dati_personali['nazione'].values[0]):
            nazione = dati_personali['nazione'].values[0]
    
    return render_template('user.html', utente_id=utente_id, nome_utente=nome_utente, citta=citta, nazione=nazione)

@app.route('/update_profile', methods=['POST'])
def aggiorna_profilo():
    utente_id = request.form.get('user_id')
    nome_utente = request.form.get('user_name')
    
    if not utente_id or not nome_utente:
        return redirect(url_for('login'))
    
    utente_id = int(utente_id)
    citta = request.form['citta']
    nazione = request.form['nazione']
    
    dati_utente = leggi_dati_utente()
    
    if utente_id in dati_utente['id'].values:
        dati_utente.loc[dati_utente['id'] == utente_id, 'citta'] = citta
        dati_utente.loc[dati_utente['id'] == utente_id, 'nazione'] = nazione
    else:
        nuovi_dati = pd.DataFrame({'id': [utente_id], 'citta': [citta], 'nazione': [nazione]})
        dati_utente = pd.concat([dati_utente, nuovi_dati], ignore_index=True)
    
    dati_utente.to_csv('DatiUtente.csv', index=False)
    
    return redirect(url_for('utente', utente_id=utente_id, nome_utente=nome_utente))

@app.route('/logout')
def disconnetti():
    return redirect(url_for('indice'))

if __name__ == '__main__':
    app.run(debug=True)
