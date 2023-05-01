import InformationVille as I

def creationDatabase(conn,curs):
    curs.execute("""CREATE TABLE IF NOT EXISTS Ville (
                    idVille INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nom VARCHAR,
                    NomComplet VARCHAR,
                    Latitude FLOAT,
                    Longitude FLOAT,
                    InfosVille TEXT
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Meteo (
                    idMeteo INTEGER PRIMARY KEY AUTOINCREMENT,
                    Heure DATETIME,
                    TemperatureDegres FLOAT,
                    Description TEXT,
                    HumiditePourcent INTEGER,
                    VitesseVentKmH FLOAT,
                    id_Ville INTEGER REFERENCES VillesRecherchees (idVille)
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Restaurant (
                    idRestaurant INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nom VARCHAR,
                    Adresse TEXT,
                    TypeCuisine TEXT,
                    HorairesOuverture TEXT,
                    Latitude FLOAT,
                    Longitude FLOAT,
                    id_Ville INTEGER REFERENCES VillesRecherchees (idVille)
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Hotel (
                    idHotel INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nom VARCHAR,
                    Adresse TEXT,
                    NbEtoile INTEGER,
                    Latitude FLOAT,
                    Longitude FLOAT,
                    id_Ville INTEGER REFERENCES VillesRecherchees (idVille)
                )""")
    curs.execute("""CREATE TABLE IF NOT EXISTS Attraction (
                    idAttraction INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nom VARCHAR,
                    Adresse TEXT,
                    HorairesOuverture TEXT,
                    Latitude FLOAT,
                    Longitude FLOAT,
                    id_Ville INTEGER REFERENCES VillesRecherchees (idVille)
                )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS Tweet (
                    idTweet INTEGER PRIMARY KEY AUTOINCREMENT,
                    heure TEXT, 
                    tweet_texte TEXT, 
                    likes INTEGER,
                    id_Ville INTEGER REFERENCES VillesRecherchees (idVille)
                )""")

def villesBDD(curs):
    """récupère les noms des villes de la BDD

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion

    """
    curs.execute("SELECT Nom FROM Ville")
    nomsVilles = curs.fetchall()
    for nom in nomsVilles:
        print("- " + nom[0])

def infoVilles(curs, ville):
    """récupère toutes les informations de la Table Ville associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations

    """
    curs.execute("SELECT * FROM Ville WHERE Nom = ?", (ville,))
    villes = curs.fetchall()
    for ville in villes:
        print(f"{ville[1]} - {ville[3]}, {ville[4]} \n{ville[5]}")

def afficherMeteoVille(curs, ville, conn):
    """récupère toutes les données météo de la Table Meteo associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """
    I.insertionMeteoVilleBDD(ville,curs,conn) #utilisation de la fonction pour qu'au moment où l'on demande les données météo de la ville, 
                                              #la météo actuelle soit ajoutée à la BDD et affichée à l'utilisateur
    curs.execute("SELECT * FROM Meteo WHERE id_Ville IN (SELECT idVille FROM Ville WHERE Nom = ?)", (ville,))
    meteos = curs.fetchall()
    for meteo in meteos:
        print(f"Heure : {meteo[1]}")
        print(f"Température : {meteo[2]}°C")
        print(f"Description : {meteo[3]}")
        print(f"Humidité : {meteo[4]}%")
        print(f"Vitesse du vent : {meteo[5]} km/h\n")

def afficherTousRestaurants(curs, ville):
    """récupère tous les restaurants de la Table Restaurant associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations

    """
    curs.execute("SELECT * FROM Restaurant WHERE id_Ville IN (SELECT idVille FROM Ville WHERE Nom = ?)", (ville,))
    restaurants = curs.fetchall()
    for restaurant in restaurants:
        print(f"{restaurant[1]} - {restaurant[2]}")
        print(f"Type de cuisine : {restaurant[3]}")
        print(f"Horaires d'ouverture : {restaurant[4]}\n")

def afficherTousHotels(curs, ville):
    """récupère tous les hotels de la Table Hotel associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations

    """
    curs.execute("SELECT * FROM Hotel WHERE id_Ville IN (SELECT idVille FROM Ville WHERE Nom = ?)", (ville,))
    hotels = curs.fetchall()
    for hotel in hotels:
        print(f"{hotel[1]} - {hotel[2]}")
        print(f"Nombre d'étoiles : {hotel[3]}\n")

def afficherToutesAttractions(curs, ville):
    """récupère toutes les attractions de la Table Attraction associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations

    """
    curs.execute("SELECT * FROM Attraction WHERE id_Ville IN (SELECT idVille FROM Ville WHERE Nom = ?)", (ville,))
    attractions = curs.fetchall()
    for attraction in attractions:
        print(f"{attraction[1]} - {attraction[2]}")
        print(f"Horaires d'ouverture : {attraction[3]}\n")

def afficherTousTweets(curs, ville):
    """récupère toutes les tweets de la Table Tweet associé à ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations

    """
    curs.execute("SELECT * FROM Tweet WHERE id_Ville IN (SELECT idVille FROM Ville WHERE Nom = ?)", (ville,))
    tweets = curs.fetchall()
    for tweet in tweets:
        print(f"Heure : {tweet[1]}")
        print(f"Tweet : {tweet[2]}")
        print(f"Likes : {tweet[3]}\n")
