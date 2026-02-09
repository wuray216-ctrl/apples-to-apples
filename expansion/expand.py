#!/usr/bin/env python3
"""
Apples to Apples - Major Data Expansion
Adds 8 new indicators + 59 new regions
"""
import os, re, random

DATA_FILE = os.path.expanduser('~/Desktop/apples-to-apples/src/data.js')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# New indicator estimates for existing regions (unemployment%, inflation%, R&D%GDP, military%GDP, popDensity, medianAge, birthRate/1000, deathRate/1000)
# Based on World Bank/UN 2023 data from training knowledge
EXISTING_EXTRA = {
    # Countries
    'us': '3.6,3.2,3.5,3.4,34,38.5,11.0,8.9',
    'cn': '5.2,0.2,2.4,1.7,149,38.5,7.5,7.2',
    'jp': '2.6,3.3,3.3,1.1,326,48.6,6.8,12.1',
    'de': '3.1,5.9,3.1,1.5,233,45.8,8.8,12.5',
    'gb': '4.0,6.7,1.7,2.1,280,40.5,10.2,9.3',
    'fr': '7.3,4.9,2.2,1.9,101,42.0,10.5,9.8',
    'in': '7.5,5.7,0.7,2.4,435,28.4,17.5,7.3',
    'br': '7.9,4.6,1.2,1.3,25,33.5,13.5,6.9',
    'it': '7.6,5.6,1.3,1.5,196,47.2,6.7,12.1',
    'ca': '5.4,3.9,1.7,1.3,4,41.1,9.5,7.8',
    'kr': '2.7,3.6,4.9,2.7,520,43.7,5.9,6.1',
    'au': '3.7,5.6,1.8,2.0,3,37.9,11.5,6.8',
    'mx': '2.8,5.5,0.3,0.6,65,29.2,16.2,5.5',
    'es': '11.7,3.5,1.4,1.3,95,44.9,7.5,9.3',
    'id': '5.5,3.7,0.3,0.7,146,29.7,16.5,7.2',
    'nl': '3.6,4.1,2.3,1.5,429,42.8,9.5,9.5',
    'sa': '5.6,2.3,0.8,6.0,17,31.8,15.2,3.8',
    'tr': '9.4,53.9,1.1,1.9,108,32.2,14.8,5.5',
    'ch': '2.0,2.2,3.4,0.7,220,42.5,9.8,8.2',
    'pl': '2.9,10.9,1.4,2.4,131,41.7,8.5,12.8',
    'se': '7.5,6.0,3.4,1.5,24,40.5,10.2,9.2',
    'be': '5.5,2.3,3.2,1.1,387,41.5,9.8,10.5',
    'th': '1.0,1.2,1.3,1.3,140,40.2,9.2,7.8',
    'at': '5.0,7.7,3.2,0.8,107,43.5,9.2,9.8',
    'no': '3.3,5.8,2.1,1.9,14,39.5,10.2,8.2',
    'il': '3.5,4.3,5.4,5.2,409,30.1,20.5,5.2',
    'ie': '4.3,5.2,1.1,0.3,71,37.8,11.5,6.5',
    'sg': '2.1,4.8,2.2,3.0,8358,35.5,8.5,4.8',
    'my': '3.5,2.5,1.0,1.0,103,30.5,15.5,5.2',
    'ph': '4.3,5.3,0.3,1.0,390,25.7,22.5,6.2',
    'vn': '2.0,3.2,0.4,2.3,299,31.9,16.2,5.8',
    'ng': '4.1,22.4,0.1,0.5,242,18.1,36.5,11.5',
    'eg': '7.0,24.4,0.7,1.2,113,24.1,22.5,5.8',
    'ar': '6.2,72.0,0.5,0.5,17,31.8,15.2,7.5',
    'za': '32.9,5.9,0.8,0.9,49,27.6,19.5,9.2',
    'dk': '2.7,3.3,2.8,2.0,140,41.7,10.2,9.5',
    'fi': '7.2,4.3,2.9,2.4,18,42.8,8.8,10.5',
    'nz': '3.4,5.7,1.4,1.5,19,37.3,11.2,6.5',
    'pt': '6.5,4.3,1.7,1.5,109,46.2,8.2,11.2',
    'cz': '2.6,12.1,1.8,1.3,127,43.0,10.2,11.5',
    'ro': '5.6,10.4,0.5,2.0,80,42.5,9.2,13.8',
    'gr': '11.2,4.5,1.5,3.7,76,45.8,7.8,12.2',
    'hu': '3.8,17.6,1.6,1.8,108,43.3,9.2,13.5',
    'ua': '24.0,12.4,0.4,33.6,61,40.5,7.8,14.5',
    'ru': '3.2,5.9,1.1,4.1,9,39.6,9.8,14.2',
    'cl': '8.5,7.6,0.4,1.9,26,35.5,12.2,6.5',
    'co': '10.5,10.2,0.3,3.4,46,30.8,14.5,5.2',
    'pe': '6.8,6.5,0.1,1.0,26,28.2,17.5,5.8',
    'pk': '6.3,29.2,0.2,3.7,261,22.8,28.5,6.8',
    'bd': '5.2,9.0,0.3,1.4,1148,27.6,18.2,5.5',
    'et': '3.5,30.2,0.3,0.5,114,19.5,32.5,6.5',
    'ke': '5.5,7.7,0.8,1.2,97,20.0,28.5,5.2',
    'gh': '4.7,23.5,0.4,0.4,138,21.1,29.5,7.2',
    'tz': '2.2,4.4,0.5,1.1,69,17.7,35.5,6.2',
    'cr': '11.5,1.5,0.4,0.0,100,33.5,12.2,5.2',
    'uy': '8.3,7.6,0.4,2.1,20,35.5,13.2,9.5',
    'pa': '8.5,1.5,0.1,0.0,57,29.8,18.5,5.2',
    'ec': '3.5,2.2,0.3,1.7,70,28.5,19.5,5.2',
    # Chinese provinces
    'cn-bj': '3.5,0.5,6.8,0.0,1375,42.5,6.8,5.5',
    'cn-sh': '4.2,0.8,4.2,0.0,4167,44.8,5.2,5.8',
    'cn-tj': '3.8,0.5,3.5,0.0,1167,42.2,6.5,6.2',
    'cn-cq': '4.5,0.2,2.1,0.0,390,40.5,7.5,7.8',
    'cn-he': '3.8,0.3,1.5,0.0,399,40.2,8.2,7.5',
    'cn-sx': '4.2,0.2,1.2,0.0,224,39.5,8.5,7.2',
    'cn-nm': '3.5,0.2,1.0,0.0,20,38.8,7.8,6.8',
    'cn-ln': '4.8,0.5,1.8,0.0,291,45.2,5.8,8.5',
    'cn-jl': '4.5,0.2,1.2,0.0,126,42.5,5.5,8.2',
    'cn-hl': '5.2,0.2,1.2,0.0,70,42.8,5.2,9.2',
    'cn-js': '3.2,0.5,2.8,0.0,825,41.5,6.8,7.2',
    'cn-zj': '3.5,0.8,2.8,0.0,623,42.2,7.2,6.5',
    'cn-ah': '3.8,0.2,2.0,0.0,436,40.8,8.5,7.5',
    'cn-fj': '3.5,0.5,2.0,0.0,341,39.5,8.8,6.8',
    'cn-jx': '3.2,0.2,1.5,0.0,269,37.8,9.2,6.5',
    'cn-sd': '3.8,0.5,2.5,0.0,650,41.2,7.5,7.8',
    'cn-ha': '4.2,0.2,1.5,0.0,593,38.5,8.8,7.2',
    'cn-hb': '4.0,0.3,2.2,0.0,312,40.2,7.8,7.5',
    'cn-hn': '3.8,0.2,1.8,0.0,311,38.8,8.5,7.2',
    'cn-gd': '3.5,0.5,3.2,0.0,706,36.5,8.5,5.5',
    'cn-gx': '4.5,0.2,1.0,0.0,210,35.8,10.5,7.2',
    'cn-hi': '4.0,0.5,0.8,0.0,286,36.5,9.8,6.2',
    'cn-sc': '4.2,0.2,1.8,0.0,173,39.2,7.8,7.5',
    'cn-gz': '4.5,0.2,0.8,0.0,222,35.5,11.2,7.2',
    'cn-yn': '4.8,0.2,0.8,0.0,119,34.8,10.8,6.8',
    'cn-xz': '2.5,0.2,0.5,0.0,3,28.5,14.5,5.0',
    'cn-sn': '3.8,0.2,2.2,0.0,194,39.5,8.2,7.2',
    'cn-gs': '4.5,0.2,0.8,0.0,59,36.5,9.2,7.5',
    'cn-qh': '3.2,0.2,0.6,0.0,8,32.5,12.5,5.8',
    'cn-nx': '3.5,0.2,0.8,0.0,106,35.2,10.5,6.5',
    'cn-xj': '4.2,0.2,0.8,0.0,16,33.5,11.8,5.5',
    # US states
    'us-al': '3.0,3.5,0.9,0.5,37,39.8,11.5,11.2',
    'us-ak': '5.8,2.5,0.5,0.5,0,34.5,12.8,6.5',
    'us-az': '3.8,3.2,0.8,0.5,24,37.5,11.2,8.2',
    'us-ar': '3.2,3.5,0.7,0.5,22,38.5,11.8,10.8',
    'us-ca': '4.5,3.5,4.8,0.5,92,37.0,11.2,7.5',
    'us-co': '3.0,3.0,2.5,0.5,22,36.8,10.8,7.2',
    'us-ct': '4.2,3.2,2.8,0.5,286,41.0,9.5,9.2',
    'us-de': '4.5,3.5,0.5,0.5,167,41.2,10.8,9.5',
    'us-fl': '3.0,3.2,1.2,0.5,135,42.5,10.2,10.5',
    'us-ga': '3.2,3.5,1.5,0.5,71,37.2,11.5,8.5',
    'us-hi': '3.2,3.0,0.8,0.5,36,40.2,11.2,8.5',
    'us-id': '2.8,3.0,0.8,0.5,9,36.5,12.5,7.8',
    'us-il': '4.5,3.5,2.2,0.5,87,38.5,11.0,9.5',
    'us-in': '3.2,3.2,1.2,0.5,74,38.0,11.5,10.2',
    'us-ia': '2.5,3.0,1.5,0.5,21,38.2,11.8,9.5',
    'us-ks': '2.8,3.2,1.5,0.5,14,37.2,12.0,9.2',
    'us-ky': '4.0,3.5,0.8,0.5,48,39.5,11.2,11.5',
    'us-la': '4.5,3.8,0.5,0.5,37,37.2,12.5,10.5',
    'us-me': '3.5,3.0,0.5,0.5,11,44.8,8.5,11.5',
    'us-md': '3.5,3.2,2.8,0.5,188,39.2,10.8,8.5',
    'us-ma': '3.5,3.2,4.5,0.5,259,39.8,9.8,8.8',
    'us-mi': '4.2,3.5,2.0,0.5,40,39.8,10.8,10.5',
    'us-mn': '2.8,3.0,2.2,0.5,27,38.2,11.2,8.2',
    'us-ms': '3.8,3.8,0.5,0.5,24,37.5,12.2,11.2',
    'us-mo': '2.8,3.5,1.2,0.5,33,39.2,11.5,10.5',
    'us-mt': '2.5,3.0,0.5,0.5,3,39.8,10.5,9.2',
    'us-ne': '2.0,3.0,1.2,0.5,10,36.5,12.5,8.8',
    'us-nv': '5.2,3.5,0.5,0.5,10,38.2,11.2,8.5',
    'us-nh': '2.2,3.0,1.2,0.5,42,43.2,8.8,9.5',
    'us-nj': '4.0,3.2,2.2,0.5,391,40.0,10.2,8.8',
    'us-nm': '5.5,3.5,1.5,0.5,6,38.5,11.5,8.5',
    'us-ny': '4.2,3.5,2.5,0.5,142,39.0,10.5,8.2',
    'us-nc': '3.5,3.2,1.5,0.5,79,39.0,11.2,9.2',
    'us-nd': '2.0,2.8,0.8,0.5,4,35.2,12.5,8.5',
    'us-oh': '4.0,3.5,1.8,0.5,103,39.5,11.0,11.2',
    'us-ok': '3.0,3.5,0.8,0.5,22,36.5,12.2,10.5',
    'us-or': '3.8,3.2,2.0,0.5,16,39.5,10.5,9.2',
    'us-pa': '4.2,3.5,2.2,0.5,109,40.8,10.5,10.8',
    'us-ri': '3.8,3.2,1.2,0.5,250,40.2,9.8,9.8',
    'us-sc': '3.2,3.5,0.8,0.5,60,39.5,11.2,10.2',
    'us-sd': '2.0,2.8,0.5,0.5,5,37.2,12.2,8.5',
    'us-tn': '3.2,3.5,1.0,0.5,64,39.0,11.5,10.8',
    'us-tx': '3.8,3.5,1.5,0.5,45,35.0,12.5,7.2',
    'us-ut': '2.2,3.0,1.5,0.5,14,31.2,14.5,5.8',
    'us-vt': '2.5,3.0,0.5,0.5,26,43.5,8.2,10.2',
    'us-va': '2.8,3.2,2.5,0.5,81,38.5,10.8,8.2',
    'us-wa': '3.8,3.2,3.5,0.5,43,38.2,10.8,7.8',
    'us-wv': '5.2,3.8,0.5,0.5,29,42.8,9.2,14.2',
    'us-wi': '2.8,3.0,1.8,0.5,35,39.5,10.8,9.5',
    'us-wy': '3.2,3.0,0.3,0.5,2,38.2,11.2,9.2',
    # Cities and subnational (added in previous patch)
    'jp-tk': '2.5,3.2,4.5,0.0,6349,45.5,7.2,8.5',
    'kr-sl': '3.0,3.5,5.2,0.0,16000,42.8,5.5,5.2',
    'gb-ln': '4.5,6.5,2.2,0.0,5598,36.5,12.5,6.2',
    'fr-pr': '6.5,4.8,3.2,0.0,1000,39.5,12.8,6.8',
    'de-by': '2.8,5.8,3.5,0.0,183,44.2,9.5,11.8',
    'de-nw': '3.5,6.0,2.2,0.0,529,44.5,9.2,12.2',
    'de-bw': '2.5,5.5,3.8,0.0,306,44.0,9.8,11.5',
    'in-mh': '5.5,5.8,0.8,0.0,409,30.5,16.2,6.5',
    'in-ka': '4.2,5.5,1.2,0.0,354,29.8,17.5,6.8',
    'in-tn': '5.8,5.5,0.6,0.0,600,33.2,14.5,7.2',
    'br-sp': '8.5,4.5,1.5,0.0,185,35.5,12.8,6.5',
    'au-nsw': '3.5,5.5,2.0,0.0,10,38.5,11.2,6.8',
    'it-lm': '5.2,5.5,1.5,0.0,417,46.5,7.2,11.8',
    'es-ct': '9.5,3.2,1.5,0.0,250,43.8,8.2,9.5',
    'mx-cd': '4.5,5.2,0.5,0.0,6000,33.5,14.2,5.8',
    # German states (added previously)
    'de-be': '8.5,5.5,3.5,0.0,4090,42.5,10.2,10.5',
    'de-hh': '5.5,5.8,2.5,0.0,2400,42.2,10.8,10.2',
    'de-he': '3.8,5.8,2.8,0.0,286,44.5,9.5,11.5',
    'de-ni': '3.0,5.5,2.0,0.0,167,44.8,8.8,12.0',
    'de-sn': '5.2,5.5,2.2,0.0,222,47.2,8.5,13.5',
    'de-sh': '3.5,5.5,1.5,0.0,188,45.2,8.8,12.5',
    'de-rp': '3.2,5.5,1.8,0.0,200,45.0,8.5,12.2',
    'de-th': '5.0,5.5,1.5,0.0,125,47.5,7.8,13.8',
    'de-bb': '5.5,5.5,1.2,0.0,100,48.2,7.5,13.2',
    'de-mv': '6.8,5.5,1.0,0.0,87,47.8,7.2,13.5',
    'de-sl': '5.8,5.5,1.5,0.0,333,46.5,7.8,13.2',
    'de-st': '6.5,5.5,1.2,0.0,100,47.8,7.5,14.2',
    'de-hb': '8.2,5.8,2.8,0.0,1599,44.0,9.2,11.5',
    # French regions
    'fr-ra': '6.5,4.5,2.2,0.0,114,41.5,10.8,8.8',
    'fr-na': '7.2,4.5,1.5,0.0,71,43.2,9.5,10.5',
    'fr-oc': '9.2,4.5,1.5,0.0,82,42.8,10.2,9.8',
    'fr-pd': '5.8,4.5,1.8,0.0,125,41.0,11.2,8.5',
    'fr-br': '5.5,4.5,1.5,0.0,111,42.5,10.5,9.2',
    'fr-hf': '9.8,4.8,1.2,0.0,188,40.5,11.5,9.5',
    'fr-ge': '7.5,4.5,1.5,0.0,103,42.2,10.2,9.8',
    'fr-paca': '8.8,4.5,1.5,0.0,161,43.5,9.8,10.2',
    # Italian regions
    'it-vn': '4.8,5.2,1.5,0.0,278,46.8,7.0,11.5',
    'it-er': '4.5,5.2,2.0,0.0,182,46.5,7.2,11.8',
    'it-pm': '6.2,5.2,1.8,0.0,160,47.5,6.8,12.5',
    'it-ts': '5.5,5.2,1.5,0.0,174,47.0,6.5,12.8',
    'it-lz': '8.2,5.5,1.8,0.0,353,44.5,7.5,10.8',
    'it-cm': '18.5,5.5,0.8,0.0,429,41.5,8.2,9.2',
    'it-si': '18.2,5.5,0.5,0.0,192,44.8,7.8,11.5',
    # Spanish regions
    'es-md': '9.2,3.2,2.0,0.0,875,42.5,8.8,8.2',
    'es-an': '18.5,3.5,0.8,0.0,103,42.2,8.5,8.8',
    'es-vc': '11.5,3.2,1.2,0.0,217,43.5,7.8,9.8',
    'es-ga': '10.2,3.2,1.0,0.0,100,48.2,6.5,12.5',
    'es-pv': '7.5,3.0,2.0,0.0,286,46.5,7.2,10.5',
    # UK
    'gb-en': '3.8,6.5,1.8,0.0,431,40.2,10.5,9.2',
    'gb-sc': '3.5,6.2,1.5,0.0,63,42.0,9.2,11.2',
    'gb-wl': '4.2,6.5,1.0,0.0,143,42.5,9.5,11.8',
    'gb-ni': '2.8,6.2,1.2,0.0,143,38.5,11.8,8.5',
    'gb-mn': '5.2,6.5,2.0,0.0,4355,38.0,12.0,9.5',
    # Japan
    'jp-os': '3.0,3.2,2.5,0.0,4631,46.5,7.0,10.2',
    'jp-ai': '1.8,3.2,3.2,0.0,1460,44.2,8.5,9.5',
    'jp-fk': '2.8,3.2,1.8,0.0,1023,44.8,8.2,10.5',
    'jp-hk': '2.5,3.2,1.2,0.0,60,49.2,6.2,13.2',
    # Canada
    'ca-on': '5.5,3.8,1.8,0.0,14,40.5,10.2,7.5',
    'ca-qc': '4.5,4.2,2.5,0.0,6,42.8,9.5,8.2',
    'ca-bc': '5.2,3.5,1.5,0.0,5,41.2,9.8,7.5',
    'ca-ab': '5.8,3.2,1.2,0.0,8,37.5,11.5,6.2',
    'ca-ns': '7.5,4.2,1.0,0.0,18,44.5,8.5,9.5',
    'ca-mb': '4.5,3.8,1.2,0.0,2,36.8,12.2,8.5',
    'ca-sk': '5.2,3.5,0.8,0.0,2,37.2,12.8,8.2',
    # Dutch, Swedish, Russian, Euro capitals
    'nl-nh': '3.2,4.0,2.8,0.0,1025,41.5,9.8,9.2',
    'nl-zh': '3.5,4.0,2.0,0.0,1333,41.2,10.2,9.5',
    'se-st': '5.5,5.8,4.5,0.0,371,39.5,11.5,7.8',
    'ru-ms': '1.5,5.5,2.5,0.0,4333,40.5,10.5,10.2',
    'ru-sp': '2.2,5.5,2.2,0.0,3991,40.2,10.2,12.5',
    'cz-pr': '1.8,12.0,3.5,0.0,2642,42.8,10.5,10.2',
    'pl-mz': '2.5,10.5,2.2,0.0,167,40.5,9.8,10.5',
    'hu-bp': '2.8,17.2,2.5,0.0,3384,42.2,9.5,12.2',
    'ro-bh': '3.5,10.2,1.5,0.0,8250,38.5,9.8,10.5',
    'at-vi': '8.5,7.5,3.8,0.0,4600,41.5,10.8,9.5',
}

