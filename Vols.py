from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def accepterRobot(driver):
    wait = WebDriverWait(driver, 100)
    try:
        bouton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#kDszFvVpnEynaBA")))
        bouton.click()
    except:
        pass

def RechercheVolsDisponibles(driver, villeDepart, villeArrivee):
    #accepterRobot(driver)
    # attend que la page soit chargée
    wait = WebDriverWait(driver, 10)
    inputDepart = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#findRouteMain > div.flightSearchForm > div.searchOption.routeSearch.text_align_left > form > div:nth-child(1) > div > input")))
    inputDepart.send_keys(villeDepart)
    time.sleep(1)
    inputArrivee = driver.find_element(By.CSS_SELECTOR, "#findRouteMain > div.flightSearchForm > div.searchOption.routeSearch.text_align_left > form > div:nth-child(3) > div > input")
    inputArrivee.send_keys(villeArrivee)
    time.sleep(1)
    boutonRecherche = driver.find_element(By.CSS_SELECTOR, "#findRouteMain > div.flightSearchForm > div.trackSubmit > button")
    boutonRecherche.click()
