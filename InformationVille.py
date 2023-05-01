import requests
import datetime
import wikipedia

def informationsVille(ville, curs, conn):
    insertionInfosVilleBDD(ville, curs, conn)
    insertionMeteoVilleBDD(ville,curs,conn)

def rechercheInformationsWikipediaVille(ville):
    """recherche des informations concernant une ville, ces informations sont trouvées grâce à la librairie wikipedia

    Args:
        ville (string): ville dont on cherche des informations

    Returns:
        string: une partie de la page wikipedia
    """
    wikipedia.set_lang("fr") #langue à français
    ville = ville + " " + "ville"
    try:
        contenu_page = wikipedia.page(ville).summary
    except wikipedia.exceptions.PageError:
        contenu_page = "Aucunes informations trouvées pour cette ville !"
        
    return contenu_page  


def rechercheLocVille(ville):
    """Recherche de la localisation de la ville

    Args:
        ville (String): ville dont on cherche la longitude et latitude

    Returns:
        Tuple: nom précis de la ville, latitude et longitude
    """

    #URL de l'API OpenStreetMap
    url = f'https://nominatim.openstreetmap.org/search?q={ville}&format=json&polygon=1&limit=1&polygon_geojson=1'

    # Envoyer la requête et récupérer les données JSON
    response = requests.get(url).json()
    
    # Coordonnées
    lat = response[0]['lat']
    lon = response[0]['lon']
    nom = response[0]['display_name']

    return nom, lat, lon

def insertionInfosVilleBDD(ville, curs, conn):
    """Insertion des informations trouvées sur la ville dans la BDD

    Args:
        ville (String): ville que l'on souhaite insérer dans la base de données
        curs (sqlite3.Cursor): curseur associé à la connexion
        conn (sqlite3.Connection): instance de connexion à la base de données
    """

    # Données
    nomComplet, lat, lon = rechercheLocVille(ville)
    contenuPage = rechercheInformationsWikipediaVille(ville)

    # Vérification concernant la présence de cette ville dans la base de données
    curs.execute("SELECT * FROM Ville WHERE Nom=? AND NomComplet=? AND Latitude=? AND Longitude=?", (ville, nomComplet, lat, lon))
    result = curs.fetchone()

    # L'ajouter si elle n'est pas déjà présente
    if result is None:
        curs.execute("INSERT INTO Ville (Nom, NomComplet, Latitude, Longitude, InfosVille) VALUES (?, ?, ?, ?, ?)", (ville, nomComplet, float(lat), float(lon), contenuPage))
        conn.commit()

def rechercheMeteoVille(ville):
    """recherche des informations sur le météo au moment même de l'utilisation de cette fonction

    Args:
        ville (String): ville que l'on souhaite insérer dans la base de données

    Returns:
        Tuple: heure,temperature,description,humidite,vitesseVent de la ville
    """
    api_key = "193c20243a3ce595608d49124c9ad916" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={api_key}&units=metric"
    response = requests.get(url)
    # si il n'y a pas d'erreur
    if response.status_code == 200:
        data = response.json()
        heure = datetime.datetime.now().strftime("%H:%M:%S")
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidite = data["main"]["humidity"]
        vitesseVent = data["wind"]["speed"]
    else:
        print("Erreur lors de la récupération des données météorologiques.")
    
    return heure,temperature,description,humidite,vitesseVent

def insertionMeteoVilleBDD(ville,curs,conn):
    """insertion de la météo de la ville dans la base de donnée

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données
    """
    heure, temperature,description,humidite,vitesseVent = rechercheMeteoVille(ville)

    cursVille = curs.execute(f"SELECT idVille FROM Ville WHERE Nom LIKE '{ville}'")
    id_Ville = cursVille.fetchone()[0]
    
    curs.execute("INSERT INTO Meteo (Heure,TemperatureDegres,Description,HumiditePourcent,VitesseVentKmH,id_Ville) VALUES (?, ?, ?, ?, ?, ?)", (heure, temperature, description, humidite, vitesseVent,id_Ville))
    conn.commit()