print("📊 Apples to Apples - Major Data Expansion")
print("=" * 50)

with open(DATA_FILE, 'r') as f:
    content = f.read()

# Step 1: Add 8 new fields to every existing data line
print("\n1️⃣  Adding 8 new indicators to all existing regions...")

lines = content.split('\n')
new_lines = []
modified_count = 0

for line in lines:
    # Check if this is a data line (inside the RAW template literal)
    # Data lines start with a region id like 'us,' or 'cn-bj,'
    stripped = line.strip()
    if stripped and not stripped.startswith('//') and not stripped.startswith('const') and not stripped.startswith('`') and ',' in stripped:
        # Try to extract the id
        parts = stripped.split(',')
        if len(parts) == 27:
            region_id = parts[0]
            if region_id in EXISTING_EXTRA:
                line = line.rstrip() + ',' + EXISTING_EXTRA[region_id]
                modified_count += 1
            else:
                # Unknown region - add reasonable defaults
                line = line.rstrip() + ',,,,,,,,'
                modified_count += 1
    new_lines.append(line)

content = '\n'.join(new_lines)
print(f"   Modified {modified_count} existing regions")

# Step 2: Add new regions before closing backtick
print("\n2️⃣  Adding 59 new regions...")
new_regions_file = os.path.join(SCRIPT_DIR, 'new_regions_v2.txt')
with open(new_regions_file, 'r') as f:
    new_data = f.read().strip()

