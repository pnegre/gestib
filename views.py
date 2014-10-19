# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required, permission_required

from gestib.dom import *

from gestib.models import *
from gestib.forms import *


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

            nprofs = importProfessors(dom)
            ncursos, ngrups = importCursos(dom, anny)
            nalumnes, nmats = importAlumnes(dom, anny)
            # nsubs = importSubmateries(dom, anny)
            # nsubmatgrup = importSubmateriesGrup(dom)

            return render_to_response('gestib/import.html', {
                'finished': True,
                'nprofs': nprofs,
                'nalumnes': nalumnes,
                'ncursos': ncursos,
                'ngrups': ngrups,
                # 'nmats': nmats,
                # 'nsubs': nsubs,
                # 'nsubmatgrup': nsubmatgrup
            })

    else:
        form = ImportForm()

    return render_to_response('gestib/import.html', {
        'form': form,
    } )
