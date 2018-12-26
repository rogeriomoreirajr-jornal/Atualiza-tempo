# coding: latin-1

#-------------------------------------------------------------------------------
# Name:        saruman
# Purpose:     script para recolher dados públicos de clima
#
# Author:      rogerio.moreira
#
# Created:     12/10/2015
# Copyright:   (c) rogerio.moreira 2015
# Licence:     <your licence>
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

import os
os.environ["REQUESTS_CA_BUNDLE"] = r"cacert.pem"

os.chdir('\\\\172.20.0.45\\jornalismo novo\\# Robôs\Tempo\# script')


### Classes

class amplitude:
    def __init__(self):
        self.dia_semana = ''
        self.clima = ''
        self.maxima = ''
        self.minima = ''
        self.nome = 'amplitude'
        self.lista = ['dia_semana','clima','minima','maxima']

class instantanea:
    def __init__(self):
        self.clima = ''
        self.temperatura = ''
        self.nome = 'instantanea'
        self.lista = ['clima','temperatura']

class mapa_estado:
    def __init__(self):
        self.litoral_norte = amplitude()
        self.norte = amplitude()
        self.grande_fpolis_litoranea = amplitude()
        self.grande_fpolis_serrana = amplitude()
        self.vale_itajai = amplitude()
        self.litoral_sul = amplitude()
        self.planalto_sul = amplitude()
        self.meio_oeste = amplitude()
        self.oeste = amplitude()
        self.extremo_oeste = amplitude()
        self.nome = 'mapa_estado'
        self.lista =  ['extremo_oeste','grande_fpolis_litoranea','grande_fpolis_serrana','litoral_norte','litoral_sul','meio_oeste','norte','oeste','planalto_sul','vale_itajai']

class previsao_detalhada:
    def __init__(self):
        self.manha = instantanea()
        self.tarde = instantanea()
        self.noite = instantanea()
        self.nome = 'previsao_detalhada'
        self.lista = ['manha','tarde','noite']

class previsao_dias:
    def __init__(self):
        self.amanha = amplitude()
        self.depois_amanha = amplitude()
        self.seguinte_depois = amplitude()
        self.nome = 'previsao_dias'
        self.lista = ['amanha','depois_amanha','seguinte_depois']

class fase_lua:
    def __init__(self):
        self.data = ''
        self.fase = ''
        self.caminho = ''
        self.lista = ['caminho','fase','data']

class conjunto_fases:
    def __init__(self):
        self.lua_1 = fase_lua()
        self.lua_2 = fase_lua()
        self.lua_3 = fase_lua()
        self.lua_4 = fase_lua()
        self.lista = ['lua_1','lua_2','lua_3','lua_4']

class outros:
    def __init__(self):
        self.poente = ''
        self.nascente = ''

        self.mare = ''

        self.vento_direcao = ''
        self.vento_velocidade = ''
        self.nome = 'outros'
        self.imagem_satelite = u'file:///ultima.jpg'
        self.lista = ["mare",'vento_direcao', 'vento_velocidade',"poente","nascente","imagem_satelite"]

class cidades_brasil:
    def __init__(self):
        self.brasilia = ''
        self.sao_paulo = ''
        self.rio_de_janeiro = ''
        self.curitiba = ''
        self.porto_alegre = ''
        self.nome = 'cidade'
        self.lista = ['brasilia','curitiba','porto_alegre','rio_de_janeiro','sao_paulo']

class cidades_sc:
    def __init__(self):
        self.chapeco = ''
        self.itajai = ''
        self.criciuma = ''
        self.lages = ''
        self.joinville = ''
        self.blumenau = ''
        self.nome = 'cidade'
        self.lista = ['blumenau','chapeco', 'criciuma', 'itajai', 'joinville','lages' ]


### Variáveis

mapa_estado = mapa_estado()
cidades_brasil = cidades_brasil()
cidades_sc = cidades_sc()

florianopolis = previsao_detalhada()
florianopolis_dias = previsao_dias()
florianopolis_outros = outros()

joinville = previsao_detalhada()
joinville_dias = previsao_dias()
joinville_outros = outros()

lista_lua = conjunto_fases()


dia_da_semana = [u'Segunda', u'Terça', u'Quarta', u'Quinta', u'Sexta', u'Sábado', u'Domingo']

