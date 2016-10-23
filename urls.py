# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('',

	(r'^$', 'gestib.views.importData'),
	(r'^import/$', 'gestib.views.importData'),
	(r'^inconsistencies/$', 'gestib.views.inconsistencies'),

	(r'^getDuplicates/$', 'gestib.ajax.getDuplicates'),

)
