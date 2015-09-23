# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('',

	(r'^$', 'gestib.views.importData'),
	(r'^import/$', 'gestib.views.importData'),
	(r'^consulta/$', 'gestib.views.consultaGrup'),

)
