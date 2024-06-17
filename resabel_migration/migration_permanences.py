# -*- coding: utf-8 -*-
# ==============================================================================
# context: Resabel - systeme de REServAtion de Bateau En Ligne 
#   migration base de donnees v1 vers v2
# description: script de transformation de donnees
#  - objet : equipe des responsables de permanence
#  - source : fichier roles_membres.csv, export de la table roles_membres de resabel v1
#  - fichiers produits : roles_membres.csv correspondant
#    a la table rsbl_roles_membres de la base de donnees v2
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
# creation: 17-juin-2024 pchevaillier@gmail.com
# revision:
# ------------------------------------------------------------------------------
# comments:
# - la table de la v2 a la meme structure que dans la v1, mais pas memes types de donnees
# - le script pourrait etre plus simple mais privilegie 1 structure plus generique 
# warnings:
# - ne traite que le role "responsable" de la composante "Permamence"
# - suite a bug de la v1, il faut filtrer les enregistrements errones (code_membre = 0)
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
dossier_v1 = dossier_racine + '/' + 'v1_' + '2024-06-13'
dossier_v2 = dossier_racine + '/' + 'v2_' + '2024-06-13'

# ==============================================================================
# --- Structures de donnees

code_resp_v1 = "resp"
code_resp_v2 = 13
code_composante_permanence_v1 = "permanence"
code_composante_perm_v2 = 11

# Table de la version 1
class Role_Membre_v1:
  def __init__(self):
    self.code_membre = 0
    self.role = ""
    self.composante = ""
    self.rang = 0

  def remplir(self, donnee):
    self.code_membre = int(donnee[0])
    self.role = donnee[1]
    self.composante = donnee[2]
    self.rang = int(donnee[3])
    return
  
  def est_resp_permanence(self):
    # bug de la v1 : il y a des enregistrements invalide (code_membre = 0)
    condition = self.code_membre > 0 and self.role == code_resp_v1 and self.composante == code_composante_permanence_v1
    return condition

# Table de la version 2
class Role_Membre_v2:
  def __init__(self):
    self.code_membre = 0
    self.code_role = 0
    self.code_composante = 0
    self.rang = 0

  def remplir(self, role_membre_v1):
    self.code_membre = role_membre_v1.code_membre
    self.code_role = code_resp_v2
    self.code_composante = code_composante_perm_v2
    self.rang = role_membre_v1.rang
    return
  
  def formatter_ligne(self):
    resultat = ""
    resultat += delimiteur + str(self.code_membre) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_role) + delimiteur + csv_sep
    resultat += delimiteur + str(self.code_composante) + delimiteur + csv_sep
    resultat += delimiteur + str(self.rang) + delimiteur
    return resultat

# =============================================================================
if __name__ == "__main__":

  nom_fichier_v1 = "roles_membres" + "."  + extension_fichier
  chemin_fichier_v1 = os.path.join(dossier_v1, nom_fichier_v1)

  nom_fichier_v2 = "roles_membres" + "."  + extension_fichier
  chemin_fichier_v2 = os.path.join(dossier_v2, nom_fichier_v2)

  with open(chemin_fichier_v1, "r") as fichier_v1, open(chemin_fichier_v2, "w") as fichier_v2:
    for ligne_v1 in fichier_v1:

      # Lecture fichier des donnees de la v1
      ligne_v1 = ligne_v1.replace(eol, '')
      if len(ligne_v1) > 0:
        ligne_v1 = ligne_v1.replace('"', '')
        donnee_v1 =  ligne_v1.split(csv_sep)
        role_membre_v1 = Role_Membre_v1()
        role_membre_v1.remplir(donnee_v1)

        if role_membre_v1.est_resp_permanence():
          role_membre_v2 = Role_Membre_v2()
          role_membre_v2.remplir(role_membre_v1)       
          ligne_v2  = role_membre_v2.formatter_ligne()
          fichier_v2.write(ligne_v2 + eol)
          print(ligne_v2)
 
#  end of file
# ==============================================================================
