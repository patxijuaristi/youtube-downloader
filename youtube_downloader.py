from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
import os
import utils

def descargarVideo(url, kw, formato, subtitulos, rutaFichero):
	yt = YouTube(url)
	if(kw == ''):
		kw = yt.streams[0].title
	kwName=utils.convertirKwEnFilename(kw)
	
	try:
		captionsDict = yt.captions
		formatoSubts = 'a.es'
		for key in captionsDict.keys():
			if 'es-ES' in str(key):
				formatoSubts = 'es-ES'
				break
			if 'en-US' in str(key):
				formatoSubts = 'en-US'
				break
			if 'a.en' in str(key):
				formatoSubts = 'a.en'
				break
		
		if(subtitulos):
			subts = yt.captions[formatoSubts].generate_srt_captions()
			f= open(rutaFichero + kwName+"-subtitulos.txt","w+", encoding='utf-8')
			f.write(subts)
			f.close()
	except Exception as e:
		print(e)
		pass
	
	try:
		if(formato == 'mp4'):
			yt.streams.filter(progressive=True).order_by('resolution').desc().first().download(filename=rutaFichero+kwName+'.mp4')
		
		if(formato == 'mp3'):
			t=yt.streams.filter()
			t[0].download(filename=rutaFichero + kwName+'.mp4')
			videoclip = VideoFileClip(rutaFichero + kwName+'.mp4')
			audioclip = videoclip.audio
			audioclip.write_audiofile(rutaFichero + kwName+'.mp3')
			audioclip.close()
			videoclip.close()
			os.remove(rutaFichero + kwName+'.mp4')
	except Exception as e:
		print(e)
		pass
	
	print(kw +' - Descargado')