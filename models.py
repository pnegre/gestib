# -*- coding: utf-8 -*-
from django.db import models


class Curs(models.Model):
	nom = models.CharField(max_length=200)
	codi = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.nom


class Professor(models.Model):
	nom = models.CharField(max_length=200)
	llinatge1 = models.CharField(max_length=200)
	llinatge2 = models.CharField(max_length=200)
	codi = models.CharField(max_length=200)
	
	def __unicode__(self):
		return  self.llinatge1 + ' ' + self.llinatge2 + ', ' + self.nom


class Grup(models.Model):
	nom = models.CharField(max_length=200)
	codi = models.CharField(max_length=200)
	
	tutor = models.ForeignKey(Professor)
	curs = models.ForeignKey(Curs)
	
	def __unicode__(self):
		return self.curs.nom + " " + self.nom


class Alumne(models.Model):
	nom = models.CharField(max_length=200)
	llinatge1 = models.CharField(max_length=200)
	llinatge2 = models.CharField(max_length=200)
	expedient = models.CharField(max_length=200)
	
	grup = models.ForeignKey(Grup)
	
	def __unicode__(self):
		return self.llinatge1 + ' ' + self.llinatge2 + ', ' + self.nom


class Submateria(models.Model):
	nom = models.CharField(max_length=200)
	descripcio = models.CharField(max_length=400)
	codi = models.CharField(max_length=200)
	
	curs = models.ForeignKey(Curs)
	grup = models.ForeignKey(Grup)
	
	def __unicode__(self):
		return self.nom



