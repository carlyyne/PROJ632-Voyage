from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import InformationVille as I
import scrapingTwitter as ScrapT
import apiHotelRestaurantAttraction as HR
import DataBase as DB
import sqlite3 as sql

def toutesLesInformations(driver,curs,conn,ville):
        """regroupement de toutes les fonctions: récupère toutes les données associées à la ville

        Args:
            driver (selenium.webdriver.chrome.webdriver.WebDriver): objet qui permet de simuler l'interaction humaine avec un navigateur web à partir du code Python
            ville (String): ville que l'on souhaite insérer dans la base de données
            curs (sqlite3.Cursor): curseur associé à la connexion
            conn (sqlite3.Connection): instance de connexion à la base de données
        """
        print("\nMerci de patienter le temps de la récupération des données...")
        I.insertionInfosVilleBDD(ville, curs, conn)
        I.insertionMeteoVilleBDD(ville,curs,conn)
        ScrapT.informationsTweeter(driver,ville,curs,conn)
        I.rechercheMeteoVille(ville)
        HR.afficher_carte(ville, curs,conn)
        print("\nINFORMATIONS RÉCUPÉRÉES ! :)")

def menu():
    print("\nVilles présentes dans la base de données:")
    if DB.villesBDD(curs):
        DB.villesBDD(curs)
    else:
        print("Aucune ville présente !")
    print("\nQue souhaitez-vous faire ?")
    print("\n1 - Rechercher les informations d'une nouvelle ville")
    print("2 - Retrouver les informations d'une des villes de la base de donnée")
    choix = input("\nVotre choix (1 ou 2): ")
    if choix == "1":
        ville = input("\nEntrez le nom de la ville : ")
        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.get("https://twitter.com/login")
        toutesLesInformations(driver, curs, conn, ville)
    elif choix == "2":
        ville = input("\nEntrez le nom de la ville : ")
        while True:
            print("\n1 - Informations générales sur la ville (description et localisation)")
            print("2 - Actualités Twitter")
            print("3 - Météo de la ville")
            print("4 - Monuments/Attractions touristiques à voir dans la ville")
            print("5 - Hôtels à proximité de la ville")
            print("6 - Restaurants à proximité de la ville")
            print("7 - Quitter")
            reponse = input("\nVotre choix (1, 2, 3, 4, 5, 6, ou 7): ")

            if reponse == "1":
                print("\n######### INFORMATIONS GENERALES #########")
                DB.infoVilles(curs, ville)
            elif reponse == "2":
                print("\n######### TWEETS #########")
                DB.afficherTousTweets(curs, ville)
            elif reponse == "3":
                print("\n######### METEO #########")
                DB.afficherMeteoVille(curs, ville)
            elif reponse == "4":
                print("\n######### ATTRACTIONS #########")
                DB.afficherToutesAttractions(curs, ville)
            elif reponse == "5":
                print("\n######### HOTELS #########")
                DB.afficherTousHotels(curs, ville)
            elif reponse == "6":
                print("\n######### RESTAURANTS #########")
                DB.afficherTousRestaurants(curs, ville)
            elif reponse == "7":
                print("Retour au menu principal...")
                break
            else:
                print("Choix invalide. Veuillez choisir une option valide.")
    else:
        print("Choix invalide. Veuillez choisir une option valide.")


if __name__ == "__main__":

    ########## Masquage du webScraping ##########
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'

    # configuration des options de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')

    # création de l'objet de service Chrome
    chrome_service = webdriver.chrome.service.Service(ChromeDriverManager().install())

    ########## INITIALISATION ET CREATION DATABASE #########
    conn = sql.connect("databaseVoyage.db")
    curs = conn.cursor()
    DB.creationDatabase(conn,curs)

    ########## Affichage du menu ##########
    menu()
