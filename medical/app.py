from flask import Flask, request
from flask_cors import CORS
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import json as js
app = Flask("scheduling for agent", static_url_path='', static_folder='static/')
CORS(app)

df4 = None
def clustering(x,y):
    global df4

    df=pd.read_csv("https://raw.githubusercontent.com//asaikiran1999/diagnostic-center-agents-sheduling/main/final_data.csv")
    df1 = df.drop(df.columns[[0,2,3,6,7,9,10,12,22,23,24,25]], axis = 1)
    df2=df1

    df3=df1[df1['Sample Collection Date']==x]
    df4=df3.copy()



    le = LabelEncoder()

    df3['patient location'] = le.fit_transform(df3['patient location'])
    df3['Diagnostic Centers'] = le.fit_transform(df3['Diagnostic Centers'])
    df3['Availabilty time (Patient)'] = le.fit_transform(df3['Availabilty time (Patient)'])
    X =df3[['patient location','Diagnostic Centers','shortest distance Patient-Pathlab(m)','Availabilty time (Patient)']]


    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(X)
    X=pd.DataFrame(scaled)
    X.columns=['patient location','Diagnostic Centers','shortest distance Patient-Pathlab(m)','Availabilty time (Patient)']
    

    kmeans = KMeans(n_clusters=y,random_state=1234)

    kmeans.fit(X)

    labels = kmeans.labels_
    df3["Agent id "]=labels
    df4["Agent id "]=labels
    
    
@app.route("/", methods=['GET'])
def index():
    return app.send_static_file('app.html')

@app.route("/app2", methods=['GET'])
def app2():
    return app.send_static_file('app2.html')


@app.route("/generate_clusters", methods=['POST'])
def generate_clusters():
    data = request.get_json()
    schedule_date = data['date']
    no_of_agents = int(data['no_of_agents'])
    clustering(schedule_date,no_of_agents)
    return {'success':True}


@app.route("/show_agent_shedule", methods=['POST'])
def show_agent_shedule():
    data = request.get_json()
    z = int(data['agent_id'])
    df5 = df4[df4['Agent id ']==z]
    df5.index = range(df5.shape[0])

    t = df5.shape[0]
    df5['avail']=0
    for i in range(t):
      df5["avail"][i]=int(df5['Availabilty time (Patient)'][i].split('to')[0].strip().split(':')[0])        
    df6 = df5.sort_values(['avail', 'shortest distance Patient-Pathlab(m)'],ascending=[1,1])
    df7 = df6.drop(['avail','Test Booking Time HH:MM','Test Booking Date'], axis = 1)
    first_column = df7.pop('Availabilty time (Patient)')
    df7.insert(0, 'Availabilty time (Patient)', first_column)
    df7 = df7.drop(['shortest distance Patient-Pathlab(m)'],axis=1)
    df7 = df7.drop(['Sample Collection Date'  ],axis=1)
    df7 = df7.drop(df7.columns[[10]], axis = 1)
    df7 = js.dumps(df7.to_numpy().tolist())
    return {'success':True,'data':df7}




if __name__ == '__main__':
    # debug = False
    debug = True
    port = 5000
    #clustering('2022-01-03 00:00:00' , 5)
    #print(df4.head())
    #show_agent_shedule()
    app.run(debug=debug, port=port)
    