import re, sys, os, glob
import zipfile

curPath = os.path.dirname(os.path.abspath(__file__))

if (len(sys.argv) == 1):
   print('debe especificar el nombre del archivo')
   exit()

file =  sys.argv[1]
ext = os.path.splitext(file)[1]
regex = r"(.*)([sS][0-9]{2}[eE][0-9]{2}|[0-9]{1,2}[xX][0-9]{1,2})(.*)(mp4|mkv|avi|srt)"

def applyRegex(fileName):
   # -------------------------------------------------------------------------------------------------------------
   # debe devolver 4 grupos de captura
   # -------------------------------------------------------------------------------------------------------------
   # 1: nombre de la serie
   # 2: identificador del capitulo en formato S##E## o #X## -> ejemplo: S01E01 o 1x01
   # 3: cualquier sufijo adicional que tenga el capitulo como el grupo que lo ripeo o la descripcion del capitulo.
   # 4: la extension del capitulo (avi, mp4, mkv)
   # -------------------------------------------------------------------------------------------------------------  
   matches = re.findall(regex, fileName, re.MULTILINE)
   
   flag = False

   if (len(matches) > 0):
     if (len(matches[0]) > 0):
       flag = True

   if flag == False:
     print('Error parseando el nombre del archivo')
     exit()   

   return matches[0]

def parseFromVideoFile():
   regItm = applyRegex(file)
   titulo = regItm[0].replace("."," ").strip() 
   capitulo = regItm[1]
   extReplace =  "." + regItm[3]

   print("titulo: {}".format(titulo))
   print("capitulo: {}".format(regItm[1]))
   print("extension: {}".format(regItm[3]))   

   subs = [item.replace(curPath + "/", "") for item in glob.glob(curPath + "/*.srt") if titulo in item and capitulo in item]
   if len(subs) > 0:
      original = subs[0]
      nuevo = file.replace(extReplace, ".srt")
      print("sub original: {}".format(original))
      print("sub nuevo: {}".format(nuevo))
      resp = raw_input("Desea renombrar el archivo de subtitulo s/n:")
      if (resp in "YySs"):
         print("renombrando archivo...")
         pathOrig = os.path.join(curPath, original)
         pathNew = os.path.join(curPath, nuevo)
         os.rename(pathOrig, pathNew)
         print("proceso finalizado!")

   return

def parseFromZipRarFile():
   subInZip = ""
   print('el archivo es un {}'.format(ext))
   try:
     with zipfile.ZipFile(curPath + "/" + file, 'r') as zip_ref:
      subInZip = zip_ref.infolist()[0].filename
      print("subName: {}".format(subInZip))
      zip_ref.extractall(curPath)
   except:
     print('error descomprimiendo el archivo...')   

   if (subInZip == ""):   
     print("error obteniendo el nombre del archivo de subtitulos desde el .zip/rar")
     return

   regItm = applyRegex(subInZip)
   titulo = regItm[0].replace("."," ").strip() 
   capitulo = regItm[1]

   print("titulo: {}".format(titulo))
   print("capitulo: {}".format(regItm[1]))
   print("extension: {}".format(regItm[3]))   

   regexEpisode = r"[sS]{0,1}([0-9]{1,2})[xXEe]{0,1}([0-9]{1,2})"
   matches = re.findall(regexEpisode, capitulo, re.MULTILINE)[0]   
   
   #patron #x## -> 1x01
   subPattern1 = str(int(matches[0])) + "x" + matches[1] 
   #patron S##E## -> S01E01
   subPattern2 = "s" +   matches[0].rjust(2,"0") + "e" + matches[1]
      
   videos = [item.replace(curPath + "/", "") for item in glob.glob(curPath + "/*.mkv") if titulo in item and (subPattern1 in item.lower() or subPattern2 in item.lower())]
   videos.extend([item.replace(curPath + "/", "") for item in glob.glob(curPath + "/*.mp4") if titulo in item and (subPattern1 in item.lower() or subPattern2 in item.lower())])
   videos.extend([item.replace(curPath + "/", "") for item in glob.glob(curPath + "/*.avi") if titulo in item and (subPattern1 in item.lower() or subPattern2 in item.lower())])   
   if (len(videos) == 0):
     print("no se encontraron videos para el subtitulo seleccionado!.")
     exit()

   original = subInZip   
   extVideo = os.path.splitext(videos[0])[1]
   nuevo = videos[0].replace(extVideo, ".srt")
   
   print("sub original: {}".format(original))
   print("sub nuevo: {}".format(nuevo))     

   resp = raw_input("Desea renombrar el archivo de subtitulo s/n:")
   print("respuesta: {}".format(resp))
   if (resp in "YySs"):
      print("renombrando archivo...")
      pathOrig = os.path.join(curPath, original)
      pathNew = os.path.join(curPath, nuevo)
      zipPath = os.path.join(curPath, file) 
      os.rename(pathOrig, pathNew)
      print("eliminando el archivo .zip")
      os.remove(zipPath)
      print("proceso finalizado!")

   return

### MAIN CODE ###
if ext in ".zip|.rar":
   parseFromZipRarFile()
else:
   parseFromVideoFile()
  