site_open_weather_floripa = 'http://api.openweathermap.org/data/2.5/forecast/daily?q=Florianopolis&mode=xml&units=metric&cnt=7&appid=04dbb22dcf1d4f86ef0610c75e9d9afb'
site_open_weather_joinville = 'http://api.openweathermap.org/data/2.5/forecast/daily?q=Joinville&mode=xml&units=metric&cnt=7&appid=04dbb22dcf1d4f86ef0610c75e9d9afb'
site_mar_floripa = 'http://ondas.cptec.inpe.br/cidades/faces/cidadeframe.jsp?idCid=228'
site_mar_joinville = 'http://ondas.cptec.inpe.br/cidades/faces/cidade.jsp?idCid=4825'
site_regiao = 'http://www.ciram.com.br/index.php?option=com_content&view=article&id=2405&Itemid=141'
site_cabecalho = 'http://www.ciram.sc.gov.br/index.php?option=com_content&view=article&id=2405&Itemid=141'
site_horario_floripa = 'https://www.cptec.inpe.br/cidades/tempo/228'
site_horario_joinville = 'https://www.cptec.inpe.br/cidades/tempo/2808'


# variáveis

from valinor import *

##s = requests.Session()
##
##senha = open(u'\\\\172.20.0.45\\jornalismo novo\_Utilit\xe1rios\password.txt').read()
##
##proxy = ({
##    'http':'http://rogerio.moreira:{}@172.20.0.75:8080'.format(senha),
##	'https':'https://rogerio.moreira:{}@172.20.0.75:8080'.format(senha)
##	})
##
##def make_soup(url):
##    html = s.get(url, proxies=proxy, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'})
##    return BeautifulSoup(html.content, "lxml")


##auth = HTTPBasicAuthHandler()
##opener = build_opener(proxy, auth, HTTPHandler)
##opener.addheaders.append(('Cookie', 'cookiename=cookievalue'))
##install_opener(opener)

# O que o programa tem que fazer é abrir os xml, retornar os dados
# aos objetos e gravar eles no xml. Eu poderia ter um XML grandão,
# montado a partir do InDesign, e dai para a frente usar ele aqui,
# substituindo os números pelas variáveis que o programa vai obter.

##caminho_tempo

caminho_icones = u'file:///Icones/'
caminho_fases = u'file:///Icones/lua/'

mapeamento_icones = u"""thunderstorm with light rain	chovendo com trovoada
thunderstorm with rain	chovendo com trovoada
thunderstorm with heavy rain	chovendo com trovoada
light thunderstorm	chovendo com trovoada
thunderstorm	chovendo com trovoada
heavy thunderstorm	chovendo com trovoada
ragged thunderstorm	chovendo com trovoada
thunderstorm with light drizzle	chovendo com trovoada
thunderstorm with drizzle	chovendo com trovoada
thunderstorm with heavy drizzle	chovendo com trovoada
light intensity drizzle	chuva e sol
drizzle	chuva e sol
heavy intensity drizzle	chuva e sol
light intensity drizzle rain	chuva e sol
drizzle rain	chovendo
heavy intensity drizzle rain	chovendo
shower rain and drizzle	chovendo
heavy shower rain and drizzle	chovendo
shower drizzle	chovendo
light rain	chovendo
sky is clear	sol
moderate rain	chovendo
heavy intensity rain	chovendo
very heavy rain	chovendo
extreme rain	chovendo
freezing rain	chovendo
light intensity shower rain	sol com chuva
shower rain	sol com chuva
heavy intensity shower rain	sol com chuva
ragged shower rain	sol com chuva
light snow	-
snow	-
heavy snow	-
sleet	-
shower sleet	-
light rain and snow	-
rain and snow	-
light shower snow	-
shower snow	-
heavy shower snow	-
mist	-
smoke	-
haze	-
sand, dust whirls	-
fog	-
sand	-
dust	-
volcanic ash	-
squalls	-
tornado	-
clear sky	sol
Ensolarado	sol
few clouds	sol com nuvem
scattered clouds	sol com nuvem
broken clouds	nublado
overcast clouds	nublado
Céu com algumas nuvens	sol com nuvem
Céu com muitas nuvens	nublado
Encoberto com chuva	chovendo
Nebulosidade variável	sol com nuvem
Nebulosidade vari\xc3\xa1vel	sol com nuvem
Nebulosidade variável e chuva isolada	chuva e sol
Nebulosidade vari\xc3\xa1vel e chuva isolada	chuva e sol
Sol com algumas nuvens	sol com nuvem
Sol com muitas nuvens	nublado
Céu encoberto	nublado
Pancada de chuva isolada	chuva e sol
Sol com aumento de nuvens	sol com nuvem
Céu estrelado	sol
chancerain	sol com nuvem
chancetstorms	chovendo
clear	sol
cloudy	sol com nuvem
flurries	-
fog	-
hazy	-
mostlycloudy	nublado
mostlysunny	sol com nuvem
partlycloudy	sol com nuvem
partlysunny	sol com nuvem
rain	chovendo
sunny	sol
tstorms	chovendo
cloudy	nublado
partlycloudy	sol com nuvem"""

