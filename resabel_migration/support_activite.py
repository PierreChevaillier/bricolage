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
# revision:
# ------------------------------------------------------------------------------
# comments:
# -  
# warnings:
# - 
# todos:
#  - test it and then test it again
# ==============================================================================

import os

eol = '\n' # SEE: https://docs.python.org/3/library/os.html (see os.linesep)
csv_sep = ';' # to avoid confusion between french decimal sep (,) and field separator
extension_fichier = 'csv'
delimiteur = '"'

# ==============================================================================
# --- Chemins d'acces aux fichiers en relatif / dossier racine
dossier_racine = './../../bdd_resabel'
dossier = dossier_racine + '/' + 'v2_' + '2024-06-13'

# ==============================================================================
# --- Structures de donnees
#"code","numero","code_type_support","nom","modele","constructeur","annee_construction","fichier_image","actif","code_site_base","nombre_postes","competition","loisir","nb_initiation_min","nb_initiation_max"
# Table de la version 2
class Support_Activite:

  numero_code = {}
  site = {}

  def __init__(self):
    self.code = 0
    self.numero = ""
    self.code_site = 0

  def remplir(self, donnee):
    self.code = int(donnee[0])
    self.numero = donnee[1]
    self.code_site = donnee[9]
    return

  def lire_fichier():
    nom_fichier = "rsbl_supports" + "."  + extension_fichier
    chemin_fichier = os.path.join(dossier, nom_fichier)

    with open(chemin_fichier, "r") as fichier:
      for ligne in fichier:
        ligne = ligne.replace(eol, '')
        if len(ligne) > 0:
          ligne = ligne.replace('"', '')
          donnee =  ligne.split(csv_sep)
          support = Support_Activite()
          support.remplir(donnee)
          Support_Activite.numero_code[support.numero] = support.code
          Support_Activite.site[support.code] = support.code_site
          print(ligne)
          print("numero:"  + support.numero + " => " + str(support.code))
    return

# =============================================================================
if __name__ == "__main__":

  Support_Activite.lire_fichier()
  print(Support_Activite.numero_code)

#  end of file
# ==============================================================================
