from flask import Flask, url_for, request, render_template
import httplib2
import os
import re
import sys


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
	return render_template("result.html",videos=videos)



if __name__ == '__main__':
   app.run(debug = True)

