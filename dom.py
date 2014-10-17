
from xml.dom.minidom import parse, parseString

from gestib.models import *


def getYear(dom):
    root = dom.getElementsByTagName('CENTRE_EXPORT')
    for r in root:
        anny = r.getAttribute('any')
        return int(anny)


def importProfessors(dom):
    nprofes = 0
    professors = dom.getElementsByTagName('PROFESSOR')
    for prof in professors:
        codi_prof = prof.getAttribute('codi')
        if Professor.objects.filter(codi=codi_prof): continue

        p = Professor(
            codi = prof.getAttribute('codi'),
            nom = prof.getAttribute('nom'),
            llinatge1 = prof.getAttribute('ap1'),
            llinatge2 = prof.getAttribute('ap2'),
        )
        p.save()
        nprofes += 1

    return nprofes


def importCursos(dom, anny):
    ncursos = 0
    ngrups = 0
    cursos = dom.getElementsByTagName('CURS')
    for curs in cursos:
        cu = Curs.objects.filter(codi=curs.getAttribute('codi'), anny=anny)
        if cu == None or len(cu) == 0:
            c = Curs(nom=curs.getAttribute('descripcio'),codi=curs.getAttribute('codi'),anny=anny)
            c.save()
            ncursos += 1
        else:
            c = cu[0]

        grups = curs.getElementsByTagName('GRUP')
        for grup in grups:
            tutor = None
            try:
                tutor = Professor.objects.get(codi=grup.getAttribute('tutor'))
            except:
                pass

            try:
                g = Grup.objects.get(codi=grup.getAttribute('codi'))
                if tutor:
                    g.tutor = tutor
                    g.save()

            except Grup.DoesNotExist:
                g = Grup(
                    nom = grup.getAttribute('nom'),
                    curs = c,
                    codi = grup.getAttribute('codi'),
                )
                if tutor:
                    g.tutor = tutor

                g.save()
                ngrups += 1

    return ncursos, ngrups


def importAlumnes(dom, anny):
    nalumnes = 0
    nmats = 0
    alumnes = dom.getElementsByTagName('ALUMNE')
    for alumne in alumnes:
        exp = alumne.getAttribute('expedient')

        try:
            alm = Alumne.objects.get(expedient=alumne.getAttribute('expedient'))
        except Alumne.DoesNotExist:
            nom = alumne.getAttribute('nom')
            l1 = alumne.getAttribute('ap1')
            l2 = alumne.getAttribute('ap2')
            alm = Alumne(nom=nom,llinatge1=l1,llinatge2=l2,expedient=exp)
            alm.save()
            nalumnes += 1

        gp = Grup.objects.filter(codi=alumne.getAttribute('grup'))
        if gp == None: continue
        if len(gp) == 0: continue
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

        sbm = Submateria(nom=nom,descripcio=descripcio,curta=curta,codi=codi,curs=curs)
        sbm.save()
        nsubs += 1

    return nsubs
