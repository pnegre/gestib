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

#
# def cleanBeforeImport(anny):
#     # Fem actiu només l'any actual
#     Any.objects.all().update(actiu=False)
#     anny.active = True
#     anny.save()
#
#     # Esborrem totes les matrícules d'aquest any
#
#     # Desactivem tots els alumnes
#
#     # Desactivem tots els profes
#
#     # Desactivem tots els cursos
#
#     # Desactivem tots els grups

def getOption(dct, attr):
    if attr not in dct.keys():
        return False

    return dct[attr]


# Mostra el form per importar dades de l'xml del gestib
@permission_required('gestib.importar_alumnes')
def importData(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            annyid = form.cleaned_data['anny']
            fle = form.cleaned_data['fle']
            anny = Any.objects.get(id=annyid)
            ials = getOption(form.cleaned_data, 'importAlumnes')
            iprofs = getOption(form.cleaned_data, 'importProfessors')
            icursos = getOption(form.cleaned_data, 'importCursos')
            isubmats = getOption(form.cleaned_data, 'importSubmateries')

            dom = parse(fle)
            if anny.any1 != getYear(dom):
                # Any acadèmic no correspon amb l'any del fitxer XML
                # TODO: Missatge d'error al form així com toca
                message = "Error in XML: els anys no coincideixen. XML: %d, bbdd: %d" % (anny.any1, getYear(dom))
                return renderResponse(request, 'gestib/missatge.html', {
                    'message': message
                })

            # Importem les dades!!!
            incidencies = []
            nprofs, ncursos, ngrups, nalumnes, nmats, nsubs, nsubmatgrup = 0,0,0,0,0,0,0

            if iprofs:
                Professor.objects.all().update(actiu=False)
                nprofs = importProfessors(incidencies, dom)

            if icursos:
                Curs.objects.all().update(actiu=False)
                Grup.objects.all().update(actiu=False)
                ncursos, ngrups = importCursos(incidencies, dom, anny)

            if ials:
                mats = Matricula.objects.filter(anny=anny).delete()
                Alumne.objects.all().update(actiu=False)
                nalumnes, nmats = importAlumnes(incidencies, dom, anny)

            if isubmats:
                # Alerta: no desactivem les submatèries. L'atribut "actiu" aquí ho emprem per altres coses...
                nsubs = importSubmateries(dom, anny)
                nsubmatgrup = importSubmateriesGrup(dom)

            # Fem actiu només l'any actual
            Any.objects.all().update(actiu=False)
            anny.active = True
            anny.save()

            return renderResponse(request, 'gestib/import.html', {
                'finished': True,
                'nprofs': nprofs,
                'nalumnes': nalumnes,
                'ncursos': ncursos,
                'ngrups': ngrups,
                'incidencies': incidencies,
                'nmats': nmats,
                'nsubs': nsubs,
                'nsubmatgrup': nsubmatgrup,
            })

    else:
        form = ImportForm()

    return renderResponse(request, 'gestib/import.html', {
        'form': form,
    } )