string_lua = """ 1175 JAN. 01 23 24 JAN. 08 19 25
 1176 JAN. 16 23 17 JAN. 24 19 20 JAN. 31 10 27 FEV. 07 12 54
 1177 FEV. 15 18 05 FEV. 23 05 09 MAR. 01 21 51 MAR. 09 08 20
 1178 MAR. 17 10 11 MAR. 24 12 35 MAR. 31 09 37 ABR. 08 04 17
 1179 ABR. 15 22 57 ABR. 22 18 45 ABR. 29 21 58 MAI. 07 23 09
 1180 MAI. 15 08 48 MAI. 22 00 49 MAI. 29 11 20 JUN. 06 15 32
 1181 JUN. 13 16 43 JUN. 20 07 51 JUN. 28 01 53 JUL. 06 04 51
 1182 JUL. 12 23 48 JUL. 19 16 52 JUL. 27 17 20 AGO. 04 15 18
 1183 AGO. 11 06 58 AGO. 18 04 48 AGO. 26 08 56 SET. 02 23 37
 1184 SET. 09 15 01 SET. 16 20 15 SET. 24 23 52 OUT. 02 06 45
 1185 OUT. 09 00 47 OUT. 16 15 02 OUT. 24 13 45 OUT. 31 13 40
 1186 NOV. 07 13 02 NOV. 15 11 54 NOV. 23 02 39 NOV. 29 21 19
 1187 DEZ. 07 04 20 DEZ. 15 08 49 DEZ. 22 14 48 DEZ. 29 06 34"""

dicionario_icones = {lista.split('\t')[0]: lista.split('\t')[1] for lista in mapeamento_icones.split('\n')}

locale.setlocale(locale.LC_TIME, "ptb")

### Funções

def month(number):
    if number < 10:
        return "0"+str(number)
    else:
        return str(number)

def year(number):
    return str(number)[-2:]

def rgetattr(obj, attr):
    return reduce(getattr, [obj]+attr.split('.'))

def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def celsius(string):
    return str(int(round(float(string)))) + u'°C'

##def make_soup(url):
##    html = urllib2.urlopen(url).read()
##    return BeautifulSoup(html, "html.parser")

def format_time(string):
    return re.sub('^0?(\d+):(\d+):\d+','\g<1>h\g<2>', string)

def dia_atributo(string):
    return caminho_icones + dicionario_icones[string] + ".eps"

def noite_atributo(string):
    return caminho_icones + r'noite_'+dicionario_icones[string] + ".eps"

def lua_atributo(string):
##    print string
    return caminho_fases + 'lua_'+ string.lower() + ".ai"

def tuple_lua(string):
    linha = string.split(' - ')
    linha[0] = datetime.strptime(linha[0],'%d %b %Y')
    return linha

def fases_lua2():
    global lista_media
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

##    outros.lua.lua_1.fase
##    outros.lua.lua_1.data
    luas = ['lua_1','lua_2','lua_3','lua_4']
    itens = ['data','fase','caminho']
    for lua in luas:
        index = luas.index(lua)
        i = 0
        for item in itens:
            rsetattr(lista_lua,lua+'.'+itens[i],lista_final[index][i])
            i += 1


