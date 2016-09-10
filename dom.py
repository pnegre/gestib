
from sets import Set
from xml.dom.minidom import parse, parseString

from gestib.models import *


def getYear(dom):
    root = dom.getElementsByTagName('CENTRE_EXPORT')
    for r in root:
        anny = r.getAttribute('any')
        return int(anny)


def importProfessors(incidencies, dom):
    nprofes = 0
    professors = dom.getElementsByTagName('PROFESSOR')
    for prof in professors:
        codi_prof = prof.getAttribute('codi')
        try:
            p = Professor.objects.get(codi=codi_prof)
            # El professor ja existeix. L'activem
            p.actiu = True
            continue

        except Professor.DoesNotExist:
            p = Professor(
                codi = prof.getAttribute('codi'),
                nom = prof.getAttribute('nom'),
                llinatge1 = prof.getAttribute('ap1'),
                llinatge2 = prof.getAttribute('ap2'),
                actiu = True,
            )
            nprofes += 1

        p.save()
    
    return nprofes


def importCursos(incidencies, dom, anny):
    ncursos = 0
    ngrups = 0
    cursos = dom.getElementsByTagName('CURS')
    for curs in cursos:
        cu = Curs.objects.get(codi=curs.getAttribute('codi'), anny=anny)
        if cu == None:
            c = Curs(nom=curs.getAttribute('descripcio'),codi=curs.getAttribute('codi'),anny=anny)
            c.save()
            ncursos += 1
        else:
            c = cu

        c.actiu = True
        c.save()

        grups = curs.getElementsByTagName('GRUP')
        if len(grups) == 0:
            incidencies.append("Curs %s no te grups" % (curs.getAttribute('descripcio')))
        for grup in grups:
            tutor = None
            try:
                tutor = Professor.objects.get(codi=grup.getAttribute('tutor'))
            except:
                incidencies.append("Grup %s-%s no te tutor" % (curs.getAttribute('descripcio'), grup.getAttribute('nom')))

            try:
                g = Grup.objects.get(codi=grup.getAttribute('codi'))
                if tutor:
                    g.tutor = tutor
                    g.actiu = True
                    g.save()

            except Grup.DoesNotExist:
                g = Grup(
                    nom = grup.getAttribute('nom'),
                    curs = c,
                    codi = grup.getAttribute('codi'),
                    actiu = True
                )
                if tutor:
                    g.tutor = tutor

                g.save()
                ngrups += 1

    return ncursos, ngrups

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

    #
    # if alumne.getAttribute('ap1').encode('ascii', errors='ignore') != alBD.llinatge1.encode('ascii', errors='ignore'):
    #     return False
    # if alumne.getAttribute('ap2').encode('ascii', errors='ignore') != alBD.llinatge2.encode('ascii', errors='ignore'):
    #     return False

    return True

def importAlumnes(incidencies, dom, anny):
    nalumnes = 0
    nmats = 0
    alumnes = dom.getElementsByTagName('ALUMNE')
    for alumne in alumnes:
        exp = alumne.getAttribute('expedient')

        try:
            # Alerta. Hem de comprovar QUANTS d'alumnes hi ha amb expedient duplicats?

            # Ja existeix un alumne amb aquest expedient?
            alm = Alumne.objects.get(expedient=alumne.getAttribute('expedient'))

            # Si l'alumne ja estava activat, problema fatal. No el matriculem
            if alm.actiu == True:
                incidencies.append("FATAL: expedients actius duplicats: %s" % exp)
                continue

            # Si el nom o llinatges no coincideixen, tenim una incidencia.
            #if alm.nom == alumne.getAttribute('nom') or alm.llinatge1 != alumne.getAttribute('ap1') or alm.llinatge2 != alumne.getAttribute('ap2'):
            if not esAlumneDuplicat(alumne, alm):
                v1 = "%s %s, %s. Exp %s"  % (alm.llinatge1, alm.llinatge2, alm.nom, alm.expedient)
                v2 = "%s %s, %s" % (alumne.getAttribute('ap1'), alumne.getAttribute('ap2'), alumne.getAttribute('nom'))
                incidencies.append("Expedients duplicats..." + v1 + " --- " + v2)

            alm.actiu = True
            alm.save()

        except Alumne.DoesNotExist:
            nom = alumne.getAttribute('nom')
            l1 = alumne.getAttribute('ap1')
            l2 = alumne.getAttribute('ap2')
            alm = Alumne(nom=nom,llinatge1=l1,llinatge2=l2,expedient=exp,actiu=True)
            alm.save()
            nalumnes += 1

        gp = Grup.objects.filter(codi=alumne.getAttribute('grup'))
        if gp == None or len(gp) == 0:
            incidencies.append("Alumne %s no te grup assignat" % (alm))
            continue

        grup = gp[0]

        try:
            mt = Matricula.objects.get(alumne=alm, anny=anny, grup=grup)
        except Matricula.DoesNotExist:
            mt = Matricula(alumne=alm, anny=anny, grup=grup)
            mt.save()
            nmats += 1

    return nalumnes, nmats




def importSubmateries(dom, anny):
    nsubs = 0
    submateries = dom.getElementsByTagName('SUBMATERIES')[0].getElementsByTagName('SUBMATERIA')
    for submateria in submateries:
        codi = submateria.getAttribute('codi')
        descripcio = submateria.getAttribute('descripcio')
        curta = submateria.getAttribute('curta')
        nom = submateria.getAttribute('curta')
        curs = None
        try:
            curs = Curs.objects.get(codi=submateria.getAttribute('curs'), anny=anny)
        except:
            pass

        try:
            sbm = Submateria.objects.get(codi=codi, curs=curs)
        except Submateria.DoesNotExist:
            sbm = Submateria(nom=nom,descripcio=descripcio,curta=curta,codi=codi,curs=curs)
            sbm.save()
            nsubs += 1

    return nsubs


def importSubmateriesGrup(dom):
    nsubmatgrup = 0
    horgs = dom.getElementsByTagName('HORARIG')[0].getElementsByTagName('SESSIO')
    data = {}
    for ses in horgs:
        cgrup = ses.getAttribute('grup')
        csubmat = ses.getAttribute('submateria')
        if not cgrup in data.keys():
            data[cgrup] = Set([ csubmat ])
        else:
            data[cgrup].add(csubmat)

    for cg in data.keys():
        try:
            grup = Grup.objects.get(codi=cg)
        except Grup.DoesNotExist:
            continue

        for cs in data[cg]:
            try:
                submateria = Submateria.objects.get(codi=cs)
                try:
                    SubmateriaGrup.objects.get(submateria=submateria, grup=grup)
                except SubmateriaGrup.DoesNotExist:
                    obj = SubmateriaGrup(submateria=submateria, grup=grup)
                    obj.save()
                    nsubmatgrup += 1
            except Submateria.DoesNotExist:
                pass

    return nsubmatgrup
