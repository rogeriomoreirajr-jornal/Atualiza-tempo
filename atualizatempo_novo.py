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
	html = s.get(url, proxies=proxy, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'})
	return BeautifulSoup(html.content, "lxml")



### Classes

class Previsao():
	def __init__(self, debug = False):
		self.debug = debug

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
		climas = [re.search(u'(Região:[^\n]+) .+Tarde: ([^\n]+) \n', item, re.DOTALL).groups() for item in lista]
		for regioes in climas:
			regiao, clima = regioes
			icone = dia_atributo(clima)
			regiao_xml = etree.SubElement(parent_xml, dicionario[regiao])
			etree.SubElement(regiao_xml, 'clima').set('href', icone)

		self.d_print('Ok\n')


	def previsao_detalha(self):
		self.d_print('Verificando dados de Florianópolis... ')

		parent_xml = etree.SubElement(root, 'previsao_detalhada')

		dia = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)

		site_detalhado = "http://api.wunderground.com/api/8ffaaf696715df86/hourly/q/Brazil/zmw:00000.80.83897.xml"
		soup = make_soup(site_detalhado)
		horarios = [i.parent.parent for i in soup.findAll('mday',text=dia.day)]

		# Aqui eu pego as temperaturas
		temp_manha = horarios[9].temp.metric.get_text()
		temp_tarde = horarios[14].temp.metric.get_text()
		temp_noite = horarios[19].temp.metric.get_text()

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

		site_previsao = "http://api.wunderground.com/api/8ffaaf696715df86/forecast10day/q/Brazil/zmw:00000.80.83897.xml"
		soup = make_soup(site_previsao)

		atributos =['amanha', 'depois_amanha', 'seguinte_depois']
		dias = [2, 3, 4]

		for n in range(3):
			dia_xml = etree.SubElement(parent_xml, atributos[n])

			dia = datetime.now() + timedelta(days = dias[n]) - timedelta(hours = 5)
			etree.SubElement(dia_xml, 'dia_semana').text = dia_da_semana[dia.weekday()]

			clima = soup.simpleforecast.find('day',text=dia.day).parent.parent.icon.get_text()
			etree.SubElement(dia_xml, 'clima').set('href', dia_atributo(clima))

			minima = soup.simpleforecast.find('day',text=dia.day).parent.parent.low.celsius.get_text()
			etree.SubElement(dia_xml, 'minima').text = celsius(minima)

			maxima = soup.simpleforecast.find('day',text=dia.day).parent.parent.high.celsius.get_text()
			etree.SubElement(dia_xml, 'maxima').text = celsius(maxima)

		self.d_print('Ok\n')


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
		etree.SubElement(parent_xml, 'mare').text = baixa_mar('60245')

		poente, nascente = horario_sol()

		etree.SubElement(parent_xml, 'poente').text = poente
		etree.SubElement(parent_xml, 'nascente').text = nascente

		self.d_print('Ok\n')


	def conjunto_fases(self):
		self.d_print('Verificando dados da lua... ')

		parent_xml = etree.SubElement(root, 'conjunto_fases')

		dia = datetime.today()

		soup = BeautifulSoup(open('lua.txt').read(), 'lxml')

		linhas = soup.find('div','left_moon_phases').table.tbody.findAll('tr')
		colunas = re.compile('([^\d]+)(.+)(\d{2}:\d{2}:\d{2})').findall
		datas = [colunas(el.text)[0] for el in linhas]

		for el in datas:
			if datetime.strptime(el[1].encode('latin1'), '%d %B %Y') > dia:
				index = datas.index(el)
				lista_media = datas[index-1:index+3]
				break

		dict_luas = {u'Lua cheia':'Cheia',
		u'\xfaltimo quarto':'Minguante',
		u'Lua nova':'Nova',
		u'Primeiro quarto':'Crescente'}

		lista_final = []

		for data in lista_media:
			data_string = (' de ').join(data[1].split(' ')[:2])
			horario_string = ('h').join(data[2].split(':')[:2])

			data_horario = data_string+', '+horario_string
			fase = dict_luas[data[0]]
			caminho = lua_atributo(fase)

			lista_final.append([data_horario, fase, caminho])

		luas = ['lua_1','lua_2','lua_3','lua_4']
		itens = ['data','fase','caminho']
		for lua in luas:
			i = 0
			index = luas.index(lua)
			lua_xml = etree.SubElement(parent_xml, luas[index])
			for item in itens[::-1]:
				if item != 'caminho':
					etree.SubElement(lua_xml, item).text = lista_final[index][::-1][i]
				else:
 					etree.SubElement(lua_xml, 'caminho').set('href', lista_final[index][::-1][i])
				i += 1

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

def baixa_mar(codigo_cidade):
	amanha = date.today() + timedelta(days = 1)
	dia, mes, ano = month(amanha.day), month(amanha.month), year(amanha.year)
	soup = make_soup("http://ondas.cptec.inpe.br/~rondas/mares/index.php?cod=%s&mes=%s&ano=%s"%(codigo_cidade, mes, ano))
	tuples_mares = re.findall('0*(\d\d?):(\d{2})[^\d\w]+([\d.]{3})',soup.find('strong', text='%s/%s' % (dia, mes)).parent.get_text())
	string_mares = ('\n').join(['%sh%s: %s'%t for t in tuples_mares])
	return string_mares

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


def mare(string):
	soup = make_soup(site_mar)
	for row in soup.findAll('tr')[3:]:
		 if re.search(string, row.get_text()):
			teste = [item.get_text() for item in row.findAll('td')]
##			print row.get_text()
			linha = [re.findall('([\d:\.]+)',item.get_text()) for item in row.findAll('td')[1:]][2:4]
##			print linha
			for altura in linha[::2]:
				horario = linha[linha.index(altura)-1]
				lista_final = []
				for item in altura:
					lista_final.append([item, horario[altura.index(item)]])
				mares = ('\n').join([(': ').join(el) for el in lista_final])
				mares = re.sub('^0','',mares,re.MULTILINE)
				mares = re.sub('\n0','\n',mares,re.MULTILINE)
				mares = re.sub('(\d):(\d)','\g<1>h\g<2>',mares,re.MULTILINE)
				return mares

def master():
	t = Previsao()

	for function in (t.mapa_estado,
	t.previsao_detalha,
	t.cidades_sc,
	t.previsao_dias,
	t.outros,
	t.conjunto_fases):

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