def fases_da_lua():
    global lista_media
    ano = str(date.today().year)
    dia = datetime.today() + timedelta(days = -100)
    fases = ['nova','crescente','cheia','minguante']
    site = "http://www.inmet.gov.br/portal/index.php?r=home2/page&page=fasesLua%s" %ano
    soup = make_soup(site)

    tab_moon_raw = soup.find("table","phase").findAll("tr")[4:-1]
    tab_moon_raw = [[linha.string for linha in conjunto.findAll('td')]
    for conjunto in tab_moon_raw]

    datas = []
    for conjunto in tab_moon_raw:
        for linha in conjunto:
            if linha != '--':
                lista_linha = tuple_lua(linha)
                lista_linha.append(fases[conjunto.index(linha)])
                datas.append(lista_linha)

    for data in datas:
        if data[0] > dia:
            indice = datas.index(data)-1
            final = indice + 4
            lista_media = datas[indice:final]
            break

    lista_final = []

    for data in lista_media:
        data_string = data[0].strftime("%d de %B")
        data_horario = data_string.decode('utf-8', 'ignore') +', '+data[1]
        data[2] = data[2].capitalize()
        caminho = lua_atributo(data[2])
        lista_final.append([data_horario, data[2],caminho])

        for item in lista_final:
            item[0]=re.sub(', ',',\n',item[0])
            item[0]=re.sub('^0','',item[0])
            item[0]=re.sub('0*(\d+):(\d+)',r'\1h\2',item[0])

##    outros.lua.lua_1.fase
##    outros.lua.lua_1.data
    luas = ['lua_1','lua_2','lua_3','lua_4']
    itens = ['data','fase','caminho']
    for lua in luas:
        index = luas.index(lua)
        i = 0
        for item in itens:
            rsetattr(lista_lua,lua+'.'+itens[i],lista_final[index][i])
            i += 1


def open_weather(site=site_open_weather_floripa, cidade=florianopolis, cidade_dias=florianopolis_dias, string_regiao='Flori', attemps=3):
    dia = date.today() + timedelta(days = 1)

    site_detalhado = "http://api.wunderground.com/api/8ffaaf696715df86/hourly/q/Brazil/zmw:00000.80.83897.xml"
    soup = make_soup(site_detalhado, filtro='mday', attemps=attemps)
    horarios = [i.parent.parent for i in soup.findAll('mday',text=dia.day)]

    # Aqui eu pego as temperaturas
    manha = horarios[9].temp.metric.get_text()
    cidade.manha.temperatura = celsius(manha)
    tarde = horarios[14].temp.metric.get_text()
    cidade.tarde.temperatura = celsius(tarde)
    noite = horarios[19].temp.metric.get_text()
    cidade.noite.temperatura = celsius(noite)

    site_previsao = "http://api.wunderground.com/api/8ffaaf696715df86/forecast10day/q/Brazil/zmw:00000.80.83897.xml"
    soup = make_soup(site_previsao)

    atributos =['amanha', 'depois_amanha', 'seguinte_depois']
    dias = [2, 3, 4]

    for n in range(3):
        dia = datetime.now() + timedelta(days = dias[n]) - timedelta(hours = 3)
        rsetattr(cidade_dias, atributos[n] + '.dia_semana', dia_da_semana[dia.weekday()])

        temperatura = soup.simpleforecast.find('day',text=dia.day).parent.parent.low.celsius.get_text()
        rsetattr(cidade_dias, atributos[n]+'.'+ "minima", celsius(temperatura))
        temperatura = soup.simpleforecast.find('day',text=dia.day).parent.parent.high.celsius.get_text()
        rsetattr(cidade_dias, atributos[n]+'.'+ "maxima", celsius(temperatura))
        clima = soup.simpleforecast.find('day',text=dia.day).parent.parent.icon.get_text()
        rsetattr(cidade_dias, atributos[n]+'.'+ "clima", dia_atributo(clima))

    clima_detalhado(cidade, string_regiao)



def clima_detalhado(objeto, string):
    soup = make_soup(site_regiao)
    lista = [row.get_text() for row in soup.find('div',{'id':'tab-regiao-amanha'}).findAll('table') if re.match(u'.+'+ string + '.+Tarde:.+', row.getText(), re.DOTALL)]
    manha = re.search(u'Manhã: ([^\n]+) \n', lista[0]).groups()[0]
    objeto.manha.clima = dia_atributo(manha)
    tarde = re.search(u'Tarde: ([^\n]+) \n', lista[0]).groups()[0]
    objeto.tarde.clima = dia_atributo(tarde)
    noite = re.search(u'Noite: ([^\n]+) \n', lista[0]).groups()[0]
    objeto.noite.clima = noite_atributo(noite)




