# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
	
	(r'^import/$', 'gestib.views.importData'),
	(r'^doimport/$', 'gestib.views.doImport'),
	
)
