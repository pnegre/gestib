# -*- coding: utf-8 -*-

from django import forms
from gestib.models import *


class ImportForm(forms.Form):
    anny = forms.ChoiceField(label="Any acadèmic")
    fle = forms.FileField(label="Fitxer amb les dades XML (gestib)")
    importAlumnes = forms.BooleanField(label="Importar alumnes", initial=False, required=False)
    importProfes = forms.BooleanField(label="Importar profes", initial=False, required=False)
    importCursos = forms.BooleanField(label="Importar cursos", initial=False, required=False)
    importSubmateries = forms.BooleanField(label="Importar submatèries", initial=False, required=False)

    def __init__(self, *args, **kwrds):
        super(ImportForm, self).__init__(*args, **kwrds)
        self.fields['anny'].choices = [[ x.id, x] for x in Any.objects.all().order_by('-any1')[:10] ]
