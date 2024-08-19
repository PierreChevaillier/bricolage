# -*- coding: utf-8 -*-
# ==============================================================================
# context: Resabel - systeme de REServAtion de Bateau En Ligne 
#   migration base de donnees v1 vers v2
# description: script de transformation de donnees
#  - source : fichier evenements_bateaux.csv, export de la table evenements_bateaux de resabel v1
#  - fichiers produits : indisponibilites_bateau.csv correspondant
#    a la table rsbl_indisponibilites de la base de donnees v2
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
# creation: 20-juin-2024 pchevaillier@gmail.com
# revision: 18-aug-2024 pchevaillier@gmail.com filtre / date_debut_migration
# ------------------------------------------------------------------------------
# comments:
# -  seules sont traitees les indisponibilites des bateaux references 
#    dans la table rsbl_supports
# warnings:
# - Pas de gestion heure d'hiver / heure d'ete (cf. variable heure_ouverture)
# todos:
#  - test it and then test it again
# ==============================================================================

import os
from datetime import datetime
from datetime import timedelta

from support_activite import Support_Activite

eol = '\n' # SEE: https://docs.python.org/3/library/os.html (see os.linesep)
csv_sep = ';' # to avoid confusion between french decimal sep (,) and field separator
extension_fichier = 'csv'
delimiteur = '"'

# ==============================================================================
# --- Chemins d'acces aux fichiers en relatif / dossier racine
dossier_racine = './../../bdd_resabel'
dossier_v1 = dossier_racine + '/' + 'v1_' + '2024-08-26'
dossier_v2 = dossier_racine + '/' + 'v2_' + '2024-08-26'

# ==============================================================================
# --- Structures de donnees

date_debut_migration = datetime(year=2024,month=6,day=1)

# correspondance codage
#table agenda de v1 (n'existe pas en v2)
# "compet";"compet";"Réservation pour une compétition";"compet"
#"entretien";"entret";"Entretien du matériel";"entretien"
#"rando";"rando";"Réservation pour une randonnée";"randonnée"
#"secu";"bureau";"mauvaises conditions de navigation";"sécurité"
#"maree";"bureau";"basses mers de grandes marées";"grand coef"
#"jpo";"bureau";"Journée portes ouvertes - découverte";"portes ouv"
#"form";"formation";"Séance de formation";"Formation"
#"stage";"formation";"Stage de formation";"Stage"

# table motif (v2)
#"1","1","7","Réservation pour compétition","Compétition"
#"2","2","7","Compétition sur le site","Site compétition"
#"3","1","10","Réservation pour une randonnée","Randonnée"
#"4","1","4","Prêt de la coque","Prêt coque"
#"5","1","8","Entretien régulier du matériel","Entretien"
#"6","1","8","Réparation du matériel","Réparation"
#"7","1","8","Hors site pour hivernage","Hivernage"
#"8","1","6","Séance de formation des jeunes","Formation jeunes"
#"9","1","6","Séance de formation","Séance formation"
#"10","1","6","Stage de formation/perfectionnement","Stage"
#"11","1","4","Journée portes ouvertes","Portes ouvertes"
#"12","1","4","Découverte de l'aviron","Découverte"
#"13","1","4","Séance Aviron santé","Aviron santé"
#"14","2","4","Mauvaises conditions de navigation","Sécurité"
#"15","2","4","Basse mer de grandes marées","Grande marée"
codage_motif = {"compet": 1, "rando": 3, "entretien": 5, "form": 9, "stage": 10, "jpo": 11, "secu": 14, "maree": 15}

heure_ouverture = 9.0
duree_creneau = 1.0