def cidade():
    lista = {'brasilia':224 , 'sao_paulo':244, 'rio_de_janeiro':241, 'curitiba':227, 'porto_alegre':237}
    dia = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)
    for localidade in lista:
        soup = make_soup('http://servicos.cptec.inpe.br/XML/cidade/%s/previsao.xml' % lista[localidade])
        minima = soup.minima.string
        maxima = soup.maxima.string
        concatenacao = u"%s°C/%s°C" % (str(minima), str(maxima))
        setattr(cidades_brasil,localidade,concatenacao)

    lista = {'chapeco':1480 , 'itajai':2535, 'lages':2876, 'criciuma':1671, 'joinville':2808, 'blumenau':868}
    dia = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)
    for localidade in lista:
        soup = make_soup('http://servicos.cptec.inpe.br/XML/cidade/%s/previsao.xml' % lista[localidade])
        minima = soup.minima.string
        maxima = soup.maxima.string
        concatenacao = u"%s°C/%s°C" % (str(minima), str(maxima))
        setattr(cidades_sc,localidade,concatenacao)


def baixa_mar(cidade = florianopolis_outros, codigo_cidade='60245'):
    amanha = datetime.now() + timedelta(days = 1) - timedelta(hours = 5)
    dia, mes, ano = month(amanha.day), month(amanha.month), year(amanha.year)
    soup = make_soup("http://ondas.cptec.inpe.br/~rondas/mares/index.php?cod=%s&mes=%s&ano=%s"%(codigo_cidade, mes, ano))
    tuples_mares = re.findall('0*(\d\d?):(\d{2})[^\d\w]+([\d.]{3})',soup.find('strong', text='%s/%s' % (dia, mes)).parent.get_text())
    string_mares = ('\n').join(['%sh%s: %s'%t for t in tuples_mares])
    cidade.mare = string_mares

def sentence_case(string):
    lista = string.split(' ')
    lista[0] = lista[0].title()
    return(' ').join(lista)

def horario_sol(site_horario=site_horario_floripa, cidade=florianopolis_outros):
    soup = make_soup(site_horario)
    nascente = re.search('Nascer do sol:\xa0\n            ([\d\:]+)', soup.find('div','col-md-12').text).groups()[0]
    poente = re.search('P\xf4r do sol:\xa0\n            ([\d\:]+)', soup.find('div','col-md-12').text).groups()[0]
    cidade.nascente = format_time(nascente)
    cidade.poente = format_time(poente)

def cabecalho(cidade, site_cabecalho):
    cidade.cabecalho = u""


