# -*- coding: utf-8 -*-

def cons(s):
    consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
    return filter(lambda x: x in consonants, s)

# Comprova que els noms i els llinatges no son els mateixos, ignorant els caracters no-consonants
def esAlumneDuplicat(alumne, alBD):
    if cons(alumne.getAttribute('nom')) != cons(alBD.nom):
        return False
    if cons(alumne.getAttribute('ap1')) != cons(alBD.llinatge1):
        return False
    if cons(alumne.getAttribute('ap2')) != cons(alBD.llinatge2):
        return False

    return True

# Comprova que els noms i els llinatges no son els mateixos, ignorant els caracters no-consonants
def esProfessorDuplicat(prof, profBD):
    if cons(prof.getAttribute('nom')) != cons(profBD.nom):
        return False
    if cons(prof.getAttribute('ap1')) != cons(profBD.llinatge1):
        return False
    if cons(prof.getAttribute('ap2')) != cons(profBD.llinatge2):
        return False

    return True
