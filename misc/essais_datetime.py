# -*- coding: utf-8 -*-
# ==============================================================================
# context: source file template for python (personal usage)
# description: essais fonctions datetime
# copyright (c) 2024 Pierre Chevaillier. All rights reserved.
# ------------------------------------------------------------------------------
# usage: python <thisFileName>
# dependencies: python 3 (see import statements)
# used with:
#   - python 3.9.6 on macOS 13.6
#   - python 3.x on
# ------------------------------------------------------------------------------
# creation: 18-juin-2024 pchevaillier@gmail.com
# revision:
# ------------------------------------------------------------------------------
# comments:
# -
# warnings:
# - still under development - not fully tested
# - for personal usage only
# todos:
#  - test it and then test it again
# ==============================================================================
# "2024-05-25 22:41:30";"c";"60";"1720735200";"5";"1720735200";"10";"rando";"Randonnée AMP Le Trezhir-Le Conquet "
# "2024-06-08 13:07:55";"j";"628";"1717797600";"0";"1719784800";"11";"entretien";" "
from datetime import datetime
from datetime import timedelta

heure_ouverture = 8.5
duree_creneau = 1.0
heure_premier_creneau = timedelta(hours = heure_ouverture)

ts1 = 1720735200
j1 = datetime.fromtimestamp(ts1)
print(j1)
t1 = j1 + heure_premier_creneau
print(t1)

ts2 = 1719784800
j2 = datetime.fromtimestamp(ts2)
print(j2)
creneau = 11
h2 = heure_ouverture + (creneau + 1) * duree_creneau
tc2 = timedelta(hours = h2)
t2 = j2 + tc2
print(t2)

t3 = datetime.fromisoformat("2024-06-08 13:07:55")
print(t3)

# end of file
# ==============================================================================