def imagem_satelite():
    imagem_sc = 'http://www.ciram.sc.gov.br/ciram_arquivos/arquivos/saidas_scripts/img/satelite/goes13IR/ultima.jpg'
    imagem = requests.get(imagem_sc, stream=True, proxies=proxy, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'})
    saida = open(r'\\172.20.0.45\jornalismo novo\Diagramação\Tempo\ultima.jpg', 'wb')
    saida.write(imagem.content)
    saida.close()


def mare(string):
    soup = make_soup(site_mar)
    for row in soup.findAll('tr')[3:]:
         if re.search(string, row.get_text()):
            teste = [item.get_text() for item in row.findAll('td')]
##            print row.get_text()
            linha = [re.findall('([\d:\.]+)',item.get_text()) for item in row.findAll('td')[1:]][2:4]
##            print linha
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


def regiao():
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
    climas = [re.findall(u'(Região:[^\n]+) .+Tarde: ([^\n]+) \n', item, re.DOTALL) for item in lista]
    for regioes in climas:
        rsetattr(mapa_estado, dicionario[regioes[0][0]] +'.'+ 'clima', dia_atributo(regioes[0][1]))


##def nome_regiao(div):
##    # retorna o nome da região, dentro da div da previsão do tempo para o próximo dia
##    return re.search('Regi\xe3o: (.+)', div.find({'span':"subtitulo"}).get_text()).group(1)

##def clima_regiao(div):
##    # retorna o clima da região

def print_objects():
    niveis = {mapa_estado:3, florianopolis:3, florianopolis_dias:3, cidades:2, florianopolis_outros:2}
    for objeto in niveis:
        print objeto.__class__.__name__
        if niveis[objeto] == 2:
            for item in objeto.__dict__:
                if item != "nome":
                   print '\t' + item + ': ' + getattr(objeto, item)
        elif niveis[objeto] == 3:
            for item in objeto.__dict__:
                if item != "nome":
                    print '\t' + item
                    for subitem in getattr(objeto, item).__dict__:
                        if subitem != "nome":
                           print '\t'*2 + subitem + ': ' + rgetattr(objeto, item + '.' + subitem)

niveis_florianopolis = {mapa_estado:3, florianopolis:3, florianopolis_dias:3, cidades_brasil:2, cidades_sc:2, florianopolis_outros:2, lista_lua:3, 'lista':[mapa_estado, florianopolis, cidades_brasil, cidades_sc, florianopolis_dias, florianopolis_outros, lista_lua]}
niveis_joinville = {mapa_estado:3, joinville:3, joinville_dias:3, cidades_brasil:2, cidades_sc:2, joinville_outros:2, 'lista':[mapa_estado, joinville, cidades_brasil, cidades_sc, joinville_dias, joinville_outros]}

def write_xml(niveis, cidade):
    root = etree.Element("root")
    for objeto in niveis['lista']:
##        print objeto.__class__.__name__
        tag = objeto.__class__.__name__
        builder_objeto = etree.SubElement(root, tag)

        if niveis[objeto] == 2:

            if 'lista' in objeto.__dict__:
               lista = objeto.lista
            else: lista = {k:v for k,v in objeto.__dict__.iteritems() if k != 'nome'}

            for item in lista:
                if item == "imagem_satelite":
##                   print getattr(objeto, item )
                   imagem_satelite = getattr(objeto, item )
                   builder_item = etree.SubElement(builder_objeto, item, href = imagem_satelite)
                elif item != "nome":
##                   print '\t'+item
                   builder_item = etree.SubElement(builder_objeto, item)
##                   print objeto, item
                   builder_item.text = getattr(objeto, item)


        elif niveis[objeto] == 3:
##             print objeto.__dict__

             if 'lista' in objeto.__dict__:

                lista = objeto.lista
             else: lista = {k:v for k,v in objeto.__dict__.iteritems() if k != 'nome'}

             for item in lista:

                if 'lista' in getattr(objeto, item).__dict__:
                   lista_subitem = rgetattr(objeto, item + ".lista")
                else: lista_subitem = {k:v for k,v in getattr(objeto, item).__dict__.iteritems() if k != 'nome'}
##                print '\t'+item
##                print '\t'+str(getattr(objeto, item).__dict__)
                builder_item = etree.SubElement(builder_objeto, item)

                for subitem in lista_subitem:
##                    print '\t'*2 + subitem+": ",
                    if subitem == "clima" or subitem == "imagem_satelite" or subitem == "caminho":
##                       print rgetattr(objeto, item + '.' + subitem)
                       clima = rgetattr(objeto, item + '.' + subitem)
                       builder_subitem = etree.SubElement(builder_item, subitem, href = clima)
                    else:
##                       print rgetattr(objeto, item + '.' + subitem)
                       builder_subitem = etree.SubElement(builder_item, subitem)
                       builder_subitem.text = rgetattr(objeto, item + '.' + subitem)

    open("previsao_%s.xml"%(cidade), 'w').write(etree.tostring(root))
    return etree.tostring(root, pretty_print=True)

def master():
	for message, function in (( 'Abrindo open-weather...', open_weather),
( 'Abrindo cidades...',cidade),
( 'Abrindo dados do mar...',baixa_mar),
( 'Descobrindo a que horas o sol trabalha...', horario_sol),
( 'Abrindo dados da região...', regiao),
( 'Abrindo dados da lua...', fases_lua2)):
  		i=0
		print message,
		while i<3:
			try:
				function()
				print 'ok'
				break
			except:
				i+=1
				sleep(5)
		if i==3:print 'erro'

def debug():
	for function in (open_weather,
    cidade,
    baixa_mar,
    horario_sol,
    regiao,
    fases_lua2,):
		function()


fases_lua2()

def local():
	os.chdir(r'S:\# Robôs\Tempo\# script')

##if __name__ == '__main__':
##
##	print 'Vamos a Florianópolis:\n'
##
##	master(), write_xml(niveis_florianopolis, 'florianopolis')
##
##	print "\n\nTudo certo. Abra os arquivos para atualizá-los."
##
##	raw_input()