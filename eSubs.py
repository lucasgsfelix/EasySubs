# coding: utf-8
# user/bin/python
import os
import re
import zipfile
import magic
# this program will be responsible to download a subtitle for a movie or tv series through
# several websites of subtitle

#https://opensubtitles.co/
#https://www.yifysubtitles.com/



def discoverTitle(fileName): #this function will be responsible to discover the title of the movie or series

    separators = [",", ".", "_", "-"]
    name = []

    ## can be case sensitive too
    for i in fileName:

        if all ( i != k for k in separators ) :
            name.append(i)

        else: #this way we have the tokens properly separated
            name.append('\t')

    return ''.join(name).split('\t')


def cleanName(name):

    ## the name will probaly have certain tokens that can be disconsidered of the name of the movie like 1080p, brRIp...etc
    tokens = ["1080p", "BrRip", "x264", "BOKUTOX", "YIFY", "DVDScr", "Hive-CM8", ]

    i=0
    while(i<len(name)):
        if any (name[i] == k for k in tokens):
            name.pop(i)
            i=i-1
        i=i+1


def makeSearch(name, movieFileTitle):

    ### this will search in the websites and make the download

    yifiSearch = "https://www.yifysubtitles.com/search?q="
    yifi = "https://www.yifysubtitles.com"
    openSubsSearch = "https://opensubtitles.co/search?q="
    k = len(name)-1

    while(k>0):
        # in the end I have to have one link
        i=0
        aux = yifiSearch
        while i<k+1:
            if(i>0):aux = aux+"+"+name[i]
            else:aux = aux+name[i]
            i=i+1

        data = downloadAndOpenFile(aux)
        if data == None:
            k=k-1
        else:
            ## here I will make the website parser to discover the "principal link"
            links = parseIt(data, "/movie-imdb/t")
            break


    if len(links)==1:

        data = readFile(yifi+links[0])
        links = parseIt(data, "/subtitles/")
        links = selectLinksByFavoriteLanguage(links, "english")


        data = readFile(yifi+links[0])
        links = parseIt(data, "/subtitle/")

        os.system("wget -O "+movieFileTitle+" "+yifi+links[0])


        if zipfile.is_zipfile(movieFileTitle): #if it's a zip file
            fileTreatment(movieFileTitle)
        else: #if it came as a srt file
            os.system("mv "+movieFileTitle+" "+movieFileTitle+".str")

    else:

        print " We don't discovered your movie title, can you type it, please ? "
        print " Is one of this your movie ?"

def fileTreatment(movieFileTitle):

    subtitle = zipfile.ZipFile(movieFileTitle)
    filesInZip = subtitle.namelist()
    subFile = srtFiles(filesInZip)
    subtitle.extract(subFile[0]) #here I have extract all files in the zip
    os.system("rm "+ movieFileTitle) ## remove the zip file
    os.system("mv "+subFile[0]+" "+movieFileTitle+".srt") #rename the sub file
    os.system("rm tempFile.html") #remove the temporary file

def srtFiles(filesInZip): # show the subtitle files in the zip

    subFile = []
    for i in filesInZip:
        j = len(i) - 1
        if i[j] == "t" and i[j-1] == "r" and i[j-2] == "s" and i[j-3] == ".":
            subFile.append(i)

    return subFile

def selectLinksByFavoriteLanguage(links, favoriteLanguage):

    i=0
    while i<len(links):
        r = [(a.start()) for a in list(re.finditer(favoriteLanguage, links[i]))]
        if len(r)==0:
            links.pop(i)
            i=i-1
        i=i+1

    return links


def readFile(name):
    os.system("wget -O tempFile.html "+ name)
    texFile = open("tempFile.html", "r")
    redableData = texFile.read()
    texFile.close()
    return redableData

def parseIt(data, search):

    r = [(a.start()) for a in list(re.finditer(search, data))]

    i=0
    links = []
    while(i<len(r)):
        p = r[i]
        while data[p] != "\"":
            links.append(data[p])
            p=p+1
        links.append('\t')
        i=i+1
    links = ''.join(links).split('\t')

    return removeRepeteadElements(links)



def removeRepeteadElements(links):


    for indexI, i in enumerate(links):
        if i == '':
            links.remove(i)

        else:
            for indexJ, j in enumerate(links):
                if i == j and indexI != indexJ:
                    links.remove(i)


    return links

def downloadAndOpenFile(name): #this function will be responsible for the download of the page and open the file

    redableData = readFile(name)
    noDiscover = ["no results", "No data record"]

    os.system("rm tempFile.html")
    #os.system("rm wget-log")
    # only yifi token
    r = [(a.start(), a.end()) for a in list(re.finditer(noDiscover[0], redableData))]

    if len(r)>0 : #which says that the subtitle that we are searching is not found

        return None

    else:

        return redableData

'''def selectFavoriteLanguage():
    # this function will give the user the liberty of choose his favorite language
    ## make a map of this
    language = {
        0 : "english"
        1 : "brazilian-portuguese"
    }'''


movieFileTitle = "La.La.Land.2016.DVDScr.XVID.AC3.HQ.Hive-CM8"
currentPath = "/home/lucasfelix/Área de Trabalho/EasySubtitles/"
name = discoverTitle(movieFileTitle)
cleanName(name)
makeSearch(name, movieFileTitle)
