from flask import Flask, url_for, request, render_template, redirect
import httplib2
import os
import re
import sys
import pafy, zipfile, math


from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

app = Flask(__name__)


DEVELOPER_KEY = "AIzaSyAt2kWulfcDsdid2AQ2iXh7_aRcNj8ay9g"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



@app.route('/')
def load():
    return render_template('basic.html')

@app.route('/result',methods=['GET','POST'])
def result():
   if request.method == 'POST':
      result = request.form
      
      return youtube_search(request.form['category'],request.form['difficulty'], request.form['age'],request.form['keywords'] )
      #return render_template("result.html",result = result)

def youtube_search(cat,diff,age,keyw):
  	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

	search_response = youtube.search().list(
	    q=cat + keyw,
	    part="id,snippet",
	    maxResults=25
	  ).execute()

	videos = []

  # Add each result to the appropriate list, and then display the lists of
	  # matching videos, channels, and playlists.
	for search_result in search_response.get("items", []):
		if search_result["id"]["kind"] == "youtube#video":
		  videos.append("%s (%s)" % (search_result["snippet"]["title"],
		                             search_result["id"]["videoId"]))

	print "Videos:\n", "\n".join(videos), "\n"
	return download_vids(videos) 
	# need to be URLS

def download_vids(vidArray):
    max_viewcount = 0
    scored_vids = []
# https://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
    if not os.path.exists("static/vids/"):
        os.makedirs("static/vids/")
    for x in vidArray:
        url = "https://www.youtube.com/watch?v=" + x
        video = pafy.new(url)
        ##owen's shit
        score = 0
        if (video.viewcount > max_viewcount):
            max_viewcount = video.viewcount
        score = score + (math.sqrt(video.rating)) + (video.viewcount / max_viewcount) ##+ count

        s = video.allstreams[1]
        scored_vids.append(tuple((score, s)))
    scored_vids.sort(key = lambda tup: tup[0], reverse=True)
    for i in range(0, len(scored_vids)):
        global count
        count += 1
        filename = scored_vids[i][1].download("static/vids/" + str(count) + ".mp4")

        # global count
        # count += 1
        # filename = s.download("static/vids/" + str(count) + ".mp4")    
    return redirect(url_for('done'))

@app.route('/done')
def done():
    zipdir('static/vids')
    return app.send_static_file('content.zip')

# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
def zipdir(path):
    zf = zipfile.ZipFile("static/content.zip", "w")
    for root, dirs, files in os.walk(path):
        for file in files:
            zf.write(os.path.join(root, file))



if __name__ == '__main__':
   app.run(debug = True)