content = content.replace('`.trim();', new_data + '\n`.trim();')

# Step 3: Update the field comment
print("\n3️⃣  Updating field documentation...")
content = content.replace(
    '// Field order: id,name,type,parent,flag,pop(M),gdp(B$),gdpPC,area(k),urban%,gini,hdi,net%,lifeExp,co2PC,unis,lit%,pisa,docs,beds,health%,mfg%,exp(B),fdi(B),forest%,pm25,renew%',
    '// Field order: id,name,type,parent,flag,pop(M),gdp(B$),gdpPC,area(k),urban%,gini,hdi,net%,lifeExp,co2PC,unis,lit%,pisa,docs,beds,health%,mfg%,exp(B),fdi(B),forest%,pm25,renew%,unemp%,inflate%,rd%,mil%,popDens,medAge,birthR,deathR'
)
content = content.replace('// 320+ regions, 22 indicators', '// 380+ regions, 30 indicators')
content = content.replace('// 250+ regions, 18 indicators', '// 380+ regions, 30 indicators')

# Step 4: Update the parser to handle 35 fields
print("\n4️⃣  Updating data parser...")
old_parser = """    const [id,name,type,parent,flag,pop,gdp,gdpPC,area,urban,gini,hdi,net,life,co2,uni,lit,pisa,doc,bed,health,mfg,exp,fdi,forest,pm25,renew] = line.split(',');
    return {
      id, name, type, parent: parent || null, flag,
      population: parseFloat(pop) * 1e6 || null,
      gdp: parseFloat(gdp) * 1e3 || null,
      gdpPerCapita: parseFloat(gdpPC) || null,
      area: parseFloat(area) * 1e3 || null,
      urbanization: parseFloat(urban) || null,
      gini: parseFloat(gini) || null,
      hdi: parseFloat(hdi) || null,
      internetPenetration: parseFloat(net) || null,
      lifeExpectancy: parseFloat(life) || null,
      co2PerCapita: parseFloat(co2) || null,
      universityCount: parseFloat(uni) || null,
      literacyRate: parseFloat(lit) || null,
      pisaScore: parseFloat(pisa) || null,
      doctorsPer1000: parseFloat(doc) || null,
      hospitalBeds: parseFloat(bed) || null,
      healthExpenditure: parseFloat(health) || null,
      manufacturingPct: parseFloat(mfg) || null,
      exports: parseFloat(exp) * 1e3 || null,
      fdiInflow: parseFloat(fdi) * 1e3 || null,
      forestCoverage: parseFloat(forest) || null,
      airQualityPM25: parseFloat(pm25) || null,
      renewableEnergy: parseFloat(renew) || null,
    };"""

