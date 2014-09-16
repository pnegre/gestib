
from xml.dom.minidom import parse, parseString

from gestib.models import *


def getYear(dom):
    root = dom.getElementsByTagName('CENTRE_EXPORT')
    for r in root:
        anny = r.getAttribute('any')
        return int(anny)


def importProfessors(dom):
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


def importCursos(dom, anny):
    cursos = dom.getElementsByTagName('CURS')
    for curs in cursos:
        cu = Curs.objects.filter(codi=curs.getAttribute('codi'), anny=anny)
        if cu == None or len(cu) == 0:
            c = Curs(nom=curs.getAttribute('descripcio'),codi=curs.getAttribute('codi'),anny=anny)
            c.save()
        else:
            c = cu[0]

        grups = curs.getElementsByTagName('GRUP')
        for grup in grups:
            try:
                Grup.objects.get(codi=grup.getAttribute('codi'))

            except:
                try:
                    prof = Professor.objects.get(codi=grup.getAttribute('tutor'))
                except:
                    continue

                g = Grup(
                    nom = grup.getAttribute('nom'),
                    curs = c,
                    tutor = prof,
                    codi = grup.getAttribute('codi'),
                )
                g.save()

def importAlumnes(dom, anny):
    alumnes = dom.getElementsByTagName('ALUMNE')
    for alumne in alumnes:
        if Alumne.objects.filter(expedient=alumne.getAttribute('expedient')): continue

        nom = alumne.getAttribute('nom')
        l1 = alumne.getAttribute('ap1')
        l2 = alumne.getAttribute('ap2')
        exp = alumne.getAttribute('expedient')
        gp = Grup.objects.filter(codi=alumne.getAttribute('grup'))
        if gp == None: continue
        if len(gp) == 0: continue

        a = Alumne(nom=nom,llinatge1=l1,llinatge2=l2,expedient=exp,grup=gp[0])
        a.save()

# No emprar, per ara
# Hi ha problemes en importar
def importSubmateries(dom):
    submateries = dom.getElementsByTagName('SUBMATERIES')[0].getElementsByTagName('SUBMATERIA')
    sessions = dom.getElementsByTagName('HORARIP')[0].getElementsByTagName('SESSIO')
    for submateria in submateries:
        codi = submateria.getAttribute('codi')
        descripcio = submateria.getAttribute('descripcio')
        nom = submateria.getAttribute('curta')
        curs = Curs.objects.filter(codi=submateria.getAttribute('curs'))
        grup = None

        for s in sessions:
            sm = s.getAttribute('submateria')
            g = s.getAttribute('grup')
            if sm == codi:
                gr = Grup.objects.filter(codi=g)
                if gr:
                    grup=gr[0]
                    break

        if grup == None: continue

        sbm = Submateria(nom=nom,descripcio=descripcio,codi=codi,curs=curs[0],grup=grup)
        sbm.save()
