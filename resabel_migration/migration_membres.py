# -*- coding: utf-8 -*-
# ==============================================================================
# context: Resabel - systeme de REServAtion de Bateau En Ligne 
#   migration base de données v1 vers v2
# description: script de transformation de donnes
#  - source : fichier membres.csv, export de la table membres de resabel v1
#  - fichiers produits : fichiers csv correspondants 
#    aux tables rsbl_membres et rsbl_connexions de base de donnees v2
# copyright (c) 2024 Pierre Chevaillier. All rights reserved.
# ------------------------------------------------------------------------------
# usage: python <thisFileName>
# dependencies: python 3 (see import statements)
#  - chemin vers les fichiers 
# - structure des fichiers de donnees source et destination
# used with:
#   - python 3.8.17 on macOS 13.6
#   - python 3.9.6 on macOS 13.6
# ------------------------------------------------------------------------------
# creation: 07-juin-2024 pchevaillier@gmail.com
# revision:
# ------------------------------------------------------------------------------
# comments:
# - quelques initialiations de champs quand la donnee est manquante 
#   (ou possiblement fausse) dans la table de la v1
# warnings:
# - 
# todos:
#  - test it and then test it again
# ==============================================================================

import os
import sys

eol = '\n' # SEE: https://docs.python.org/3/library/os.html (see os.linesep)
csv_sep = ';' # to avoid confusion between french decimal sep (,) and field separator
extension_fichier = 'csv'
delimiteur = '"'

# ==============================================================================
# --- Chemins d'acces aux fichiers en relatif / dossier racine
dossier_racine = './../../bdd_resabel'
dossier_v1 = dossier_racine + '/' + 'v1_' + '2024-06-06'
dossier_v2 = dossier_racine + '/' + 'v2_' + '2024-06-06'

# ==============================================================================
# --- Structures de donnees

# Table de la version 1
# "code";"identifiant";"actif";"connexion";"niveau";"genre";"mot_passe";"prenom";"nom";"date_naissance";"code_commune";"rue";"telephone";"telephone2";"courriel";"cdb";"derniere_connexion";"num_licence"
class Membre_v1:
  def __init__(self):
    self.code = 0
    self.identifiant = ""
    self.actif = 0
    self.connexion = 0
    self.niveau = 0
    self.genre = ""
    self.prenom = ""
    self.nom = ""
    self.date_naissance = ""
    self.code_commune = 0
    self.rue = ""
    self.telephone = ""
    self.telephone2 = ""
    self.courriel = ""
    self.cdb = 0
    self.derniere_connexion = 0
    self.num_licence = ""

  def remplir(self, donnee):
    self.code = int(donnee[0])
    self.identifiant = donnee[1]
    self.actif = int(donnee[2])
    self.connexion = int(donnee[3])
    self.niveau = int(donnee[4])
    self.genre = donnee[5]
    # on ne lit pas le mot de passe
    self.prenom = donnee[7]
    self.nom = donnee[8]
    self.date_naissance = donnee[9]
    self.code_commune = donnee[10]
    self.rue = donnee[11]
    self.telephone = donnee[12]
    self.telephone2= donnee[13]
    self.courriel = donnee[14]
    self.cdb = int(donnee[15])
    self.derniere_connexion = donnee[16]
    self.num_licence = donnee[17]
    # print(f"code: {self.code} id: {self.identifiant}")
    return

# Tables de la version 2
class Membre_v2:
  def __init__(self):
    self.code = 0
    self.niveau = 0
    self.genre = "F"
    self.prenom = u""
    self.nom = u""
    self.date_naissance = ""
    self.code_commune = 0
    self.rue = u""
    self.telephone = ""
    self.telephone2 = ""
    self.courriel = ""
    self.cdb = 0
    self.num_licence = ""

  def remplir(self, membre_v1):
    self.code = int(membre_v1.code)
    self.niveau = int(membre_v1.niveau)
    self.genre = membre_v1.genre
    self.prenom = membre_v1.prenom
    self.nom = membre_v1.nom
    if membre_v1.date_naissance == "0000-00-00":
      self.date_naissance = "1900-01-01" 
    else:
      self.date_naissance = membre_v1.date_naissance
    self.code_commune = int(membre_v1.code_commune)
    self.rue = membre_v1.rue
    self.telephone = membre_v1.telephone
    self.telephone2 = membre_v1.telephone2
    self.courriel = membre_v1.courriel
    self.cdb = membre_v1.cdb
    self.num_licence = membre_v1.num_licence
    return
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code) + delimiteur + csv_sep
    resultat += delimiteur + str(self.niveau) + delimiteur + csv_sep
    resultat += delimiteur + self.genre + delimiteur + csv_sep
    resultat += delimiteur + self.prenom + delimiteur + csv_sep
    resultat += delimiteur + self.nom + delimiteur + csv_sep
    resultat += delimiteur + self.date_naissance + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_commune) + delimiteur + csv_sep
    resultat += delimiteur + self.rue + delimiteur + csv_sep
    resultat += delimiteur + self.telephone + delimiteur + csv_sep
    resultat += delimiteur + self.telephone2 + delimiteur + csv_sep
    resultat += delimiteur + self.courriel + delimiteur + csv_sep
    resultat += delimiteur + str(self.cdb) + delimiteur + csv_sep
    resultat += delimiteur + self.num_licence + delimiteur
    return resultat

