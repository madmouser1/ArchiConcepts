__author__ = 'morrj140'
#!/usr/bin/python
#
# Export Archimate to Concepts
#
__author__ = 'morrj140'
__VERSION__ = '0.1'

import sys
import os
import StringIO
import time
import hashlib
import logging

from nl_lib import Logger
logger = Logger.setupLogging(__name__)
logger.setLevel(logging.INFO)

from nl_lib.Constants import *
from nl_lib.Concepts import Concepts

from lxml import etree

import nltk
from nltk import tokenize, tag, chunk
from nltk.corpus import webtext
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer

import ArchiLib as AL

class ExportArchi(object):

    def __init__(self):
        pass

    def findConcept(self, concepts, name, n=0):
        n += 1
        c = None

        if n == 3:
            return c

        for x in concepts.getConcepts().values():
            if x.name == name:
                return x
            else:
               c = self.findConcept(x, name, n)
        return c

    def getWords(self, s, concepts):
        lemmatizer = WordNetLemmatizer()

        for word, pos in nltk.pos_tag(nltk.wordpunct_tokenize(s)):
            if len(word) > 1 and pos[0] == "N":
                lemmaWord = lemmatizer.lemmatize(word.lower())
                e = concepts.addConceptKeyType(lemmaWord, "Word")
                f = e.addConceptKeyType(pos, "POS")

    def exportArchi(self, al=None):
        logger.info("Archimate File : %s" % AL.fileArchimate)
        logger.info("Export File    : %s" % AL.fileConceptsExport)

        if al == None:
            self.al = AL.ArchiLib()
            self.al.logTypeCounts()

        p, fname = os.path.split(AL.fileArchimate)

        m = hashlib.md5()

        concepts = Concepts("Node", "Nodes")

        logger.info("Found %d Nodes" % len(al.dictNodes))
        logger.info("Found %d Edges" % len(al.dictEdges))

        count = 0
        listTSort = list()
        for x in al.dictEdges.keys():
            logger.debug("Edge [%s]=%s" % (al.dictEdges[x], x))

            if al.dictEdges[x].has_key("source") and al.dictEdges[x].has_key("target"):

                typeEdge   = al.dictEdges[x][AL.ARCHI_TYPE]
                logger.debug("Edge   : %s" % typeEdge)

                source = al.dictEdges[x]["source"]
                logger.debug("Source : %s" % source)

                target = al.dictEdges[x]["target"]
                logger.debug("Target : %s" % target)

                logger.debug("  Rel    : %s" % (al.dictEdges[x][AL.ARCHI_TYPE]))

                sourceName = al.getNodeName(source)
                targetName = al.getNodeName(target)

                logger.debug(" %s--%s--%s" % (sourceName, al.dictEdges[x][AL.ARCHI_TYPE][10:], targetName))

                if al.dictNodes.has_key(source):
                    l = list()
                    sc = concepts.addConceptKeyType(sourceName, al.dictNodes[source][AL.ARCHI_TYPE][10:])
                    #getWords(sourceName, sc)

                nameEdge = "(" + sourceName + "," + targetName + ")"
                logger.debug("nameEdge : %s[%d]" % (nameEdge, len(nameEdge)))
                logger.debug("typeEdge : %s" % typeEdge[10:])

                ne = str(al.cleanString(nameEdge))
                hl = hashlib.sha224(str(ne)).hexdigest()

                logger.debug("hash : %s" % hl)

                nh = "%s-%s" % (typeEdge[10:], hl)

                rc = sc.addConceptKeyType(nh, typeEdge[10:])

                if al.dictNodes.has_key(target):
                    tc = rc.addConceptKeyType(targetName, al.dictNodes[target][AL.ARCHI_TYPE][10:])
                    #getWords(sourceName, tc)

        Concepts.saveConcepts(concepts, AL.fileConceptsExport)

        return concepts, al

if __name__ == "__main__":
    ea = ExportArchi()
    ea.exportArchi()