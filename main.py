# project: p4
# submitter: kgschears@wisc.edu
# partner: none
# hours: 5
# Data: https://www.kaggle.com/datasets/equinxx/spotify-top-50-songs-in-2021
import pandas as pd
from flask import Flask, request, jsonify, Response
import re
import time 
import matplotlib
# !!!!!!!
matplotlib.use('Agg') #very important for using matplotlib in the backend
#!!!!!!!

import matplotlib.pyplot as plt
from io import StringIO
# !!!!!!!
matplotlib.use('Agg') #very important for using matplotlib in the backend
#!!!!!!!

users={}
User_Count=0
Version_A=True
clicked_A=0
clicked_B=0
Version_B=None 
data= pd.read_csv("main.csv")
app = Flask(__name__)
# df = pd.read_csv("main.csv")

@app.route('/')
def home():
    global User_Count
    global Version_A
    global clicked_A
    global clicked_B
    global Version_B
    User_Count+=1
    if Version_A and User_Count < 10 or User_Count > 10 and clicked_A > clicked_B:
        with open("index.html") as f:
            html = f.read()
    else:
        if not Version_B: 
            new_html=""
            with open("index.html","r") as f:
                f.seek(0)
                old_html=f.readlines()
                new_html+="".join(old_html[:2])
                new_html+="\n <style> \n #donate {text-decoration:none;} \n a {border: solid red 2px;} \n </style>\n"
                new_html+="".join(old_html[2:])
                Version_B = new_html
        html=Version_B
    Version_A= not Version_A #toggle boolean to switch to Version_B
    return Response(html,status=200)

# @app.route('/')
# def home():
#     global User_Count
#     global Version_A
#     global clicked_A
#     global clicked_B
#     User_Count+=1
#     if Version_A and User_Count < 10 or User_Count > 10 and clicked_A > clicked_B:
#         with open("index_Version_A.html") as f:
#             html = f.read()
#     else:
#         with open("index_Version_B.html") as f:
#             html = f.read()
#     Version_A= not Version_A #toggle boolean to switch to Version_B
#     return html

@app.route('/browse.html')
def browse():
    global data
    html="<h1>Spotify Top 50 2021 Dataset</h1>"
    html+=data.to_html()
    return Response(html,status=200)

@app.route('/browse.json')
def browse_json():
    global users
    global data
    # request.remote_addr a flask client variable that holds the clients IP address
    found= False 
    if users.get(request.remote_addr):
        found=True 
    if  not found or found and time.time()-users[request.remote_addr] > 60 :
        
        data_dict=data.to_dict("index")
        users[request.remote_addr]=time.time()
        return jsonify(data_dict)
    else:
        return Response(f"<h1>Retry-After: {60-(time.time()-users[request.remote_addr])} seconds<h1>",status=429, headers={"Retry-After": 60-(time.time()-users[request.remote_addr])})


@app.route('/donate.html')
def donate():
    global User_Count
    if User_Count < 10:
        global Version_A
        global clicked_A
        global clicked_B
        if not Version_A: # not Version_A means it is Version_A because boolean toggle at end of home() function!
            clicked_A+=1
        else:
            clicked_B+=1
    with open("donate.html") as f:
        html=f.read()
    return Response(html,status=200)

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"^[a-zA-Z0-9]?[a-zA-Z0-9]*@{1}[a-zA-Z0-9]*\.com$", email): # 1
        with open("emails.txt", "a+") as f: # open file in append mode
            f.write(email + "\n") # 2
            f.seek(0)
            num_subscribed= len(f.readlines())
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("Enter vaild email or Will Smith will slap you in your sleep!") # 3

@app.route('/dashboard_1.svg', methods=["GET"])
def scatter_plot():
    fig, ax = plt.subplots(figsize=(5,5))
    global data 
    args = request.args
    x_axis = args.get("x_axis")
    y_axis = args.get("y_axis")
    if x_axis and y_axis:
        x_ax=x_axis
        y_ax=y_axis
    else: 
        # dancability vs acousticness  scatter plot 
        x_ax="tempo"
        y_ax="acousticness"
       
    ax.scatter(x=data[x_ax], y=data[y_ax]) # same as data.plot.scatter(ax=ax, x=x_ax,y=y_ax)
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title(f"{x_ax} vs {y_ax} Top 50 song 2021")
    f = StringIO()
    fig.savefig(f, format="svg")
    plt.close() # closes the most recent fig

    svg = f.getvalue()

    hdr = {"Content-Type": "image/svg+xml"}
    return Response(svg, headers=hdr)
        
        
@app.route('/dashboard_2.svg')
def hist_plot(): 
    global data 
    # histogram of artists and the number of count in the top 50 song list 
    fig, ax = plt.subplots(figsize=(7,7))
    data["artist_name"].hist(ax=ax, bins=35)
    plt.xticks(rotation = 90)
    ax.margins(x=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)
    ax.set_xlabel("Artist name")
    #----Need this block for every svg graph------
    f = StringIO()
    fig.savefig(f, format="svg", bbox_inches='tight',pad_inches = 0)
    plt.close() # closes the most recent fig
    svg = f.getvalue()
    hdr = {"Content-Type": "image/svg+xml"}
    #--------------------------------------------
    return Response(svg, headers=hdr)
        
    






if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
