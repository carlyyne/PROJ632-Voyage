import os
import requests
import csv
import folium

def afficher_carte(ville, curs, conn):
    """afficher la carte avec tous les popups des restaurants, hotels et attractions touristiques

    Args:
        ville (String): ville que l'on souhaite insérer dans la base de données
        curs (sqlite3.Cursor): curseur associé à la connexion
        conn (sqlite3.Connection): instance de connexion à la base de données
    """
    
    #recherche des différents points d'interets
    rechercheRestaurant(ville, curs, conn)
    rechercheHotel(ville, curs, conn)
    rechercheAttractionsTouristiques(ville, curs, conn)

    #recuperation des contenu des fichiers csv
    dossier = f'vacances_a_{ville}'
    restaurants = lireFichier(dossier, "restaurant", ville)
    hotels = lireFichier(dossier, "hotel", ville)
    attractions = lireFichier(dossier, "attractions_touristique", ville)

    #recuperation des coordonnées de la ville pour le placement de la carte
    curs.execute(f"SELECT Latitude, Longitude FROM Ville WHERE Nom LIKE '{ville}'")
    resultat = curs.fetchone()
    lat = resultat[0]
    lon = resultat[1]

    # Création de la carte
    carte = folium.Map(location=[lat, lon], zoom_start=12)

    # Ajout des marqueurs pour chaque lieu
    carte = creationPointsInteretsCarte(restaurants,hotels,attractions,carte,dossier,ville)