class Connexion:
  def __init__(self):
    self.code_membre = 0
    self.identifiant  = ""
    self.mot_passe = ""
    self.date_mot_passe = ""
    self.actif = 0
    self.date_actif = ""
    self.connexion = 0
    self.date_connexion = ""
    self.date_creation = ""

  def remplir(self, membre_v1):
    self.code_membre = membre_v1.code
    self.identifiant = membre_v1.identifiant
    self.mot_passe = "azertyiop"
    self.actif = membre_v1.actif
    
    self.connexion = membre_v1.connexion
    if membre_v1.derniere_connexion == "0000-00-00 00:00:00":
      self.date_connexion = "1990-01-01 00:00:01"
    else:
      self.date_connexion = membre_v1.derniere_connexion
    if membre_v1.code < 2000:
      self.date_creation = "2014-01-01"
    elif membre_v1.prenom == "z":
      self.date_creation = membre_v1.derniere_connexion
    else:
      annee = 2000 + membre_v1.code // 1000
      self.date_creation = str(annee) + "-01-01 00:00:01"

    self.date_actif = self.date_creation
    self.date_mot_passe = "2024-06-13 21:44:00"
    return
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code_membre) + delimiteur + csv_sep
    resultat += delimiteur + self.identifiant + delimiteur + csv_sep
    resultat += delimiteur + self.mot_passe + delimiteur + csv_sep
    resultat += delimiteur + self.date_mot_passe + delimiteur + csv_sep
    resultat += delimiteur + str(self.actif) + delimiteur + csv_sep
    resultat += delimiteur + self.date_actif + delimiteur + csv_sep
    resultat += delimiteur + str(self.connexion) + delimiteur + csv_sep
    resultat += delimiteur + self.date_connexion + delimiteur + csv_sep
    resultat += delimiteur + self.date_creation + delimiteur

    return resultat

# =============================================================================
if __name__ == "__main__":

  nom_fichier_membres_v1 = "membres" + "."  + extension_fichier
  chemin_fichier_membres_v1 = os.path.join(dossier_v1, nom_fichier_membres_v1)

  nom_fichier_membres_v2 = "membres" + "."  + extension_fichier
  chemin_fichier_membres_v2 = os.path.join(dossier_v2, nom_fichier_membres_v2)

  nom_fichier_connexion = "connexions" + "."  + extension_fichier
  chemin_fichier_connexion = os.path.join(dossier_v2, nom_fichier_connexion)

  chemin_fichier_mdp = os.path.join(dossier_v2, "rsbl_connexions-mot_passe.bin")
  fichier_mdp = open(chemin_fichier_mdp, "r")
  mdp = fichier_mdp.read()

  nb_v1 = 0
  nb_v2 = 0
  with open(chemin_fichier_membres_v1, "r") as membres_v1, open(chemin_fichier_membres_v2, "w") as membres_v2, open(chemin_fichier_connexion, "w") as connexions:
    for ligne_v1 in membres_v1:

      # Lecture fichier des donnees de la v1
      ligne_v1 = ligne_v1.replace(eol, '')
      if len(ligne_v1) > 0:
        nb_v1 += 1
        ligne_v1 = ligne_v1.replace('"', '')
        donnee_v1 =  ligne_v1.split(csv_sep)
        membre_v1 = Membre_v1()
        membre_v1.remplir(donnee_v1)

        membre_v2 = Membre_v2()
        membre_v2.remplir(membre_v1)
        connexion = Connexion()
        connexion.remplir(membre_v1)
        connexion.mot_passe = mdp

        # Filtre conservation des enregistrements de la v1 en v2
        conserve =  True
        if (membre_v2.code > 9050 and membre_v2.code < 9100):
          conserve = False
        if connexion.identifiant == 'xxx.yyyy':
          conserve = False
        
        # Ecriture des fichiers de donnees de la v2
        if conserve:
          nb_v2 += 1
          ligne_membre_v2  = membre_v2.formatter_ligne()
          membres_v2.write(ligne_membre_v2 + eol)
          print(ligne_membre_v2)
          ligne_connexion = connexion.formatter_ligne()
          connexions.write(ligne_connexion + eol)
          print(ligne_connexion)

        #print(donnee_v1)
  print(f"nombre conservés : {nb_v2} / {nb_v1}")
# end of file
# ==============================================================================
