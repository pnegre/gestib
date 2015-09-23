# -*- coding: utf-8 -*-

import random, string

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext

from gestib.dom import *

from gestib.models import *
from gestib.forms import *

# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))


# Mostra el form per importar dades de l'xml del gestib
@permission_required('gestib.importar_alumnes')
def importData(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            annyid = form.cleaned_data['anny']
            fle = form.cleaned_data['fle']
            anny = Any.objects.get(id=annyid)

            dom = parse(fle)
            if anny.any1 != getYear(dom):
                # Any acadèmic no correspon amb l'any del fitxer XML
                # TODO: Missatge d'error al form així com toca
                message = "Error in XML: els anys no coincideixen. XML: %d, bbdd: %d" % (anny.any1, getYear(dom))
                return renderResponse(request, 'gestib/missatge.html', {
                    'message': message
                })

            incidencies = []
            nprofs = importProfessors(incidencies, dom)
            ncursos, ngrups = importCursos(incidencies, dom, anny)
            nalumnes, nmats = importAlumnes(incidencies, dom, anny)
            # nsubs = importSubmateries(dom, anny)
            # nsubmatgrup = importSubmateriesGrup(dom)

            return renderResponse(request, 'gestib/import.html', {
                'finished': True,
                'nprofs': nprofs,
                'nalumnes': nalumnes,
                'ncursos': ncursos,
                'ngrups': ngrups,
                'incidencies': incidencies,
                # 'nmats': nmats,
                # 'nsubs': nsubs,
                # 'nsubmatgrup': nsubmatgrup
            })

    else:
        form = ImportForm()

    return renderResponse(request, 'gestib/import.html', {
        'form': form,
    } )

def stripchars(s):
    s = s.replace(u"á","a")
    s = s.replace(u"é","e")
    s = s.replace(u"í","i")
    s = s.replace(u"ó","o")
    s = s.replace(u"ú","u")
    s = s.replace(u"à","a")
    s = s.replace(u"è","e")
    s = s.replace(u"ì","i")
    s = s.replace(u"ò","o")
    s = s.replace(u"ù","u")
    s = s.replace(u"ñ","n")
    s = s.replace(u"ç","c")
    s = s.replace(" ", "")
    return s

def tractaAlumne(al):
    pwd = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
    l1 = stripchars(al.llinatge1.lower())
    l2 = stripchars(al.llinatge2.lower())
    nm = stripchars(al.nom.lower())
    username = nm[0] + l1 + l2[0]
    return "null@callisto.esliceu.com;Palma;%s;%s;%s;%s;%s\n" % (al.llinatge1, al.llinatge2, al.nom, username, pwd)

# Per consultar alumnes d'un grup
@permission_required('gestib.importar_alumnes')
def consultaGrup(request):
    any_actual = Any.objects.latest('any1')

    if request.method == 'POST':
        post = request.POST
        gid = post['grup']
        grup = Grup.objects.get(id=gid)
        result = "email;city;lastname1;lastname2;firstname;username;password_clear\n"
        for m in Matricula.objects.filter(anny=any_actual, grup=grup):
            result += tractaAlumne(m.alumne)

        response = HttpResponse(content = result, content_type='text/csv')
        filename = str(any_actual) + "." + str(grup) + ".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response
    else:
        cursos = Curs.objects.filter(anny=any_actual)
        grups = []
        for c in cursos:
            for g in Grup.objects.filter(curs=c):
                grups.append(g)

        return renderResponse(request, 'gestib/consulta.html', {
            'grups': grups,
            'anny': any_actual,
        })