# Table de la version 1
class Evenement_Bateau:
  def __init__(self):
    self.identifiant = ""
    self.portee = ""
    self.code_bateau = ""
    self.jour_debut = 0
    self.creneau_debut = 0
    self.jour_fin = 0
    self.creneau_fin = 0
    self.agenda = ""
    self.information = ""

  def remplir(self, donnee):
    self.identifiant = donnee[0]
    self.portee = donnee[1]
    self.code_bateau = donnee[2]
    self.jour_debut = int(donnee[3])
    self.creneau_debut = int(donnee[4])
    self.jour_fin = int(donnee[5])
    self.creneau_fin= int(donnee[6])
    self.agenda = donnee[7]
    self.information = donnee[8]
    return
  
  def est_valide(self):
    jour = datetime.fromtimestamp(self.jour_fin)
    condition = jour >= date_debut_migration
    if condition:
      condition = condition and self.code_bateau in Support_Activite.numero_code
      if not condition:
        print("support non referencé: " + self.code_bateau)
    return condition
  
# Table de la version 2
class Indisponibilite_Support:
  def __init__(self):
    self.code = 0
    self.code_type = 1
    self.nom_classe = "Indisponibilite_Support"
    self.date_creation = None
    self.code_createur = 0
    self.code_motif = 0
    self.code_objet = 0
    self.date_debut = ""
    self.date_fin = ""
    self.information = ""

  def remplir(self, code, evenement):
    self.code = code
    self.date_creation = datetime.fromisoformat(evenement.identifiant)
    cle = evenement.agenda
    self.code_motif = codage_motif[cle]
    code_support = Support_Activite.numero_code[evenement.code_bateau]
    self.code_objet = code_support
    self.information = evenement.information

    jour_debut = datetime.fromtimestamp(evenement.jour_debut)
    heure_creneau_debut = heure_ouverture + (evenement.creneau_debut) * duree_creneau
    heure_debut = timedelta(hours = heure_creneau_debut)
    self.date_debut = jour_debut + heure_debut

    jour_fin = datetime.fromtimestamp(evenement.jour_fin)
    heure_creneau_fin = heure_ouverture + (evenement.creneau_fin + 1) * duree_creneau
    heure_fin = timedelta(hours = heure_creneau_fin)
    self.date_fin = jour_fin + heure_fin

    return
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_type) + delimiteur + csv_sep
    resultat += delimiteur + str(self.nom_classe) + delimiteur + csv_sep

    date_sql = self.date_creation.isoformat()
    date_sql = date_sql.replace('T', ' ')
    resultat += delimiteur + date_sql + delimiteur + csv_sep

    resultat += "NULL" + csv_sep
    resultat += delimiteur + str(self.code_motif) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_objet) + delimiteur + csv_sep
    
    date_sql = self.date_debut.isoformat()
    date_sql = date_sql.replace('T', ' ')
    resultat += delimiteur + date_sql + delimiteur + csv_sep

    date_sql = self.date_fin.isoformat()
    date_sql = date_sql.replace('T', ' ')
    resultat += delimiteur + date_sql + delimiteur + csv_sep

    resultat += delimiteur + self.information + delimiteur
    return resultat

# =============================================================================
if __name__ == "__main__":

  Support_Activite.lire_fichier();
  print(Support_Activite.numero_code)

  nom_fichier_v1 = "evenements_bateaux" + "."  + extension_fichier
  chemin_fichier_v1 = os.path.join(dossier_v1, nom_fichier_v1)

  nom_fichier_v2 = "indisponibilites_support" + "."  + extension_fichier
  chemin_fichier_v2 = os.path.join(dossier_v2, nom_fichier_v2)

  with open(chemin_fichier_v1, "r") as fichier_v1, open(chemin_fichier_v2, "w") as fichier_v2:
    code_indispo = 0
    for ligne_v1 in fichier_v1:

      ligne_v1 = ligne_v1.replace(eol, '')
      if len(ligne_v1) > 0:
        ligne_v1 = ligne_v1.replace('"', '')
        donnee_v1 =  ligne_v1.split(csv_sep)
        evenement = Evenement_Bateau()
        evenement.remplir(donnee_v1)

        if evenement.est_valide():
          code_indispo += 1
          indispo = Indisponibilite_Support()
          indispo.remplir(code_indispo, evenement)       
          ligne_v2  = indispo.formatter_ligne()
          fichier_v2.write(ligne_v2 + eol)
          #print(ligne_v2)
    print(f"nombre d'indisponibilités conservées : {code_indispo}")

#  end of file
# ==============================================================================
