import requests

from tqdm import tqdm

from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import re

import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

import pandas as pd

import numpy as np

from astroquery.mast import Observations
from astroquery.simbad import Simbad

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos= set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, 
                                  password=password,caching=caching, 
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

class Recon:
    """
    Performance of web reconnaisanse on an interesting target.
    
    Attributes:
        aliases : (list of strings) names by which the target is known in other catalogs.
        input_name : (str) name of target you're interested in.
        webb_approved : (bool) whether or not the target has been included in approved webb program.
        webb_proposal_link : (list of strings) if there are associated JWST proposals, these
                                are the associated URLs.
        HST_data : (dict)
        exoplanet_archive_data : (dict)
                

        any other atmospheric data from exoplanet catologue
        link to arxv scrape
    
    
    Methods:
        __init__ : initializes.
        find_aliases :
    """
    aliases = []
    input_name = None
    webb_approved = None
    hst_approved = None
    webb_proposal_links = []
    webb_proposal_names = []
    hst_data = {}
    exoplanet_archive_data = {}
    arxiv_links = []
    
    def __init__(self, input_name):
        self.input_name = input_name
        
    def search_webb_site(self, URL):
        """
        Checks whether self has been approved via GTO or ERS. Needs debugging as missing above targets still.
        Adds any links to webb_proposal_links. changed webb_approved. not validated to ERS.
        """
        if not self.aliases:
            print('Not checking aliases.')
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')

        all_targets = []

        gto_pages = []
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                str_begin = '/jwst/observing-programs/program-information?id='
                if link.attrs['href'][:48] == str_begin:
                    gto_page = 'http://www.stsci.edu/' + link.attrs['href'] # give better name
                    gto_pages.append(gto_page)

        for gto_page in tqdm(gto_pages, position=0, leave=True):
            ID = gto_page[-4:]
            pdf_link = f'http://www.stsci.edu/jwst/phase2-public/{ID}.pdf'
            urlretrieve(pdf_link, "tmp.pdf")
            text = convert_pdf_to_txt("tmp.pdf")
            start = text.find("Science Target") + len("Science Target")
            end = text.find("ABSTRACT")
            target_table = text[start:end]
            targets = list(set(re.findall(r"""\(\d\)\ (\w+)""", target_table)))
        #         targets += list(set(re.findall(r"""\(\d\)(\w+)""", target_table)))
            targets += list(set(re.findall(r"""\(\d\)\ (\w+-\w+)""", target_table)))
            targets += list(set(re.findall(r"""\(\d\)\ (\w+-\w+-\w+)""", target_table))) # for HAT-P-35, for example
            targets += list(set(re.findall(r"""\(\d\)\ (\w+ \w+)""", target_table)))
            in_targets = [a for a in self.aliases if a in targets]
            if len(in_targets) > 0 and self.input_name in _targets:
                self.webb_approved = True
                self.webb_proposal_links.append(pdf_link)
            os.remove('tmp.pdf')
        if self.webb_approved is None: # has not been changed to True
            self.webb_approved = False
        return
    
    def search_GTO(self):
        URL = 'http://www.stsci.edu/jwst/observing-programs/approved-gto-programs'
        self.search_webb_site(URL)
        
    def search_ERS(self):
        URL = 'http://www.stsci.edu/jwst/observing-programs/approved-ers-programs'
        self.search_webb_site(URL)
        
    def search_webb(self):
        self.search_GTO()
        self.search_ERS()
    
    def find_aliases(self):
        self.aliases += list(Simbad.query_objectids(self.input_name)['ID'])
    
    def scrape_HST(self):
        """
        Checks MAST
        Need to fill in the other stuff
        """
        obs = Observations.query_object(self.input_name, radius=".02 deg") # should work. waliases
        HST_obs = obs[obs['obs_collection']=='HST']
        if len(HST_obs) > 0:
            self.hst_approved = True
            for ob in HST_obs:
                self.hst_data[ob['obs_title']] = ob['dataURL']
        if self.hst_approved is None:
            self.hst_approved = False
        
    def scrape_webb_MAST(self):
        """
        Uses MAST to scrape. Does not seem to work for ERS.
        Need to fill in other stuff
        """
        obs = Observations.query_object(self.input_name, radius=".02 deg") # should work. waliases
        JWST_obs = obs[obs['obs_collection']=='JWST']
        if len(JWST_obs) > 0:
            self.webb_approved = True
            for ob in JWST_obs:
                self.webb_proposal_names.append(ob['obs_title'])
        if self.webb_approved is None:
            self.webb_approved = False
        return
        
    
    def scrape_arxiv(self, progress=False):
        """
        Searches through arxiv abstracts for the target.
        Does not take aliases into account yet.
        """
        if self.aliases:
            for alias in tqdm(self.aliases, position=0, leave=True, desc='Scraping arXiv'):
                query_URL = f'https://arxiv.org/search/astro-ph?query={alias}&searchtype=abstract&abstracts=show&order=-announced_date_first&size=50'
                page = requests.get(query_URL)
                soup = BeautifulSoup(page.content, 'html.parser')
                for link in soup.find_all('a'):
                    try:
                        paper = link.get('href')
                        if 'pdf'in paper and paper not in self.arxiv_links:
                            self.arxiv_links.append(paper)
                    except TypeError:
                        continue
        else: # I'm sure there's a more elegant way to do this!
            query_URL = f'https://arxiv.org/search/astro-ph?query={self.input_name}&searchtype=abstract&abstracts=show&order=-announced_date_first&size=50'
            page = requests.get(query_URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            for link in soup.find_all('a'):
                try:
                    paper = link.get('href')
                    if 'pdf'in paper and paper not in self.arxiv_links:
                        self.arxiv_links.append(paper)
                except TypeError:
                    continue
            
    
    def scrape_exoplanet_archive(self):
        if not self.aliases:
            print('Not checking aliases.')
        raise NotImplementedError
        
    def scrape_all(self):
        self.find_aliases()
        self.scrape_arxiv()
        self.scrape_webb_MAST()
        self.scrape_HST()
        
def scrape_all_GTO():
    """
    Gets all science targets of all JWST GTO programs that have hit phase 2.
    Takes around 4 minutes on Arjun's mac.
    
    outputs:
        
    """
    URL = 'http://www.stsci.edu/jwst/observing-programs/approved-gto-programs'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    all_targets = []

    gto_pages = []
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            str_begin = '/jwst/observing-programs/program-information?id='
            if link.attrs['href'][:48] == str_begin:
                gto_page = 'http://www.stsci.edu/' + link.attrs['href'] # give better name
                gto_pages.append(gto_page)

    for gto_page in tqdm(gto_pages, position=0, leave=True):
        ID = gto_page[-4:]
        pdf_link = f'http://www.stsci.edu/jwst/phase2-public/{ID}.pdf'
        urlretrieve(pdf_link, "tmp.pdf")
        text = convert_pdf_to_txt("tmp.pdf")
        start = text.find("Science Target") + len("Science Target")
        end = text.find("ABSTRACT")
        target_table = text[start:end]
        targets = list(set(re.findall(r"""\(\d\)\ (\w+)""", target_table)))
#         targets += list(set(re.findall(r"""\(\d\)(\w+)""", target_table)))
        targets += list(set(re.findall(r"""\(\d\)\ (\w+-\w+)""", target_table)))
        targets += list(set(re.findall(r"""\(\d\)\ (\w+-\w+-\w+)""", target_table))) # for HAT-P-35, for example
        targets += list(set(re.findall(r"""\(\d\)\ (\w+ \w+)""", target_table)))
        all_targets += targets
        os.remove('tmp.pdf')
    return list(set(all_targets))
        