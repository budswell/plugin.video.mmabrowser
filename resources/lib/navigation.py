#!/usr/bin/env python

import os
import xbmc
import xbmcaddon
import xbmcvfs

from resources.lib.utils import *
import resources.lib.databaseops as dbops
import resources.lib.library as library

### get addon info
__addon__             = xbmcaddon.Addon()
__addonpath__         = __addon__.getAddonInfo('path')


def mainMenu():
    log('Showing main menu')
    addDir("Browse by: Organisation", "/browsebyorganisation/", os.path.join(__addonpath__, "resources", "images", "generic_poster.jpg"), "", "Browse a list of all MMA Promotions in your library.")
    addDir("Browse by: Fighter", "/browsebyfighter/", os.path.join(__addonpath__, "resources", "images", "generic_poster.jpg"), "", "Browse a list of all fighters in your library")
    addDir("All Events", "/allevents/", os.path.join(__addonpath__, "resources", "images", "generic_poster.jpg"), "", "Browse a list of all events in your library")
    addDir("Search", "/search/", os.path.join(__addonpath__, "resources", "images", "generic_poster.jpg"), "", "Search all items in your library")

def allEvents():
    log('Browsing: All events')
    for event in dbops.getAllEvents():
        for x in library.loadLibrary():
            if event[0] == x['ID']:
                fightList = dbops.getFightersByEvent(event[0])
                addEvent(event[0], event[1], event[2], event[3], event[4], event[5], fightList)

def browseByOrganisation():
    log('Browsing: Organisations')
    for promotion in dbops.getAllPromotions():
        addPromotion(promotion[0])

def getEventsByOrganisation(organisation):
    log('Listing all events for: %s' % organisation)
    for event in dbops.getEventsByPromotion(organisation):
        for x in library.loadLibrary():
            if event[0] == x['ID']:
                fightList = dbops.getFightersByEvent(event[0])
                addEvent(event[0], event[1], event[2], event[3], event[4], event[5], fightList)

def browseByFighter():
    log('Browsing: Fighters')
    for fighter in dbops.getAllFighters():
        addFighter(fighter[0], fighter[1], fighter[2], fighter[3], fighter[4], fighter[5], fighter[6], fighter[7], fighter[8], fighter[9], fighter[10], dbops.getFightCount(fighter[0]))

def getEventsByFighter(fighterID):
    log('Listing all events for: %s' % fighterID)
    for event in dbops.getEventsByFighter(fighterID):
        for x in library.loadLibrary():
            if event[0] == x['ID']:
                fightList = dbops.getFightersByEvent(event[0])
                addEvent(event[0], event[1], event[2], event[3], event[4], event[5], fightList)

def searchAll():
    log('Searching MMA Library')
    searchStr = getUserInput(title = "Search MMA Library")
    for event in dbops.searchEvents(searchStr):
        for x in library.loadLibrary():
            if event[0] == x['ID']:
                fightList = dbops.getFightersByEvent(event[0])
                addEvent(event[0], event[1], event[2], event[3], event[4], event[5], fightList)
    for fighter in dbops.searchFighters(searchStr):
        addFighter(fighter[0], fighter[1], fighter[2], fighter[3], fighter[4], fighter[5], fighter[6], fighter[7], fighter[8], fighter[9], fighter[10], dbops.getFightCount(fighter[0]))

def getEvent(eventID):
    event = dbops.getEvent(eventID)
    log('Listing video files for event: %s' % event[1])
    for x in library.loadLibrary():
        if event[0] == x['ID']:
            thumbPath = os.path.join(__thumbDir__, '%s-poster.jpg' % x['ID'])
            if not xbmcvfs.exists(thumbPath):
                thumbPath = os.path.join(__promotionDir__, '%s-poster.jpg' % event[2].replace(' ', ''))
            fanartPath = os.path.join(__thumbDir__, '%s-fanart.jpg' % x['ID'])
            if not xbmcvfs.exists(fanartPath):
                fanartPath = os.path.join(__promotionDir__, '%s-fanart.jpg' % event[2].replace(' ', ''))
            outline = '%s: %s, %s' % (event[3], event[4], event[5])
            try:
                description = open(os.path.join(__thumbDir__, '%s-description.txt' % event[0])).read()
            except IOError:
                description = outline
            fileList = []
            for root, dirs, files in os.walk(x['path']):
                for vidFileName in files:
                    vidFile = {}
                    vidFile['filename'] = vidFileName
                    vidFile['ext'] = os.path.splitext(vidFileName)[1]
                    vidFile['path'] = os.path.join(root, vidFileName)
                    if __addon__.getSetting("cleanFilenames") == 'true':
                        vidFile['title'] = os.path.splitext(vidFileName)[0].lstrip('0123456789. ')
                    else:
                        vidFile['title'] = vidFileName
                    if vidFile['ext'] in ['.mkv', '.mp4', '.flv', '.avi', '.iso', '.mpg', '.ts']:
                        fileList.append(vidFile)
                    else:
                        log('File ignored: %s' % vidFile['path'])
            if len(fileList) == 1:
                xbmc.Player().play(fileList[0]['path'])
                sys.exit(0)
            else:
                for vidFile in sorted(fileList, key=lambda k: k['filename']):
                    addLink(linkName = vidFile['title'], plotoutline = outline, plot = description, url = vidFile['path'], thumbPath = thumbPath, fanartPath = fanartPath, genre = 'MMA')