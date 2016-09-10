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


def cleanBeforeImport(anny):
    # Fem actiu només l'any actual
    Any.objects.all().update(actiu=False)
    anny.active = True
    anny.save()

    # Esborrem totes les matrícules d'aquest any
    mats = Matricula.objects.filter(anny=anny).delete()

    # Desactivem tots els alumnes
    Alumne.objects.all().update(actiu=False)

    # Desactivem tots els profes
    Professor.objects.all().update(actiu=False)

    # Desactivem tots els cursos
    Curs.objects.all().update(actiu=False)

    # Desactivem tots els grups
    Grup.objects.all().update(actiu=False)

    # TODO: Faltaríen les matéries i submatèries...



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

            # Netejam abans d'importar
            cleanBeforeImport(anny)

            # Importem les dades!!!
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
                'nmats': nmats,
                # 'nsubs': nsubs,
                # 'nsubmatgrup': nsubmatgrup
            })

    else:
        form = ImportForm()

    return renderResponse(request, 'gestib/import.html', {
        'form': form,
    } )
