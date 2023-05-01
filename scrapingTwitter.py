import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def informationsTweeter(driver,ville,curs,conn):
    """regroupement de toutes les fonctions necessaires au scraping: récupère tous les tweets associés à la ville

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): objet qui permet de simuler l'interaction humaine avec un navigateur web à partir du code Python
        ville (String): ville que l'on souhaite insérer dans la base de données
        curs (sqlite3.Cursor): curseur associé à la connexion
        conn (sqlite3.Connection): instance de connexion à la base de données
    """
    connectionTwitter(driver)
    trouverCompteVille(driver,ville)
    recupererTweetCompteVille(driver, ville)
    insererTweetsBDD(ville,curs,conn)
    driver.close()
    driver.quit()


def connectionTwitter(driver):

    """ Recherche dans fichier id.txt le terminal l'identifiant et le mot de passe"""
    f = open("/Users/carlynebarrachin/Documents/Polytech/FI3/S6/PROJ632-SCRAPING/Projet2/id.txt", "r")
    lines = f.read().splitlines() #afficher le contenu dans une liste, par ligne, sans \n

    #Entrer dans le terminal l'adresse mail et le mot de passe
    inputEmail = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="text"]')))
    #inputEmail.send_keys(input('Adresse email: '))
    inputEmail.send_keys(lines[0])

    #suivant
    bouton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Suivant')]")))
    bouton.click()

    try:
        #verification utilisateur
        inputUtilisateur = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="text"]')))
        #inputUtilisateur.send_keys(input('Nom utilisateur: '))
        inputUtilisateur.send_keys(lines[1])

        #suivant
        bouton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Suivant')]")))
        bouton.click()

        #mot de passe
        inputMDP = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="password"]')))
        #inputMDP.send_keys(getpass.getpass('Mot de passe: '))
        inputMDP.send_keys(lines[2])


        #se connecter
        boutonConnection = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Se connecter')]")))
        boutonConnection.click()

    except:
        #mot de passe
        inputMDP = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="password"]')))
        #inputMDP.send_keys(getpass.getpass('Mot de passe: '))
        inputMDP.send_keys(lines[2])

        #se connecter
        boutonConnection = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Se connecter')]")))
        boutonConnection.click()

def trouverCompteVille(driver, ville):
    # rechercheVille
    inputVille = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')))
    inputVille.send_keys(ville)

    # rechercher
    inputVille.send_keys(Keys.ENTER)

    # selectionner la section people
    people = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"People")]')))
    people.click()

    # chercher le compte de la ville
    try:
        compteVille = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(),"Ville de {ville}")]')))
    except:
        try:
            compteVille = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(),"Tourisme {ville}")]')))
        except:
            try:
                compteVille = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(),"{ville}")]')))
            except:
                compteVille = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(),"City of {ville}")]')))
    compteVille.click()


def recupererTweetCompteVille(driver, ville):

    #nom de profil du compte de la ville
    usertag = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="UserName"]'))).text
    
    #liste des tweet recuperes
    tweets = []

    #recuperation de tous les tweets de la page
    tweets_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))

    #recuperation des 6 premiers tweets
    while len(tweets) < 6:
        for element in tweets_elements:

            #recuperation de la personne qui a poster le tweet
            userTweet = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[@data-testid="User-Name"]')))

            #on regarde si c'est la personne associee au compte qui a postee le tweet
            if usertag == str(userTweet.text).split("\n·\n")[0]:
                tweet = {}
                heure = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.XPATH, './/time'))).get_attribute('datetime')
                tweet['heure'] = heure
                tweet_texte = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[@data-testid="tweetText"]'))).text
                tweet_texte = tweet_texte.replace('\n', '')
                tweet['tweet_texte'] = tweet_texte
                likes = WebDriverWait(element, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[@data-testid="like"]'))).text
                tweet['likes'] = likes
                if tweet not in tweets:
                    tweets.append(tweet)

        #scroll sur la page pour accéder à tous les tweets
        driver.execute_script('window.scrollBy(0, window.innerHeight);')
        time.sleep(2) 

        #recuperation de tous les tweets de la nouvelle page
        tweets_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))

    # Convertir les données en DataFrame pandas
    df = pd.DataFrame(tweets)

    # Vérifier si le dossier existe, sinon le créer
    dossier = f'vacances_a_{ville}'
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # Sauvegarder le DataFrame dans un fichier Excel dans le dossier tweets
    nom_fichier = os.path.join(dossier, ville + '_tweets.xlsx')
    df.to_excel(nom_fichier, index=False)

    return tweets

def insererTweetsBDD(ville,curs,conn):

    # Lire les données depuis le fichier Excel
    nom_fichier = f'vacances_a_{ville}/' + ville + '_tweets.xlsx'
    df = pd.read_excel(nom_fichier)

    cursVille = curs.execute(f"SELECT idVille FROM Ville WHERE Nom LIKE '{ville}'")
    id_Ville = cursVille.fetchone()[0]

    # Insérer les données dans la table
    for index, row in df.iterrows():
        heure = row['heure']
        tweet_texte = row['tweet_texte']
        likes = row['likes']

        curs.execute("SELECT * FROM Tweet WHERE heure=? AND tweet_texte=? AND likes=?", (heure, tweet_texte, likes))
        result = curs.fetchone()

        if not result:
            curs.execute(f"INSERT INTO Tweet (heure, tweet_texte, likes, id_Ville) VALUES ('{heure}', \"{tweet_texte}\", '{likes}', '{id_Ville}')")
            conn.commit()
        