new_parser = """    const [id,name,type,parent,flag,pop,gdp,gdpPC,area,urban,gini,hdi,net,life,co2,uni,lit,pisa,doc,bed,health,mfg,exp,fdi,forest,pm25,renew,unemp,inflate,rd,mil,popDens,medAge,birthR,deathR] = line.split(',');
    return {
      id, name, type, parent: parent || null, flag,
      population: parseFloat(pop) * 1e6 || null,
      gdp: parseFloat(gdp) * 1e3 || null,
      gdpPerCapita: parseFloat(gdpPC) || null,
      area: parseFloat(area) * 1e3 || null,
      urbanization: parseFloat(urban) || null,
      gini: parseFloat(gini) || null,
      hdi: parseFloat(hdi) || null,
      internetPenetration: parseFloat(net) || null,
      lifeExpectancy: parseFloat(life) || null,
      co2PerCapita: parseFloat(co2) || null,
      universityCount: parseFloat(uni) || null,
      literacyRate: parseFloat(lit) || null,
      pisaScore: parseFloat(pisa) || null,
      doctorsPer1000: parseFloat(doc) || null,
      hospitalBeds: parseFloat(bed) || null,
      healthExpenditure: parseFloat(health) || null,
      manufacturingPct: parseFloat(mfg) || null,
      exports: parseFloat(exp) * 1e3 || null,
      fdiInflow: parseFloat(fdi) * 1e3 || null,
      forestCoverage: parseFloat(forest) || null,
      airQualityPM25: parseFloat(pm25) || null,
      renewableEnergy: parseFloat(renew) || null,
      unemployment: parseFloat(unemp) || null,
      inflation: parseFloat(inflate) || null,
      rdExpenditure: parseFloat(rd) || null,
      militarySpending: parseFloat(mil) || null,
      populationDensity: parseFloat(popDens) || null,
      medianAge: parseFloat(medAge) || null,
      birthRate: parseFloat(birthR) || null,
      deathRate: parseFloat(deathR) || null,
    };"""

