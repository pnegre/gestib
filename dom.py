
from sets import Set
from xml.dom.minidom import parse, parseString

from gestib.models import *
from utils import *


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

            # Professor ja actiu? Impossible
            if p.actiu:
                incidencies.append("FATAL: professor duplicat ACTIU: %s", codi_prof)
                continue

            # Professor ja existeix amb un altre nom i mateix codi?
            if not esProfessorDuplicat(prof, p):
                incidencies.append("Prof duplicat: %s", codi_prof)

        except Professor.DoesNotExist:
            p = Professor(
                codi = prof.getAttribute('codi'),
                nom = prof.getAttribute('nom'),
                llinatge1 = prof.getAttribute('ap1'),
                llinatge2 = prof.getAttribute('ap2'),
            )
            nprofes += 1

        p.actiu = True
        p.save()

    return nprofes


def importCursos(incidencies, dom, anny):
    ncursos = 0
    ngrups = 0
    cursos = dom.getElementsByTagName('CURS')
    for curs in cursos:
        try:
            c = Curs.objects.get(codi=curs.getAttribute('codi'), anny=anny)
        except Curs.DoesNotExist:
            c = Curs(nom=curs.getAttribute('descripcio'),codi=curs.getAttribute('codi'),anny=anny)
            c.save()
            ncursos += 1

        c.actiu = True
        c.save()

        grups = curs.getElementsByTagName('GRUP')
        if len(grups) == 0:
            incidencies.append("Curs %s no te grups" % (curs.getAttribute('descripcio')))
        for grup in grups:
            tutor = None
            try:
                tutor = Professor.objects.get(codi=grup.getAttribute('tutor'))
            except Professor.DoesNotExist:
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



def importAlumnes(incidencies, dom, anny):
    nalumnes = 0
    nmats = 0
    alumnes = dom.getElementsByTagName('ALUMNE')
    for alumne in alumnes:
        exp = alumne.getAttribute('expedient')

        try:
            # Ja existeix un alumne amb aquest expedient?
            alm = Alumne.objects.get(expedient=alumne.getAttribute('expedient'))

            # Si l'alumne ja estava activat, problema fatal. No el matriculem
            if alm.actiu == True:
                v1 = "%s %s, %s. Exp %s"  % (alm.llinatge1, alm.llinatge2, alm.nom, alm.expedient)
                v2 = "%s %s, %s" % (alumne.getAttribute('ap1'), alumne.getAttribute('ap2'), alumne.getAttribute('nom'))
                incidencies.append("FATAL: Expedients ACTIUS duplicats..." + v1 + " --- " + v2)
                continue

            # Si el nom o llinatges no coincideixen, tenim una incidencia.
            #if alm.nom == alumne.getAttribute('nom') or alm.llinatge1 != alumne.getAttribute('ap1') or alm.llinatge2 != alumne.getAttribute('ap2'):
            if not esAlumneDuplicat(alumne, alm):
                v1 = "%s %s, %s. Exp %s"  % (alm.llinatge1, alm.llinatge2, alm.nom, alm.expedient)
                v2 = "%s %s, %s" % (alumne.getAttribute('ap1'), alumne.getAttribute('ap2'), alumne.getAttribute('nom'))
                incidencies.append("Expedients duplicats..." + v1 + " --- " + v2)

            alm.actiu = True
            alm.save()

        # L'alumne no existeix. El creem
        except Alumne.DoesNotExist:
            nom = alumne.getAttribute('nom')
            l1 = alumne.getAttribute('ap1')
            l2 = alumne.getAttribute('ap2')
            alm = Alumne(nom=nom,llinatge1=l1,llinatge2=l2,expedient=exp,actiu=True)
            alm.save()
            nalumnes += 1

        # Matriculem l'alumne al grup que toca
        # Suposem que les matricules d'aquest any estan esborrades... (ho fem abans de comencar l'importacio)
        try:
            grup = Grup.objects.get(codi=alumne.getAttribute('grup'))
            mt = Matricula(alumne=alm, anny=anny, grup=grup)
            mt.save()
            nmats += 1

        except Grup.DoesNotExist:
            incidencies.append("Alumne %s no te grup assignat" % (alm))

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

    print data
    for cg in data.keys():
        try:
            grup = Grup.objects.get(codi=cg)
        except Grup.DoesNotExist:
            continue

        for cs in data[cg]:
            try:
                submateria = Submateria.objects.get(codi=cs)
                try:
                    grup.submateries.add(submateria)
                    nsubmatgrup += 1
                except:
                    pass
            except Submateria.DoesNotExist:
                pass

        grup.save()

    return nsubmatgrup
