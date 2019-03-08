# coding: latin-1

#-------------------------------------------------------------------------------
# Name:		saruman
# Purpose:	 script para recolher dados públicos de clima
#
# Author:	  rogerio.moreira
#
# Created:	 12/10/2015
# Copyright:   (c) rogerio.moreira 2015
# Licence:	 <your licence>
#-------------------------------------------------------------------------------

from bs4 import BeautifulSoup
import requests.packages.chardet
import html5lib
import requests
import re
from functools import reduce
import xml.etree.ElementTree as ET
from lxml import etree
from datetime import date, timedelta, datetime
import locale
import requests_cache
import urllib2
from time import sleep
import json

import os
os.environ["REQUESTS_CA_BUNDLE"] = r"cacert.pem"

os.chdir('\\\\172.20.0.45\\jornalismo novo\\# Robôs\Tempo\# script')

"""
Antes o meu objetivo era ter um 'robô' que atendesse Fpolis e
Jvlle - o que, bem, não é necessário hoje.
Além disso, esse programa está bem baseado em classes
- mais do que devia, eu acho.

O desafio seria ter uma classe (acho que o AtualizaTabelas é o meu
melhor script), e várias funções dentro dela. Na verdade, não é
fazer nada novo, é mais usar o que eu já tenho hoje.
"""

### Conexão

locale.setlocale(locale.LC_TIME, "ptb")

s = requests.Session()

senha = open(u'\\\\172.20.0.45\\jornalismo novo\_Utilit\xe1rios\password.txt').read()

proxy = ({
	'http':'http://rogerio.moreira:{}@172.20.0.75:8080'.format(senha),
	'https':'https://rogerio.moreira:{}@172.20.0.75:8080'.format(senha)
	})

def make_soup(url):
	os.environ["REQUESTS_CA_BUNDLE"] = r"cacert.pem"
	os.chdir('\\\\172.20.0.45\\jornalismo novo\\# Robôs\Tempo\# script')

	html = s.get(url, proxies=proxy, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'})
	return BeautifulSoup(html.content, "lxml")



### Classes

class Previsao():
	def __init__(self, debug = False):
		self.debug = debug
		self.key = '7031a6b6563a19e4b8858782e29200ae'
		self.id = '6323121'

	def d_print(self, string):
		if self.debug == False:
			print(string),

	def mapa_estado(self):
		self.d_print('Verificando dados dos mapas... ')

		parent_xml = etree.SubElement(root, 'mapa_estado')
		dicionario = {
		u'Região: Litoral Norte':'litoral_norte',
		u'Região: Planalto Norte':'norte',
		u'Região: Grande Florianópolis Litorânea':'grande_fpolis_litoranea',
		u'Região: Grande Florianópolis Serrana':'grande_fpolis_serrana',
		u'Região: Vale do Itajaí':'vale_itajai',
		u'Região: Litoral Sul':'litoral_sul',
		u'Região: Planalto Sul':'planalto_sul',
		u'Região: Meio Oeste':'meio_oeste',
		u'Região: Oeste':'oeste' ,
		u'Região: Extremo Oeste':'extremo_oeste'
		}

		soup = make_soup(site_regiao)

		lista = [row.get_text() for row in soup.find('div',{'id':'tab-regiao-amanha'}).findAll('table') if re.match(u'.+Tarde:.+', row.getText(), re.DOTALL)]
		global climas
		climas = [re.search(u'(Região:[^\n]+) .+Tarde: ([^\n]+) \n', item, re.DOTALL).groups() for item in lista]
		for regioes in climas:
			regiao, clima = regioes
			icone = dia_atributo(clima)
			regiao_xml = etree.SubElement(parent_xml, dicionario[regiao])
			etree.SubElement(regiao_xml, 'clima').set('href', icone)

		self.d_print('Ok\n')


	def previsao_detalha(self):
		global json_
		self.d_print('Verificando dados de Florianópolis... ')

		parent_xml = etree.SubElement(root, 'previsao_detalhada')

		site = 'http://api.openweathermap.org/data/2.5/forecast?id={id_}&appid={key}&units=metric'.format(id_=self.id, key=self.key)
		json_ = json.loads(make_soup(site).text)


		dia = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)
		dia_s = dia.strftime('%Y-%m-%d')

		def temp(horario):
			return [el['main']['temp'] for el in json_['list'] if el['dt_txt'] == u'{} {}'.format(dia_s, horario)][0]

		# Aqui eu pego as temperaturas
		temp_manha = temp('06:00:00')
		temp_tarde = temp('12:00:00')
		temp_noite = temp('18:00:00')

		# Aqui eu pego o clima

		soup = make_soup(site_regiao)
		lista = [row.get_text() for row in soup.find('div',{'id':'tab-regiao-amanha'}).findAll('table') if re.match(u'.+Flori.+Tarde:.+', row.getText(), re.DOTALL)]
		cl_manha = re.search(u'Manhã: ([^\n]+) \n', lista[0]).groups()[0]
		cl_tarde = re.search(u'Tarde: ([^\n]+) \n', lista[0]).groups()[0]
		cl_noite = re.search(u'Noite: ([^\n]+) \n', lista[0]).groups()[0]

		# Aqui eu escrevo

		manha = etree.SubElement(parent_xml, 'manha')
		etree.SubElement(manha, 'clima').set('href', cl_manha)
		etree.SubElement(manha, 'temperatura').text = celsius(temp_manha)

		tarde = etree.SubElement(parent_xml, 'tarde')
		etree.SubElement(tarde, 'clima').set('href', cl_tarde)
		etree.SubElement(tarde, 'temperatura').text = celsius(temp_tarde)

		noite = etree.SubElement(parent_xml, 'noite')
		etree.SubElement(noite, 'clima').set('href', cl_noite)
		etree.SubElement(noite, 'temperatura').text = celsius(temp_noite)

		self.d_print('Ok\n')


	def previsao_dias(self):
		self.d_print('Verificando dados dos dias... ')
		parent_xml = etree.SubElement(root, 'previsao_dias')

		site = 'http://ciram.epagri.sc.gov.br/wsprev/resources/listaJson/prevMuni?cdCidade=4205407&data={}'

		atributos =['amanha', 'depois_amanha', 'seguinte_depois']
		dias = [2, 3, 4]

		for n in range(3):
			global json_
			dia_xml = etree.SubElement(parent_xml, atributos[n])

			dia = datetime.now() + timedelta(days = dias[n]) - timedelta(hours = 5)
			etree.SubElement(dia_xml, 'dia_semana').text = dia_da_semana[dia.weekday()]

			json_ = json.loads(make_soup(site.format(dia.strftime('%Y/%m/%d'))).text)[0]

			clima = json_['iconFenomeno1Desc']
			if clima not in dicionario_icones: clima == 'none'
			etree.SubElement(dia_xml, 'clima').set('href', dia_atributo(clima))

			etree.SubElement(dia_xml, 'minima').text = json_['tempMinEUnidade']
			etree.SubElement(dia_xml, 'maxima').text = json_['tempMinEUnidade']


	def cidades_sc(self):
		self.d_print('Verificando dados das cidades... ')

		parent_xml = etree.SubElement(root, 'cidades_sc')
		lista = {'chapeco':1480 , 'itajai':2535, 'lages':2876, 'criciuma':1671, 'joinville':2808, 'blumenau':868}
		dia = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)

		for localidade in sorted(lista):
			soup = make_soup('http://servicos.cptec.inpe.br/XML/cidade/%s/previsao.xml' % lista[localidade])
			minima = soup.minima.string
			maxima = soup.maxima.string
			concatenacao = u"{}°C/{}°C".format(minima, maxima)
			etree.SubElement(parent_xml, localidade).text = concatenacao

		self.d_print('Ok\n')


	def outros(self):
		self.d_print('Verificando dados de apoio... ')

		parent_xml = etree.SubElement(root, 'outros')

		poente, nascente = horario_sol()

		etree.SubElement(parent_xml, 'poente').text = poente
		etree.SubElement(parent_xml, 'nascente').text = nascente

		self.d_print('Ok\n')


