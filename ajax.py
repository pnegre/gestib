# -*- coding: utf-8 -*-

from functools import wraps

from django.contrib.auth.decorators import login_required, permission_required

from django.db.models import Count
from django.forms.models import model_to_dict

from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from gestib.models import *



#
# Torna una resposta de tipus application/json amb les dades que es passen com a paràmetre
#
def toJson(data):
    return HttpResponse(simplejson.dumps(data), content_type="application/json");


@permission_required('gestib.importar_alumnes')
def getDuplicates(request):
    dups = Alumne.objects.values('expedient').annotate(Count('id')).filter(id__count__gt=1)
    result = []
    for d in dups:
        als = Alumne.objects.filter(expedient=d['expedient'])
        lals = [ {'id': a.id, 'nom': a.nom, 'llinatge1': a.llinatge1, 'llinatge2': a.llinatge2,
            'actiu': a.actiu } for a in als]
        result.append({'exp': d['expedient'], 'alumnes': lals})

    return toJson(result)