content = content.replace(old_parser, new_parser)

# Step 5: Add new indicators to INDICATORS object
print("\n5️⃣  Adding new indicator definitions...")
old_renew_line = "  renewableEnergy: { label: 'Renewable %', unit: '%', color: '#059669', format: v => v ? v.toFixed(0)+'%' : 'N/A', category: 'environment' },"
new_indicators = """  renewableEnergy: { label: 'Renewable %', unit: '%', color: '#059669', format: v => v ? v.toFixed(0)+'%' : 'N/A', category: 'environment' },
  unemployment: { label: 'Unemployment %', unit: '%', color: '#dc2626', format: v => v ? v.toFixed(1)+'%' : 'N/A', category: 'economic' },
  inflation: { label: 'Inflation %', unit: '%', color: '#b91c1c', format: v => v ? v.toFixed(1)+'%' : 'N/A', category: 'economic' },
  rdExpenditure: { label: 'R&D % GDP', unit: '%', color: '#7c3aed', format: v => v ? v.toFixed(1)+'%' : 'N/A', category: 'economic' },
  militarySpending: { label: 'Military % GDP', unit: '%', color: '#374151', format: v => v ? v.toFixed(1)+'%' : 'N/A', category: 'economic' },
  populationDensity: { label: 'Pop. Density', unit: '/km²', color: '#d97706', format: v => v ? v.toLocaleString()+'/km²' : 'N/A', category: 'basic' },
  medianAge: { label: 'Median Age', unit: 'yrs', color: '#9333ea', format: v => v ? v.toFixed(1)+' yrs' : 'N/A', category: 'demographic' },
  birthRate: { label: 'Birth Rate', unit: '‰', color: '#2563eb', format: v => v ? v.toFixed(1)+'‰' : 'N/A', category: 'demographic' },
  deathRate: { label: 'Death Rate', unit: '‰', color: '#475569', format: v => v ? v.toFixed(1)+'‰' : 'N/A', category: 'demographic' },"""

