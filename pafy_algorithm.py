#Video-Ranking Algorithm
#Owen Martin
#Offline Youtube Project


#Steps:
#1. Create a dictionary of x videos using the links provided by Claudia
#	a. video1 = pafy.new(video_link)
#	b. video_dict.append(video1)
#2. Sort within the dictionary by various attributes
#	a. within this, how do we determine whether the video has been downloaded?
#
import math
import pafy
import numpy as np

vids = []
scored_vids = []
urls = ['https://www.youtube.com/watch?v=ferZnZ0_rSM', 'https://www.youtube.com/watch?v=fnIu25lXXY8', 'https://www.youtube.com/watch?v=88_jAJ-MduU']
max_viewcount = 0

for vid in urls:
	score = 0
	pafy_video = pafy.new(vid, gdata=True)
	vids.append(pafy_video)
	if (pafy_video.viewcount > max_viewcount):
		max_viewcount = pafy_video.viewcount
	score = score + (math.sqrt(pafy_video.rating)) + (pafy_video.viewcount / max_viewcount) ##+ count
	scored_vids.append(tuple((score, vid)))

#X = np.array(vids)
#print X[0]
scored_vids.sort(key = lambda tup: tup[0], reverse=True)
vids.sort(key=lambda x: x.rating, reverse=True)

for i in range(0,len(scores)):
	print scores[i][0]

