# -*- coding: utf-8 -*-
# =============================================================================
# fichier : parse_maree.py
# usage : python parse_maree.py (teste avec python 2.7.10 sur Mac OS 10.11.6)
#         necessite Beautiful soup, un parser XML (HTML)
# copyright (c) 2017-2018 AMP. All rights reserved.
# -----------------------------------------------------------------------------
# description: extrait les informations sur les marees des pages meteoconsult
# contexte : resabel
# =============================================================================
# creation: 15-jan-2017 pchevaillier@gmail.com
# revision: 22-jan-2017 pchevaillier@gmail.com gestion info. marees + coeff
# revision: 23-jan-2017 pchevaillier@gmail.com V3 : sans les coefficients
# revision: 28-jan-2017 pchevaillier@gmail.com V3 : sans les coefficients
# revision: 28-dec-2017 pchevaillier@gmail.com V18-1, avec les coeffs de marees
# revision: 05-jan-2018 pchevaillier@gmail.com ajout du champs 'lieu'
# -----------------------------------------------------------------------------
# commentaires :
#  - traite les données de meteoConsult
# http://marine.meteoconsult.fr/meteo-marine/horaires-maree-le-trez-hir-980-01.php
#  - 2018 : les fichiers sont stockes dans donnees_2018
#           et les fichiers sont nommes 2018-bb_Trez-Hir.html (nn: numero du mois)
# attention :
#  - il y a une erreur dans le fichier pour le mois d'aout 2018 :
#     il manque un coefficient pour la maree de 23h58.
#    j'ai modifie le ficheir 2018-08_Trez-Hir.html en ajoutant une division
#    correspondant a un coef (meme coeff que la maree precedente)
# -----------------------------------------------------------------------------
# a faire:
# =============================================================================

import os, time, re

from bs4 import BeautifulSoup

# --- constantes globales -----------------------------------------------------
separateurChamps = "," # valeur par defaut de MySQL
quoteChamps = '"' # valeur par defaut de MySQL
finLigne = "\r\n" # format MSDOS

# version 2017
#mois = ["janvier", "vrier", "mars", "avril", "mai", "juin", "juillet", "ao", "septembre", "octobre", "novembre", "cembre"]

# version 2018
annee = 2018
mois = ["-01_", "-02_", "-03_", "-04_", "-05_", "-06_", "-07_", "-08_", "-09_", "-10_", "-11_", "-12_"]
lieu = "1" # Trez-Hir

# --- Structures de donnees ---------------------------------------------------
class Table_Maree:
  marees = []

  def __init__(self):
    self.marees = []
  
  def trouver_coefficients(self, noeud):
    filtre_coeffs = re.compile('cercle|separ')

    les_coeffs = True
    coeffs_jour = []
    noeud_coeff = noeud
    while (les_coeffs):
      noeud_coeff = noeud_coeff.find_next("div", { "class" : filtre_coeffs })
      # print '>>>>>>>>>>>>>>>>>>>>>>>>> ' + noeud.attrs['class'][0]
      if noeud_coeff.attrs['class'][0] == 'cercle':
        coeffs_jour.append(noeud_coeff.contents[0])
      else:
        print coeffs_jour
        les_coeffs = False

    self.coefficients(coeffs_jour)
    return
  
  def coefficients(self, coeffs):
    #pms = [m for m in self.marees if m.type == "PM"]
    pms = []
    for m in self.marees:
      if (m.type == "PM"):
        pms.append(m)
    print str(len(pms)) + ' ' + str(len(coeffs))
    coeffs.reverse()
    for x in pms:
      x.coefficient = coeffs.pop()
    return

  def afficher(self):
    for m in self.marees:
      m.afficher()
    return

  def ecrire_dans_fichier(self, fichier):
    for m in self.marees:
      m.ecrire_dans_fichier(fichier)
    return