content = content.replace(old_renew_line, new_indicators)

# Step 6: Update INDICATOR_CATEGORIES
print("\n6️⃣  Updating indicator categories...")
old_categories = """export const INDICATOR_CATEGORIES = {
  basic: { label: '📊 Basic', keys: ['population', 'gdp', 'gdpPerCapita', 'area', 'urbanization', 'hdi', 'internetPenetration'] },
  economic: { label: '💰 Economic', keys: ['gdp', 'gdpPerCapita', 'gini', 'manufacturingPct', 'exports', 'fdiInflow'] },
  education: { label: '🎓 Education', keys: ['universityCount', 'literacyRate', 'pisaScore'] },
  health: { label: '🏥 Healthcare', keys: ['lifeExpectancy', 'doctorsPer1000', 'hospitalBeds', 'healthExpenditure'] },
  environment: { label: '🌿 Environment', keys: ['co2PerCapita', 'forestCoverage', 'airQualityPM25', 'renewableEnergy'] },
};"""

new_categories = """export const INDICATOR_CATEGORIES = {
  basic: { label: '📊 Basic', keys: ['population', 'gdp', 'gdpPerCapita', 'area', 'urbanization', 'hdi', 'internetPenetration', 'populationDensity'] },
  economic: { label: '💰 Economic', keys: ['gdp', 'gdpPerCapita', 'gini', 'manufacturingPct', 'exports', 'fdiInflow', 'unemployment', 'inflation', 'rdExpenditure', 'militarySpending'] },
  education: { label: '🎓 Education', keys: ['universityCount', 'literacyRate', 'pisaScore'] },
  health: { label: '🏥 Healthcare', keys: ['lifeExpectancy', 'doctorsPer1000', 'hospitalBeds', 'healthExpenditure'] },
  environment: { label: '🌿 Environment', keys: ['co2PerCapita', 'forestCoverage', 'airQualityPM25', 'renewableEnergy'] },
  demographic: { label: '👥 Demographics', keys: ['populationDensity', 'medianAge', 'birthRate', 'deathRate', 'urbanization'] },
};"""

