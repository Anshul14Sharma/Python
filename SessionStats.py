import pandas as pd
import re
import pymysql.cursors  
import json
import datetime as dt
import plotly
import os
import errno
import plotly.plotly as py
import plotly.graph_objs as go
from collections import defaultdict
import itertools
print(pymysql.__version__)
print(pd.__version__)
print(plotly.__version__)
re1='(\\d+)'
rg_recv = re.compile('ssrc_'+re1+'_recv',re.IGNORECASE|re.DOTALL)
rg_send = re.compile('ssrc_'+re1+'_send',re.IGNORECASE|re.DOTALL)
key = []
#sessionKey = input("Enter the session Key\n")
good_columns=[
	"inboundrtp_bytesReceived",
	"outboundrtp_bytesSent",
	#"outboundrtp_packetsLost",
	#"googAvailableReceiveBandwidth",
	"googRtt",
	"audioInputLevel",
	#"packetsSent",
	"bytesSent",
	"bytesReceived",
	"audioOutputLevel",
	#"packetsReceived",
	"googJitterBufferMs"
	]

with open("sessionkey.txt", 'r+') as f:
	for line in f:
		key.append(line.split())
merged = list(itertools.chain(*key))			

def complete(pt,ptType, df_filter_1, df_filter_2):
	final_df_1 = df_filter_1[pd.notnull(df_filter_1[ptType])]
	final_df_1 = final_df_1[['createdDT',ptType]]
	final_df_2 = df_filter_2[pd.notnull(df_filter_2[ptType])]
	final_df_2 = final_df_2[['createdDT',ptType]]

	data_v = defaultdict(list)
	ssrc_send = defaultdict(list)
	ssrc_recv = defaultdict(list)
	bwe = defaultdict(list)
	record_1 = final_df_1[ptType].apply(json.loads)
	#print(record.count() )
	for key, value in record_1.items():
		for k,v in value.items():
			if k in good_columns:
				#print(k)
				data_v[k].append(v)	
	record_2 = final_df_2[ptType].apply(json.loads)
	#print(record.count() )
	for key, value in record_2.items():			
		for k,v in value.items():
			if k == 'bweforvideo':
				for k1, v1 in v.items():
					if k1 in good_columns:
						bwe[k1].append(v1)
			if rg_recv.match(k):
				for k1 ,v1 in v.items():
					if k1 in good_columns:
						ssrc_recv[k1].append(v1)	
			if rg_send.match(k):
				for k1, v1 in v.items():
					if k1 in good_columns:
						ssrc_send[k1].append(v1)
	df_in_out = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data_v.items() ]))
	df_send = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in ssrc_send.items() ]))
	df_recv = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in ssrc_recv.items() ]))	
	df_bwe = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in bwe.items() ]))
	send_recv = df_recv.join(df_send, lsuffix='_df_recv', rsuffix='_df_send')
	stats = send_recv.join(df_in_out,lsuffix='_send_recv', rsuffix='_df_in_out')
	l1 = len(final_df_2)
	df_date_s = pd.DataFrame(final_df_2['createdDT'])
	df_date_s.index = range(l1)
	result = pd.DataFrame(df_date_s.join(stats, lsuffix='_df_date_s', rsuffix='_stats'))
	result.fillna(0)
	if result.empty:
		print("Required params not available")
	else:	
		if(ptType == 'ptVideo'):
			stats = df_bwe.join(df_recv,lsuffix='_df_bwe', rsuffix='df_recv')
			result = df_date_s.join(stats, lsuffix='_df_date_s', rsuffix = '_stats')
			plot(result,stats.columns, pt+ptType)
		else:	
			plot(result,stats.columns, pt+ptType)	

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
	fichier_html_graphs.write("<object data=\""+name+'.html'+"\" width=\"550\" height=\"500\"></object>"+"\n")

def processStats(pt):
	df_filter_1 = df[(df.name == pt) & (df.statsFor == 'SCHEDULED') ]
	df_filter_2 = df[(df.name == pt) & (df.statsFor == 'CLIENT_SIDE_WEBRTC')]
	
	#filter for SCHEDULED	
	if(df_filter_2['ptVideo'].isnull().all()):
		print("No Video record\n")
	else:
		print("Video record is available\n")
		complete(pt,'ptVideo',df_filter_1, df_filter_2)

	if(df_filter_2['ptAudio'].isnull().all()):
		print("No Audio record \n")
	else:
		print("Audio record is available\n")
		complete(pt,'ptAudio',df_filter_1, df_filter_2)
		
	if(df_filter_2['ptWhiteboard'].isnull().all()):
		print("No Whiteboard record \n")
	else:
		print("Whiteboard record is available\n")
		complete(pt,'ptWhiteboard',df_filter_1, df_filter_2)

	if(df_filter_2['ptLiveStream'].isnull().all()):
		print("No LiveStream record\n")
	else:
		print("LiveStream record is available\n")
		complete(pt,'ptLiveStream',df_filter_1, df_filter_2)
		
	if(df_filter_2['ptLocal'].isnull().all()):
		print("No Local record \n")
	else:
		print("Local record is available\n")
		complete(pt,'ptLocal',df_filter_1, df_filter_2)

connection = pymysql.connect(host='***************',
                         user='**********',
                         password='*******',                             
                         db='**********',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
print ("connect successful!!")
try:
	with connection.cursor() as cursor:
		query = "Select * from vega1.tblSessWebRtc where sessKey = %s"
		for i in merged:
			filepath = str(i) + '/'
			if not os.path.exists(os.path.dirname(filepath)):
			    try:
			        os.makedirs(os.path.dirname(filepath))
			    except OSError as exc: # Guard against race condition
			        if exc.errno != errno.EEXIST:
			            raise
			sesskey = i
			print(sesskey)
			df = pd.read_sql(query,connection, params = [sesskey])
			show_info(df)
			key = df.sessKey.unique()
			userId = df.sessUserId.unique()
			pt = df.name.unique()
			fichier_html_graphs=open(filepath+'/'+'Session'+i+'.html','w')
			fichier_html_graphs.write("<html><head></head><body>"+"\n")
			for i in pt:
				print('Creating plot for' + i )
				processStats(i)
finally:
    # Close connection.
    connection.close()
print('connection closed')  