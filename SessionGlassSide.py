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
#re1 = '(\\d+)' 
#param1 = re.compile("RTCInboundRTPAudioStream_"+re1+"_inbound-rtp_packetsReceived",re.IGNORECASE|re.DOTALL)
#param2 = re.compile("RTCInboundRTPAudioStream_"+re1+"_inbound-rtp_jitter",re.IGNORECASE|re.DOTALL)
#param3 = re.compile("RTCInboundRTPAudioStream_"+re1+"_inbound-rtp_bytesReceived",re.IGNORECASE|re.DOTALL)
#param4 = re.compile("RTCOutboundRTPAudioStream_"+re1+"_outbound-rtp_packetsSent",re.IGNORECASE|re.DOTALL)
#param5 = re.compile("RTCOutboundRTPAudioStream_"+re1+"_outbound-rtp_bytesSent",re.IGNORECASE|re.DOTALL)

'''def plot(df):
	df.set_index("createdDT")
	plt.ion()
	fig, ax = plt.subplots()
	while True:
	    dframe = df.copy()
	    dframe['createdDT'] = pd.to_datetime(dframe['createdDT']) + pd.DateOffset(minutes = 20)
	    dframe = dframe.set_index('createdDT')
	    end = dframe.index.max()
	    start= end.to_datetime() - dt.timedelta(minutes=20)
	    dframe = dframe.loc[start:end]
	    ax.plot_date(dframe.index.to_pydatetime(), dframe, marker='', linestyle='solid')
	    plt.pause(0.01)
	    '''

sessionKey = input("Enter the session Key\n")
filepath = str(sessionKey) + '/'
if not os.path.exists(os.path.dirname(filepath)):
    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


connection = pymysql.connect(host='virgoinnovation.com',
                         user='dbuser',
                         password='Dbuser123',                             
                         db='vega1',
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
	#df = pd.read_csv(filename+'.csv', delimiter=",", usecols = ["sessUserId","sessKey","name", "statsFor","isHost","isGlassUser","createdDT","ptVideo","ptAudio","ptWhiteboard","ptLiveStream","ptLocal"])
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

'''def subplot(df, columns, name,nomen, length):
	j=0
	fig = tools.make_subplots(rows=length, cols=1, subplot_titles= columns)
	for i in columns:
		trace1 = go.Scatter(x=df['createdDT'], y=df[i], name = i)
		fig.append_trace(trace1, j+1, 1)
		j = j + 1

	fig['layout'].update(height=1000, width=600, title=str(userId)+' '+nomen)
	plotly.offline.plot(fig, filename= str(userId)+nomen+'.html',auto_open=True)
	fichier_html_graphs.write("<object data=\""+str(userId)+nomen+'.html'+"\" width=\"650\" height=\"650\"></object>"+"\n")	
'''
def combine (df1, df2):
	result = df2.join(df1, lsuffix='_df2', rsuffix='_df1')
	return result

	
key = df.sessKey.unique()
userId = df.sessUserId.unique()
pt = df.name.unique()

fichier_html_graphs=open(filepath+'/'+'GlassSide.html','w')
fichier_html_graphs.write("<html><head></head><body>"+"\n")

def processStats(pt):
	df_filter = df[(df.name == pt) & (df.statsFor == 'GLASS_SIDE_WEBRTC')]
	good_columns =[
	"sendData",
	"recieveData",
	"RTCInboundRTPAudioStream_inbound-rtp_packetsLost",
	"RTCInboundRTPVideoStream_inbound-rtp_bytesReceived",
	"RTCInboundRTPVideoStream_inbound-rtp_packetsLost",
	"RTCMediaStreamTrack_track_audioLevel",
	"RTCInboundRTPVideoStream_inbound-rtp_pliCount",
	"RTCOutboundRTPVideoStream_outbound-rtp_packetsSent",
	"RTCOutboundRTPVideoStream_outbound-rtp_bytesSent",
	"RTCMediaStreamTrack_track_framesDropped",
	"RTCOutboundRTPVideoStream_outbound-rtp_pliCount"
	]
	#data_cand = defaultdict(list)
	#data_inbound = defaultdict(list)
	#data_track = defaultdict(list)
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
				'''if k in good_columns_cand_pair:
					data_cand[k].append(v)
				if k in good_columns_inbound:
					data_inbound[k].append(v)
				if k in good_columns_track:
					data_track[k].append(v)'''
						
		#print(data_cand)
		#df1 = pd.DataFrame.from_dict(data)
		df1= pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))

		'''df_cand = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data_cand.items()]))
		df_cand.fillna(0)
		#for x in df_cand.columns:
		#	df_cand[x] = df_cand[x].apply(pd.to_numeric)
		#df_cand['candidate-pair_bytesSent'] = df_cand['candidate-pair_bytesSent']/1000
		#df_cand['candidate-pair_bytesReceived'] = df_cand['candidate-pair_bytesReceived']/1000
		df_inbound = pd.DataFrame.from_dict(data_inbound)
		df_track = pd.DataFrame.from_dict(data_track)'''
		l2 = len(df_filter_li)
		df2 = pd.DataFrame(df_filter_li['createdDT'])
		df2.index = range(l2)
		#result = df1.join(df2, lsuffix='_df1', rsuffix='_df2')
		norm = combine(df1, df2)
		#candidate = combine(df_cand,df2)
		#inbound = combine(df_inbound, df2)
		#track = combine(df_track, df2)
		#print(inbound)
		#print(candidate)
		#plot(norm)
		plot(norm, df1.columns,pt+'LiveStream')
		#plot(candidate, df_cand.columns, pt+'LiveStream'+'_CandPair')
		#plot(inbound, df_inbound.columns, pt+'LiveStream'+'_inbound')
		#plot(track, df_track.columns, pt+'LiveStream'+'_track')


if __name__ == '__main__':
	show_info(df)
	for i in pt:
		print("Creating plot for userID ",  i)
		processStats(i)