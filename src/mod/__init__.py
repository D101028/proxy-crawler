"""
This mod is the place to write your 
own crawler objects. To enable the 
crawler, import the crawler object
and add it into the following list.
"""

from .template import CrawlerTemplate
from .example import ExampleCrawler     # Example of importing crawler object
from .geonode_com import GeonodeCrawler

# The list to put in your own crawler class
crawler_classes: list[type[CrawlerTemplate]] = [
    ExampleCrawler, # Example of enabling the crawler
    GeonodeCrawler, 
]