#!/usr/bin/env python3
import pandas as pd
import json
import datetime as dt
import pymysql.cursors  
import re
import os
import errno
import plotly
import plotly.graph_objs as go
from plotly import tools
from collections import defaultdict
import datetime as dt
import re
print(pymysql.__version__)
print(pd.__version__)
print(plotly.__version__)

sessionKey = input("Enter the session Key\n")
filepath = str(sessionKey) + '/'
if not os.path.exists(os.path.dirname(filepath)):
    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

# database connection 
connection = pymysql.connect(host='********',
                         user='******',
                         password='*****',                             
                         db='*****',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
print ("connect successful!!")
try:
	with connection.cursor() as cursor:
		query = "Select * from vega1.tblSessWebRtc where sessKey = %s"
		sesskey = sessionKey
		df = pd.read_sql(query,connection, params = [sesskey])
finally:
    # Close connection.
    connection.close()
print('connection closed')  

def show_info(df):
	print("Info for the Session:-")
	print("Session key:-")
	print(df.sessKey.unique())
	print("Name of participants:-")
	print(df.name.unique())
	print("Session user Id:-")
	print(df.sessUserId.unique())


def plot(df, columns, name):
	graph = []
	for x in columns:
		trace = go.Scatter(
			x = df['createdDT'],
			y = df[x],
			name = x)
		graph.append(trace)
	layout = dict(
	    xaxis = dict(title = 'Timestamp'),
	    yaxis = dict(title = 'Values'),
	    title = name
	    )
	fig1 = go.Figure( data=graph, layout=layout)
	plotly.offline.plot(fig1, filename=filepath+'/'+name+'.html',auto_open=False)
	fichier_html_graphs.write("<object data=\""+name+'.html'+"\" width=\"850\" height=\"500\"></object>"+"\n")
	
key = df.sessKey.unique()
userId = df.sessUserId.unique()
pt = df.name.unique()

fichier_html_graphs=open(filepath+'/'+'GlassSide.html','w')
fichier_html_graphs.write("<html><head></head><body>"+"\n")

def processStats(pt):
	df_filter = df[(df.name == pt) & (df.statsFor == 'GLASS_SIDE_WEBRTC')]
	good_columns =[
	"glassAudioLevel",
	"sendData",
	"recieveData",
	"RTCInboundRTPAudioStream_inbound-rtp_bytesReceived",
	"RTCOutboundRTPAudioStream_outbound-rtp_bytesSent",
	"RTCInboundRTPVideoStream_inbound-rtp_bytesReceived",
	"RTCOutboundRTPVideoStream_outbound-rtp_bytesSent",
	"RTCMediaStreamTrack_track_audioLevel",
	"RTCInboundRTPVideoStream_inbound-rtp_pliCount",
	"RTCMediaStreamTrack_track_framesDropped",
	"RTCOutboundRTPVideoStream_outbound-rtp_pliCount"
	]
	data = defaultdict(list)
	if(df_filter['ptLiveStream'].isnull().all()):
		print("No LiveStream record\n")
	else:
		print("LiveStream record is available\n")
		df_filter_li = df_filter[pd.notnull(df_filter['ptLiveStream'])]
		df_filter_li = df_filter_li[['createdDT','ptLiveStream']]
		record = df_filter_li['ptLiveStream'].apply(json.loads)
		for key, value in record.items():
			new = json.loads(value)
			for k,v in new.items():
				if k in good_columns:
					data[k].append(v)
		df1= pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))

		l2 = len(df_filter_li)
		df2 = pd.DataFrame(df_filter_li['createdDT'])
		df2.index = range(l2)
		norm = combine(df1, df2)
		plot(norm, df1.columns,pt+'LiveStream')

if __name__ == '__main__':
	show_info(df)
	for i in pt:
		print("Creating plot for userID ",  i)
		processStats(i)