content = content.replace(old_categories, new_categories)

# Step 7: Update MATCH_PRESETS comprehensive weights
print("\n7️⃣  Updating match presets...")
old_comp = "  comprehensive: { label: '📊 All', weights: { population: 0.08, gdp: 0.08, gdpPerCapita: 0.1, area: 0.05, urbanization: 0.06, hdi: 0.1, lifeExpectancy: 0.08, universityCount: 0.05, doctorsPer1000: 0.05, manufacturingPct: 0.05, forestCoverage: 0.05, renewableEnergy: 0.05, literacyRate: 0.05, internetPenetration: 0.05, co2PerCapita: 0.05, gini: 0.05 } },"
new_comp = "  comprehensive: { label: '📊 All', weights: { population: 0.06, gdp: 0.06, gdpPerCapita: 0.08, area: 0.04, urbanization: 0.04, hdi: 0.08, lifeExpectancy: 0.06, universityCount: 0.04, doctorsPer1000: 0.04, manufacturingPct: 0.04, forestCoverage: 0.04, renewableEnergy: 0.04, literacyRate: 0.04, internetPenetration: 0.04, co2PerCapita: 0.04, gini: 0.04, unemployment: 0.04, medianAge: 0.04, rdExpenditure: 0.04, populationDensity: 0.04, birthRate: 0.02, deathRate: 0.02, inflation: 0.02, militarySpending: 0.02 } },"
content = content.replace(old_comp, new_comp)

