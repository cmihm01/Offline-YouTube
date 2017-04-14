from flask import Flask, url_for, request, render_template, redirect
# import httplib2
import os
import re
import sys
import pafy, zipfile, math, shutil

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

app = Flask(__name__)

count = 0

DEVELOPER_KEY = "AIzaSyAt2kWulfcDsdid2AQ2iXh7_aRcNj8ay9g"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



@app.route('/')
def load():
    return render_template('basic.html')

@app.route('/result',methods=['GET','POST'])
def result():
    # render_template('loading.html') needs to happen here
   if request.method == 'POST':
      result = request.form
      
      return youtube_search(request.form['category'],request.form['difficulty'], request.form['age'],request.form['keywords'] )
      #return render_template("result.html",result = result)

def youtube_search(cat,diff,age,keyw):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=cat + keyw,
        part="id,snippet",
        maxResults=5
      ).execute()

    scored_results = score_and_sort(search_response, keyw)
    render_template("select.html", videos=scored_results)


def score_and_sort(search_response, keyw):
    scored_vids = []
    scored_results = []
    # videothumbs = []
    max_viewcount = 0

  # Add each result to the appropriate list, and then display the lists of
      # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            pvideo = pafy.new(search_result["id"]["videoId"])
            score = 0
            if (pvideo.viewcount > max_viewcount):
                max_viewcount = pvideo.viewcount
            score = score + (pvideo.rating) + (pvideo.viewcount / max_viewcount)
            print search_result["snippet"]["description"]
            if keyw in (search_result["snippet"]["description"]):
               score = score + 1
            scored_vids.append(tuple((score, search_result)))
    scored_vids.sort(key = lambda tup: tup[0], reverse=True)

    for i in range(0, len(scored_vids)):
        scored_results.append(scored_vids[i][1])

    # videothumbs.append(search_result["snippet"]["thumbnails"]["default"]["url"])
     #"%s (%s)" % (search_result["snippet"]["title"]
    # print "Videothumbs:\n", "\n".join(videothumbs), "\n"
    # print "Videos:\n", "\n".join(videos), "\n"
    
    # I need to give a list of videos to the download vids function 
    return scored_results
    # need to be URLS

def download_vids(vidArray):
    max_viewcount = 0
    scored_vids = []
# https://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
    if not os.path.exists("static/vids/"):
        os.makedirs("static/vids/")
    for x in vidArray:
        #url = "https://www.youtube.com/watch?v=" + x
        video = pafy.new(x)
        ##owen's shit
        
        best = video.getbest(preftype="mp4")
        bests.append(best)
    for i in range(0, len(bests)):
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
    shutil.rmtree('static/vids')



if __name__ == '__main__':
   app.run(debug = True)