# ------------------------------------------------------------------------------
class Maree:
  type = ""
  date_heure = ""
  heure = 0
  hauteur = 0.0
  coefficient = "0"

  def __init__(self):
    self.type = ""
    date_heure = ""
    self.heure = 0
    self.hauteur = 0.0
    self.coefficient = "0"
  
  def afficher(self):
    print self.date_heure + ' ' + self.type + ' ' + str(self.heure) + ' ' + str(self.hauteur) + ' ' + str(self.coefficient)

  def def_date_heure(self, jour, mois, annee, heure):
    #2017-01-24 20:22:17 : format MySQL type date
    if mois < 10:
      m = '0' + str(mois)
    else:
      m = str(mois)
    
    if jour < 10:
      j = '0' + str(jour)
    else:
      j = str(jour)
    
    self.date_heure = str(annee) + '-' + m + '-' + j + ' ' + heure
    t = time.strptime(self.date_heure, "%Y-%m-%d %H:%M:%S")
    self.heure = int(time.mktime(t))

  def ecrire_dans_fichier(self, fichier):
    ligne = quoteChamps + lieu + quoteChamps + separateurChamps + quoteChamps + self.date_heure + quoteChamps + separateurChamps + quoteChamps + self.type + quoteChamps + separateurChamps + quoteChamps + str(self.heure) + quoteChamps + separateurChamps + quoteChamps + str(self.hauteur) + quoteChamps + separateurChamps + quoteChamps + self.coefficient + quoteChamps + finLigne
    fichier.write(ligne)


# --- Quelques initialisations ------------------------------------------------

# nom du dossier racine
dossierRacine = "."

# --- Chemins d'acces aux fichiers en relatif / dossier racine
dossierFichiersSource = dossierRacine

# filtre pour la detection des fichiers contenant les donnees d'origine
filtreFichiersSource = "Trez-Hir"

# Nom de fichier de destination
dossierFichierCible = dossierRacine
nomFichierCible = "marees.csv"

# entete du fichier cible (pour l'instant il n'y en a pas, a voir...)
#header = "jour" + sepf + "heure_bm" + sepf + "hauteur_bm" + sepf + "heure_pm" + sepf + "hauteur_pm"  + "coefficient" + finLigne

# =============================================================================
# Traitement des fichiers

dossiers = [x for x in os.listdir(dossierFichiersSource) if x.count(str(annee))]

print "Traitement du dossier " + dossierFichiersSource 
print " nombre de dossiers : " + str(len(dossiers))

filtre_noeuds = re.compile('basse_mer|pleine_mer|coef')

for d in dossiers:
  cheminSource = dossierFichiersSource + "/" + d
  cheminCible = dossierFichierCible + "/" + nomFichierCible
  print "fichier cible : " + cheminCible
  
  fichierCible = open(cheminCible, 'w')
  fichiers = [x for x in os.listdir(d) if x.count(filtreFichiersSource)]
  for f in fichiers:
    cheminFichierSource = cheminSource + "/" + f
    print "Traitement du fichier " + cheminFichierSource
    
    leMois = 0;
    for m in mois:
      leMois += 1
      if re.search(m, f, re.UNICODE):
         break

    soup = BeautifulSoup(open(cheminFichierSource), "html.parser")
    for chaque_jour in  soup.findAll("div", { "class" : "tab_date" }):

      noeud = chaque_jour
      print '-----------------------------------------------------------------'
      # La date du jour
      elements = re.split(' ', noeud.contents[0])
      jour = int(elements[1])
      
      marees_jour = Table_Maree()
      
      encore = True
      while (encore):
        noeud = noeud.find_next("div", {"class" : filtre_noeuds })
        
        if re.search('Basse', noeud.contents[0]):
          maree = Maree()
          maree.type = 'BM'
        elif re.search('Pleine', noeud.contents[0]):
          maree = Maree()
          maree.type = 'PM'
        else:
          marees_jour.trouver_coefficients(noeud)
          encore = False
          break

        marees_jour.marees.append(maree)
    
        noeud = noeud.find_next("div", { "class" : "heure" })
        elements = re.split('h',noeud.contents[0])
        heure = elements[0] + ':' + elements[1] + ':00'

        maree.def_date_heure(jour, leMois, annee, heure)

        noeud = noeud.find_next("div", { "class" : "metre" })
        elements = re.split('m', noeud.contents[0])
        maree.hauteur = float(elements[0])


      marees_jour.afficher()
      marees_jour.ecrire_dans_fichier(fichierCible)

fichierCible.close()

# -----------------------------------------------------------------------------
# --- Finishing the job

# Nothing else to do :-)

# =============================================================================
# --- end of file -------------------------------------------------------------
# =============================================================================