# Step 8: Update SHOWCASE_GROUPS
print("\n8️⃣  Updating showcase groups...")
old_showcase = """export const SHOWCASE_GROUPS = [
  { title: 'Industrial Powerhouses', subtitle: 'Manufacturing giants', ids: ['de-by', 'cn-zj', 'us-tx', 'jp-ai'] },
  { title: 'City-States & Hubs', subtitle: 'Financial centers', ids: ['sg', 'kr-sl', 'cn-sh', 'de-hh'] },
  { title: 'Tech & Innovation', subtitle: 'Silicon Valleys', ids: ['us-ca', 'gb-ln', 'cn-js', 'se-st'] },
  { title: 'Emerging Economies', subtitle: 'Rising powers', ids: ['in-mh', 'br-sp', 'vn', 'co'] },
  { title: 'Small but Mighty', subtitle: 'High GDP/capita', ids: ['nl', 'ch', 'us-ma', 'es-pv'] },
  { title: 'European Regions', subtitle: 'Cross-border comparison', ids: ['de-bw', 'fr-ra', 'it-lm', 'es-ct'] },
  { title: 'Global Capitals', subtitle: 'Metro areas', ids: ['jp-tk', 'gb-ln', 'fr-pr', 'ru-ms'] },
  { title: 'Canadian Provinces', subtitle: 'North American diversity', ids: ['ca-on', 'ca-bc', 'ca-ab', 'ca-qc'] },
  { title: 'Green Leaders', subtitle: 'Renewable energy', ids: ['no', 'us-vt', 'cr', 'ca-qc'] },
  { title: 'Healthcare Excellence', subtitle: 'Best health outcomes', ids: ['jp', 'ch', 'es', 'it-lm'] },
];"""

new_showcase = """export const SHOWCASE_GROUPS = [
  { title: 'Industrial Powerhouses', subtitle: 'Manufacturing giants', ids: ['de-by', 'cn-zj', 'us-tx', 'jp-ai'] },
  { title: 'City-States & Hubs', subtitle: 'Financial centers', ids: ['sg', 'kr-sl', 'cn-sh', 'de-hh'] },
  { title: 'Tech & Innovation', subtitle: 'R&D leaders', ids: ['us-ca', 'il', 'kr', 'se-st'] },
  { title: 'Emerging Economies', subtitle: 'Rising powers', ids: ['in-mh', 'br-sp', 'vn', 'co'] },
  { title: 'Small but Mighty', subtitle: 'High GDP/capita', ids: ['sg', 'ch', 'qa', 'ie'] },
  { title: 'European Regions', subtitle: 'Cross-border comparison', ids: ['de-bw', 'fr-ra', 'it-lm', 'es-ct'] },
  { title: 'Global Capitals', subtitle: 'Metro areas', ids: ['jp-tk', 'gb-ln', 'fr-pr', 'ru-ms'] },
  { title: 'India Rising', subtitle: 'Diverse subcontinent', ids: ['in-dl', 'in-ke', 'in-gj', 'in-ka'] },
  { title: 'Brazil Coast to Interior', subtitle: 'Latin giant', ids: ['br-sp', 'br-rj', 'br-sc', 'br-am'] },
  { title: 'Young vs Aging', subtitle: 'Demographics contrast', ids: ['ng', 'jp', 'et', 'de'] },
  { title: 'Green Leaders', subtitle: 'Renewable energy', ids: ['no', 'cr', 'ca-qc', 'cn-yn'] },
  { title: 'Healthcare Excellence', subtitle: 'Best outcomes', ids: ['jp', 'ch', 'kr', 'es'] },
];"""

content = content.replace(old_showcase, new_showcase)

# Step 9: Update region count in Compare.jsx nav
print("\n9️⃣  Updating region count display...")

compare_file = os.path.expanduser('~/Desktop/apples-to-apples/src/pages/Compare.jsx')
with open(compare_file, 'r') as f:
    compare = f.read()
compare = compare.replace(
    "{REGIONS.length} regions • 10 indicators",
    "{REGIONS.length} regions • {Object.keys(INDICATORS).length} indicators"
)
# Also update the i18n version if present
compare = compare.replace(
    "t('compare.region_count', { count: REGIONS.length })",
    "t('compare.region_count', { count: REGIONS.length, indicators: Object.keys(INDICATORS).length })"
)
with open(compare_file, 'w') as f:
    f.write(compare)

with open(DATA_FILE, 'w') as f:
    f.write(content)

print("\n" + "=" * 50)
print("✅ Expansion complete!")
print(f"   📍 ~59 new regions added")
print(f"   📊 8 new indicators: Unemployment, Inflation,")
print(f"      R&D %, Military %, Pop Density, Median Age,")
print(f"      Birth Rate, Death Rate")
print(f"   🏷️ New category: 👥 Demographics")
print(f"   🎯 12 showcase groups (up from 10)")
print()
print("Run: cd ~/Desktop/apples-to-apples && npm run build")
