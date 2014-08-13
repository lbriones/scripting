#!/usr/bin/python
# -*- coding: UTF8 -*-


class mascota:
	numero_de_patas = 0
	color = 'marrón'

	def dormir(self):
		print "zzz"

	def comer(self, comida):
		print "comiendo", comida

perro = mascota()
perro.numero_de_patas = 4

comida = 'hamburguesas'
comida += ' con papas fritas'

print perro.numero_de_patas
perro.dormir()
perro.comer(comida)