def lireFichier(dossier, type_lieu, ville):
    """lecture du fichier csv associé au type du point d'intéret et creation d'une liste des lieux

    Args:
        dossier (string): dossier où le fichier va être placé
        type_lieu (string): type du lieu: restaurant ou hotel ou attraction
        ville (String): ville que l'on souhaite insérer dans la base de données

    Returns:
        list: liste des lieux qui nous interressent (restaurant ou hotel ou attraction)
    """
    lieux = []
    with open(f'{dossier}/{type_lieu}s_{ville}.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['name']:
                row['type'] = type_lieu
                lieux.append(row)
    return lieux

def creationPointsInteretsCarte(restaurants,hotels,attractions,carte,dossier,ville):
    """creation d'un marker et d'un popup: affciher les points d'interets sur la carte

    Args:
        restaurants (_type_): _description_
        hotels (_type_): _description_
        attractions (_type_): _description_
        carte (_type_): _description_
    """
    for lieu in restaurants + hotels + attractions:
        nom = lieu['name']
        latitude = float(lieu['latitude'])
        longitude = float(lieu['longitude'])
        location = [latitude, longitude]
        tooltip = nom
        popup = None
        marker_color = None
        marker_icon = None

        # Personnaliser le contenu des popups en fonction du type de lieu
        if lieu['type'] == 'restaurant':
            cuisine = lieu.get('cuisine', '')
            heure_ouverture = lieu.get('opening_hours', '')
            popup = folium.Popup(html = f"<b>{nom}</b><br>Cuisine: {cuisine}<br>Heures d'ouverture: {heure_ouverture}")
            marker_color = 'orange'
            marker_icon = 'cutlery'

        elif lieu['type'] == 'hotel':
            etoiles = lieu.get('stars', '')
            popup = folium.Popup(html = f"<b>{nom}</b><br>Etoiles: {etoiles}")
            marker_color = 'blue'
            marker_icon = 'home'

        elif lieu['type'] == 'attractions_touristique':
            horairesOuverture = lieu.get('horairesOuverture', '')
            popup = folium.Popup(html = f"<b>{nom}</b><br>Heures d'ouverture: {horairesOuverture}")
            marker_color = 'red'
            marker_icon = 'star'

        if popup is not None:
            marker = folium.Marker(location=location, tooltip=tooltip,icon=folium.Icon(color=marker_color, icon=marker_icon, prefix='glyphicon'))
            marker.add_child(popup)
            marker.add_to(carte)

    carte.save(f'{dossier}/carte_{ville}.html')

def rechercheRestaurant(ville, curs, conn):
    """recherche tous les restaurants d'une ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """

    # Requête pour récupérer les informations des restaurants
    query = f"""
    [out:json];
    area["name"="{ville}"]->.a;
    (
    node["amenity"="restaurant"](area.a);
    way["amenity"="restaurant"](area.a);
    relation["amenity"="restaurant"](area.a);
    );
    out center;
    """

    response = requests.post("https://overpass-api.de/api/interpreter", data=query)

    restaurants = []
    for feature in response.json()["elements"]:
        if "amenity" in feature["tags"] and "addr:street" in feature["tags"] and "cuisine" in feature["tags"] and "opening_hours" in feature["tags"] and "lat" in feature and "lon" in feature:
            restaurants.append(feature)

    # Vérifier si le dossier existe, sinon le créer
    dossier = f'vacances_a_{ville}'
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # Écriture des résultats dans un fichier CSV
    with open(f'{dossier}/restaurants_{ville}.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'address', 'cuisine', 'opening_hours', 'latitude', 'longitude']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


        # Écriture des restaurants
        for feature in restaurants:
            writer.writerow({
                'name': (feature["tags"]["name"] if "name" in feature["tags"] else "").strip(),
                'address': (feature["tags"]["addr:street"] + " " + feature["tags"].get("addr:postcode", "")).strip(),
                'cuisine': (feature["tags"]["cuisine"] if "cuisine" in feature["tags"] else "").strip(),
                'opening_hours': (feature["tags"]["opening_hours"] if "opening_hours" in feature["tags"] else "").strip(),
                'latitude': feature["lat"],
                'longitude': feature["lon"]
            })
    
    insersionRestaurantBDD(curs,conn,ville)

def rechercheHotel(ville, curs, conn):
    """recherche tous les hotels d'une ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """
    
    # Requête pour récupérer les informations des hotels
    query = f"""
    [out:json];
    area["name"="{ville}"]->.a;
    (
    node["tourism"="hotel"](area.a);
    way["tourism"="hotel"](area.a);
    relation["tourism"="hotel"](area.a);
    );
    out center;
    """

    response = requests.post("https://overpass-api.de/api/interpreter", data=query)

    # Tri des hôtels par nombre d'étoiles
    hotels = []
    for feature in response.json()["elements"]:
        if "tourism" in feature["tags"] and "addr:street" in feature["tags"] and "lat" in feature and "lon" in feature:
            stars = feature["tags"].get("stars", None)
            if stars is not None and stars.isdigit():
                feature["tags"]["stars"] = int(stars)
            else:
                feature["tags"]["stars"] = 0
            hotels.append(feature)
    hotels.sort(key=lambda x: x["tags"]["stars"])

     # Vérifier si le dossier existe, sinon le créer
    dossier = f'vacances_a_{ville}'
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # Écriture des résultats dans un fichier CSV
    with open(f'{dossier}/hotels_{ville}.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'address', 'stars','latitude','longitude']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Écriture des hôtels
        for feature in hotels:
            writer.writerow({
                'name': (feature["tags"]["name"] if "name" in feature["tags"] else "").strip(),
                'address': (feature["tags"]["addr:street"] + " " + feature["tags"].get("addr:postcode", "")).strip(),
                'stars': feature["tags"]["stars"],
                'latitude': feature["lat"],
                'longitude': feature["lon"]
            })
    insersionHotelBDD(curs,conn,ville)

def rechercheAttractionsTouristiques(ville, curs, conn):
    """recherche toutes les attractions touristiques d'une ville

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """

    # Requête pour récupérer les informations des attractions touristiques à {ville}
    query = f"""
    [out:json];
    area["name"="{ville}"]->.a;
    (
    node["leisure"](area.a);
    way["leisure"](area.a);
    relation["leisure"](area.a);
    node["tourism"="attraction"](area.a);
    way["tourism"="attraction"](area.a);
    relation["tourism"="attraction"](area.a);
    node["tourism"="museum"](area.a);
    way["tourism"="museum"](area.a);
    relation["tourism"="museum"](area.a);
    node["tourism"="aquarium"](area.a);
    way["tourism"="aquarium"](area.a);
    relation["tourism"="aquarium"](area.a);
    node["tourism"="artwork"](area.a);
    way["tourism"="artwork"](area.a);
    relation["tourism"="artwork"](area.a);
    node["tourism"="gallery"](area.a);
    way["tourism"="gallery"](area.a);
    relation["tourism"="gallery"](area.a);
    node["tourism"="theme_park"](area.a);
    way["tourism"="theme_park"](area.a);
    relation["tourism"="theme_park"](area.a);
    node["tourism"="viewpoint"](area.a);
    way["tourism"="viewpoint"](area.a);
    relation["tourism"="viewpoint"](area.a);
    node["tourism"="zoo"](area.a);
    way["tourism"="zoo"](area.a);
    relation["tourism"="zoo"](area.a);
    );
    out center;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data=query)

    # Récupération des attractions touristiques
    attractions = []
    for feature in response.json()["elements"]:
        if "tags" in feature and "name" in feature["tags"] and ("addr:street" in feature["tags"] or "opening_hours" in feature["tags"] or "addr:postcode" in feature["tags"]) and "lat" in feature and "lon" in feature:
            attractions.append(feature)

    # Vérifier si le dossier existe, sinon le créer
    dossier = f'vacances_a_{ville}'
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    # Écriture des résultats dans un fichier CSV
    with open(f'{dossier}/attractions_touristiques_{ville}.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'address', 'horairesOuverture','latitude','longitude']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Écriture des attractions touristiques
        for feature in attractions:
            writer.writerow({
                'name': (feature["tags"]["name"]).strip(),
                'address': (feature["tags"].get("addr:street", "") + " " + feature["tags"].get("addr:postcode", "")).strip(),
                'horairesOuverture': (feature["tags"].get("opening_hours", "")).strip(),                
                'latitude': feature["lat"],
                'longitude': feature["lon"]
            })
    
    insersionAttractionBDD(curs,conn,ville)

def insersionAttractionBDD(curs,conn,ville):
    """insère toutes les attractions d'une ville dans la BDD

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """

    cursVille = curs.execute(f"SELECT idVille FROM Ville WHERE Nom LIKE '{ville}'")
    id_Ville = cursVille.fetchone()[0]

    # Lecture du fichier CSV et insertion des données dans la table
    with open(f'vacances_a_{ville}/attractions_touristiques_{ville}.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # sauter la première ligne

        for row in reader:
            Nom = row[0]
            Adresse = row[1]
            HorairesOuverture = row[2]
            lat = row[3]
            lon = row[4]

            #Verifie si l'attraction n'est pas deja dans la BDD
            curs.execute("SELECT * FROM Attraction WHERE Nom=?", (Nom,))
            result = curs.fetchone()

            if result is None:
                curs.execute("INSERT INTO Attraction (Nom, Adresse, HorairesOuverture, Latitude, Longitude, id_Ville) VALUES (?, ?, ?, ?, ?, ?)", (Nom, Adresse, HorairesOuverture,lat,lon,id_Ville))
                conn.commit()


def insersionRestaurantBDD(curs,conn,ville):
    """insère tous les restaurants d'une ville dans la BDD

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """
    cursVille = curs.execute(f"SELECT idVille FROM Ville WHERE Nom LIKE '{ville}'")
    id_Ville = cursVille.fetchone()[0]

    # Lecture du fichier CSV et insertion des données dans la table
    with open(f'vacances_a_{ville}/restaurants_{ville}.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # sauter la première ligne

        for row in reader:
            Nom = row[0]
            Adresse = row[1]
            TypeCuisine = row[2]
            HorairesOuverture = row[3]
            lat = row[4]
            lon = row[5]

            #Verifie si le restaurant n'est pas deja dans le BDD
            curs.execute("SELECT * FROM Restaurant WHERE Nom=?", (Nom,))
            result = curs.fetchone()


            if result is None:
                curs.execute("INSERT INTO Restaurant (Nom, Adresse, TypeCuisine, HorairesOuverture, Latitude, Longitude, id_Ville) VALUES (?, ?, ?, ?, ?, ?, ?)", (Nom, Adresse, TypeCuisine, HorairesOuverture,lat,lon,id_Ville))
                conn.commit()

def insersionHotelBDD(curs,conn,ville):
    """insère tous les hotels d'une ville dans la BDD

    Args:
        curs (sqlite3.Cursor): curseur associé à la connexion
        ville (string): ville pour laquelles on chercher des informations
        conn (sqlite3.Connection): instance de connexion à la base de données

    """
    cursVille = curs.execute(f"SELECT idVille FROM Ville WHERE Nom LIKE '{ville}'")
    id_Ville = cursVille.fetchone()[0]

    # Lecture du fichier CSV et insertion des données dans la table
    with open(f'vacances_a_{ville}/hotels_{ville}.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')        
        next(reader)  # sauter la première ligne

        for row in reader:
            Nom = row[0]
            Adresse = row[1]
            NbEtoile = row[2]
            lat = row[3]
            lon = row[4]
            
            #Verifie si l'hotel n'est pas deja dans le BDD
            curs.execute("SELECT * FROM Hotel WHERE Nom=?", (Nom,))
            result = curs.fetchone()

            if result is None:
                curs.execute("INSERT INTO Hotel (Nom, Adresse, NbEtoile, Latitude, Longitude, id_Ville) VALUES (?, ?, ?, ?, ?, ?)", (Nom, Adresse, NbEtoile, lat, lon, id_Ville))
                conn.commit()