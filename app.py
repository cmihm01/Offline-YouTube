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
   if request.method == 'POST':
      result = request.form
      
      return youtube_search(request.form['category'],request.form['difficulty'], request.form['age'],request.form['keywords'],request.form['num-vids'] )
      #return render_template("result.html",result = result)

def youtube_search(cat,diff,age,keyw,num):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=cat + keyw,
        part="id,snippet",
        maxResults=num
      ).execute()
    search_videos = []

    for search_result in search_response.get("items", []):
        search_videos.append(search_result["id"]["videoId"])
    video_ids = ",".join(search_videos)

    video_response = youtube.videos().list(
        id=video_ids,
        part='snippet, recordingDetails'
    ).execute()

    descriptions = []

    # Add each result to the list, and then display the list of matching videos.
    for video_result in video_response.get("items", []):
        descriptions.append((video_result["snippet"]["description"]))
        print "Videos:\n", "\n".join(descriptions), "\n"

    count = 0
    for vid in search_response.get("items", []):
        vid["snippet"]["description"] = descriptions[count]
        count+=1

    scored_results = score_and_sort(search_response, keyw)


    # return download_vids(scored_results) 
    return render_template("select.html", videos=scored_results,descriptions=descriptions)


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
            if keyw in (search_result["snippet"]["description"]):
               score = score + 1
            scored_vids.append(tuple((score, search_result)))
    scored_vids.sort(key = lambda tup: tup[0], reverse=True)

    for i in range(0, len(scored_vids)):
        scored_results.append(scored_vids[i][1])

    # I need to give a list of videos to the download vids function 
    return scored_results
    #return download_vids(videos) 
    # need to be URLS

@app.route("/download",methods=['GET','POST'])
def download_vids():
    vidArray = []
    if request.method == 'POST':
        for vid in request.form.getlist("video"):
            vidArray.append(vid)
    max_viewcount = 0
    scored_vids = []
    if os.path.exists("content/"):
        shutil.rmtree('content/')
    os.makedirs("content/.vids/")
    target = open('content/VidPlayer.html', 'a')
    target.write("<!DOCTYPE html>\n<html>\n<body>\n\n")


    for x in vidArray:
        #url = "https://www.youtube.com/watch?v=" + x
        video = pafy.new(x)
        ##owen's shit
        score = 0
        if (video.viewcount > max_viewcount):
            max_viewcount = video.viewcount
        score = score + (math.sqrt(video.rating)) + (video.viewcount / max_viewcount) ##+ count
        scored_vids.append(tuple((score, video)))
    scored_vids.sort(key = lambda tup: tup[0], reverse=True)

    for vid in scored_vids:
        target.write('<h2>' + vid[1].title + '</h2>')
        target.write('<video width="70%" controls>\n<source src=".vids/' + vid[1].title + '.mp4" type="video/mp4">\nYour browser does not support HTML5 video.\n</video>\n\n')
        best = vid[1].getbest(preftype="mp4")
        filename = best.download("content/.vids/" + vid[1].title + ".mp4")
    target.write("</body>\n</html>")
    target.close()
       
    return redirect(url_for('done'))

@app.route('/done')
def done():
    zipdir('content/')
    return render_template('done.html')

# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory/
def zipdir(path):
    zf = zipfile.ZipFile("static/content.zip", "w")
    for root, dirs, files in os.walk(path):
        for file in files:
            zf.write(os.path.join(root, file))
    if os.path.exists("content/"):
        shutil.rmtree('content/')


if __name__ == '__main__':
   app.run(debug = True)