### Variáveis

root = etree.Element("root")

dia_da_semana = [u'Segunda', u'Terça', u'Quarta', u'Quinta', u'Sexta', u'Sábado', u'Domingo']

site_open_weather_floripa = 'http://api.openweathermap.org/data/2.5/forecast/daily?q=Florianopolis&mode=xml&units=metric&cnt=7&appid=04dbb22dcf1d4f86ef0610c75e9d9afb'
site_mar_floripa = 'http://ondas.cptec.inpe.br/cidades/faces/cidadeframe.jsp?idCid=228'
site_regiao = 'http://www.ciram.com.br/index.php?option=com_content&view=article&id=2405&Itemid=141'
site_cabecalho = 'http://www.ciram.sc.gov.br/index.php?option=com_content&view=article&id=2405&Itemid=141'
site_horario = 'https://www.cptec.inpe.br/cidades/tempo/228'


##caminho_tempo

caminho_icones = u'file:///Icones/'
caminho_fases = u'file:///Icones/lua/'

dicionario_icones = dict([el.split('\t') for el in open('S:\\# Rob\xf4s\Tempo\# script\mapeamento_icones.txt').read().decode('latin1').split('\n')])

string_lua =open('fases_lua.txt').read()


### Funções

def month(number):
	if number < 10:
		return "0"+str(number)
	else:
		return str(number)

def year(number):
	return str(number)[-2:]

def celsius(string):
	return str(int(round(float(string)))) + u'°C'

def format_time(string):
	return re.sub('^0?(\d+):(\d+):\d+','\g<1>h\g<2>', string)

def dia_atributo(string):
	return caminho_icones + dicionario_icones[string] + ".eps"

def noite_atributo(string):
	return caminho_icones + r'noite_'+dicionario_icones[string] + ".eps"

def lua_atributo(string):
	return caminho_fases + 'lua_'+ string.lower() + ".ai"

def sentence_case(string):
	lista = string.split(' ')
	lista[0] = lista[0].title()
	return(' ').join(lista)


def horario_sol():
	global soup
	soup = make_soup(site_horario)
	nascente = re.search('Nascer do sol:\xa0\n\s+([\d\:]+)', soup.find('div','col-md-12').text).groups()[0]
	poente = re.search('P\xf4r do sol:\xa0\n\s+([\d\:]+)', soup.find('div','col-md-12').text).groups()[0]
	return [format_time(el) for el in [nascente, poente]]


def master():
	t = Previsao()

	for function in (t.mapa_estado,
	t.previsao_detalha,
	t.cidades_sc,
	t.previsao_dias,
	t.outros,):

		i=0
		while i<3:
			try:
				function()
				break
			except:
				i+=1
				sleep(5)
		if i==3:print 'erro'

def debug():
	t = Previsao(debug=True)
	for function in (t.mapa_estado,
	t.previsao_detalha,
	t.cidades_sc,
	t.previsao_dias,
	t.outros,
	t.conjunto_fases):
		function()


def view(): print etree.tostring(root, pretty_print = True)


if __name__ == '__main__':
	master()

	output = etree.tostring(root, pretty_print = True)
	filename='previsao'
	open('{}.xml'.format(filename), 'w').write(output)

	print "\n\nTudo certo. Abra os arquivos para atualizá-los."

	raw_input()
