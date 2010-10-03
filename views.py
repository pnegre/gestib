# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import simplejson

from xml.dom.minidom import parse, parseString

from gestib.models import *


def importProfessors(dom):
	professors = dom.getElementsByTagName('PROFESSOR')
	for prof in professors:
		p = Professor(
			codi = prof.getAttribute('codi'),
			nom = prof.getAttribute('nom'),
			llinatge1 = prof.getAttribute('ap1'),
			llinatge2 = prof.getAttribute('ap2'),
		)
		p.save()


def importCursos(dom):
	cursos = dom.getElementsByTagName('CURS')
	for curs in cursos:
		c = Curs(nom=curs.getAttribute('descripcio'),codi=curs.getAttribute('codi'))
		c.save()
		
		grups = curs.getElementsByTagName('GRUP')
		for grup in grups:
			prof = Professor.objects.filter(codi=grup.getAttribute('tutor'))
			if prof == None: continue
			if len(prof) == 0: continue
			
			g = Grup(
				nom = grup.getAttribute('nom'),
				curs = c,
				tutor = prof[0],
				codi = grup.getAttribute('codi'),
			)
			g.save()

def importAlumnes(dom):
	alumnes = dom.getElementsByTagName('ALUMNE')
	for alumne in alumnes:
		nom = alumne.getAttribute('nom')
		l1 = alumne.getAttribute('ap1')
		l2 = alumne.getAttribute('ap2')
		exp = alumne.getAttribute('expedient')
		gp = Grup.objects.filter(codi=alumne.getAttribute('grup'))
		if gp == None: continue
		if len(gp) == 0: continue
		
		a = Alumne(nom=nom,llinatge1=l1,llinatge2=l2,expedient=exp,grup=gp[0])
		a.save()

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


@permission_required('gestib.importar_alumnes')
def importData(request):
	return render_to_response(
			'gestib/import.html', {
	} )



@permission_required('gestib.importar_alumnes')
def doImport(request):
	if request.method == 'POST':
		f = request.FILES['file']
		dom = parse(f)
		
		importProfessors(dom)
		importCursos(dom)
		importAlumnes(dom)
		importSubmateries(dom)
	
	return render_to_response(
			'gestib/ok.html', {
	} )



