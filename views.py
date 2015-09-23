# -*- coding: utf-8 -*-

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
                raise Exception("Error in XML: els anys no coincideixen. XML: %d, bbdd: %d" % (anny.any1, getYear(dom)))

            incidencies = []
            nprofs = importProfessors(incidencies, dom)
            ncursos, ngrups = importCursos(incidencies, dom, anny)
            incidenciesAlumnes, nalumnes, nmats = importAlumnes(dom, anny)
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
