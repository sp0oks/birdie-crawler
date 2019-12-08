# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Oferta(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    categoria = scrapy.Field()
    titulo = scrapy.Field()
    disponivel = scrapy.Field()
    moeda = scrapy.Field()
    preco = scrapy.Field()
    descricao = scrapy.Field()
    caracteristicas = scrapy.Field()
