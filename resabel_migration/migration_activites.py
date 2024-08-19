# -*- coding: utf-8 -*-
# ==============================================================================
# context: Resabel - systeme de REServAtion de Bateau En Ligne 
#   migration base de données v1 vers v2
# description: script de transformation de donnes
#  - source : fichier inscriptions_sortie.csv, export de la table membres de resabel v1
#             puis TRIE (jour, creneau) ascendant et cdb descendant
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
# creation: 20-juin-2024 pchevaillier@gmail.com
# revision: 18-aug-2024 pchevaillier@gmail.com filtre / date_debut_migration
# ------------------------------------------------------------------------------
# comments:
# -  seules sont traitees les sorties des bateaux references 
#    dans la table rsbl_supports
# warnings:
# - Pas de gestion heure d'hiver / heure d'ete (cf. variable heure_ouverture)
# - ATTENTION : inscriptions_sortie.csv doit etre prealablement TRIE 
# todos:
#  - test it and then test it again
# ==============================================================================

import os
import sys
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

heure_ouverture = 9.0
duree_creneau = 1.0

date_debut_migration = datetime(year=2024,month=6,day=1)

# Table de la version 1
# "1425078000";"0";"63";"1";"0"
# "jour";"creneau";"code_bateau";"code_membre";"cdb"
class Sortie:
  def __init__(self):
    self.jour = 0
    self.creneau = 0
    self.code_bateau = ""
    self.code_membre = 0
    self.cdb = 0

  def remplir(self, donnee):
    self.jour = int(donnee[0])
    self.creneau = int(donnee[1])
    self.code_bateau = donnee[2]
    self.code_membre = int(donnee[3])
    self.cdb = int(donnee[4])
    return
  
  def meme_sortie(self, sortie):
    return self.jour == sortie.jour and self.creneau == sortie.creneau and self.code_bateau == sortie.code_bateau
  
  def est_valide(self):
    jour = datetime.fromtimestamp(self.jour)
    condition = jour >= date_debut_migration
    if condition:
      condition = condition and self.code_bateau in Support_Activite.numero_code
      if not condition:
        jour_texte = jour.isoformat()
        print("support non referencé: " + self.code_bateau + " pour sortie du " + jour_texte)
    return condition
  
# Tables de la version 2
class Seance_Activite:
  def __init__(self):
    self.code = 0
    self.code_site = 1
    self.code_support = 0
    self.date_debut = None
    self.date_fin = None
    self.code_responsable = None
    self.information = "import v1"

  def remplir(self, code_seance, sortie):
    self.code = code_seance

    self.code_support = Support_Activite.numero_code[sortie.code_bateau]
    self.code_site = Support_Activite.site[self.code_support]

    jour = datetime.fromtimestamp(sortie.jour)
    heure_creneau_debut = heure_ouverture + (sortie.creneau) * duree_creneau
    heure_debut = timedelta(hours = heure_creneau_debut)
    self.date_debut = jour + heure_debut

    heure_creneau_fin = heure_ouverture + (sortie.creneau + 1) * duree_creneau
    heure_fin = timedelta(hours = heure_creneau_fin)
    self.date_fin = jour + heure_fin

    if sortie.cdb == 1:
      self.code_responsable = sortie.code_membre
    return
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_site) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_support) + delimiteur + csv_sep

    date_sql = self.date_debut.isoformat()
    date_sql = date_sql.replace('T', ' ')
    resultat += delimiteur + date_sql + delimiteur + csv_sep

    date_sql = self.date_fin.isoformat()
    date_sql = date_sql.replace('T', ' ')
    resultat += delimiteur + date_sql + delimiteur + csv_sep

    if self.code_responsable == None:
      resultat += "NULL" + csv_sep
    else:
      resultat += delimiteur + str(self.code_responsable) + delimiteur + csv_sep

    resultat += delimiteur + self.information + delimiteur
    return resultat

# 
class Participation_Activite:
  def __init__(self):
    self.code_seance = 0
    self.code_membre = 0
    self.information  = "import v1"
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code_seance) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_membre) + delimiteur + csv_sep
    resultat += delimiteur + self.information + delimiteur
    return resultat

# =============================================================================
if __name__ == "__main__":

  print("Migration des sorties apres le " + date_debut_migration.isoformat())

  Support_Activite.lire_fichier();
  print(Support_Activite.numero_code)
  print(Support_Activite.site)

  nom_fichier_sorties = "inscriptions_sortie" + "."  + extension_fichier
  chemin_fichier_sorties = os.path.join(dossier_v1, nom_fichier_sorties)

  nom_fichier_seances = "seances_activite" + "."  + extension_fichier
  chemin_fichier_seances = os.path.join(dossier_v2, nom_fichier_seances)

  nom_fichier_participations = "participations_seances" + "."  + extension_fichier
  chemin_fichier_participations = os.path.join(dossier_v2, nom_fichier_participations)

  nb_sortie = 0
  code_seance = 0
  nb_participation = 0

  with open(chemin_fichier_sorties, "r") as sorties, open(chemin_fichier_seances, "w") as seances, open(chemin_fichier_participations, "w") as participations:
    sortie = Sortie()

    for ligne_sortie in sorties:

      ligne_sortie = ligne_sortie.replace(eol, '')
      if len(ligne_sortie) > 0:
        nb_sortie += 1
        ligne_sortie = ligne_sortie.replace('"', '')
        donnee_v1 =  ligne_sortie.split(csv_sep)
        nouvelle_sortie = Sortie()
        nouvelle_sortie.remplir(donnee_v1)
        if nouvelle_sortie.est_valide():
          if not nouvelle_sortie.meme_sortie(sortie):
            code_seance += 1
            seance = Seance_Activite()
            seance.remplir(code_seance, nouvelle_sortie)
            ligne_seance = seance.formatter_ligne()
            seances.write(ligne_seance + eol)
            sortie = nouvelle_sortie
          nb_participation += 1
          participation = Participation_Activite()
          participation.code_seance = code_seance
          participation.code_membre = nouvelle_sortie.code_membre
          participation.information = "import v1"
          ligne_participation = participation.formatter_ligne()
          participations.write(ligne_participation + eol)
        #print(donnee_v1)
  print(f"nombre de séances conservées : {code_seance} avec {nb_participation} participations pour {nb_sortie} sorties en v1")

# end of file
# ==============================================================================
