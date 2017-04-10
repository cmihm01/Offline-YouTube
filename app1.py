from flask import Flask, render_template, request, redirect, url_for
import pafy, zipfile, os, math
app = Flask(__name__)

count = 0
urls = ['https://www.youtube.com/watch?v=ferZnZ0_rSM', 'https://www.youtube.com/watch?v=fnIu25lXXY8', 'https://www.youtube.com/watch?v=88_jAJ-MduU']

@app.route('/')
def download():
    return download_vids(urls)

def download_vids(vidArray):
    max_viewcount = 0
    scored_vids = []
# https://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
    if not os.path.exists("static/vids/"):
        os.makedirs("static/vids/")
    for x in vidArray:
        url = x
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
    zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('tmp/', zipf)
    zipf.close()