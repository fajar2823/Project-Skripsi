# from flask import Flask, render_template, request #redirect, url_for
# import joblib
# import numpy as np
# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import random
# import folium
#
# app = Flask(__name__)
# warung = pd.read_csv('dataset/warung.csv')
# rf_clf = joblib.load('model_warung')
# #@app.route('/')
# @app.route('/main', methods = ['POST'])
# def main():
#     warung = pd.read_csv('dataset/warung.csv')
#     #if request.method == 'POST':
#     halal= int(request.form['halal'])
#     area_merokok= int(request.form['area merokok'])
#     harga= int(request.form['harga'])
#     tempat_parkir = int(request.form['tempat parkir'])
#     arr = np.array([[halal, area_merokok, harga, tempat_parkir]])
#     return render_template('main.html', data = arr)
#
# if __name__ == '__main__':
#
#    app.run(debug = True)
from flask import Flask, render_template, request
import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import folium

app = Flask(__name__)

warung = pd.read_csv('dataset/warung.csv')
rf_clf = joblib.load('model_warung')
@app.route('/')
def man():
    return render_template('main.html')


@app.route('/rekomendasi', methods=['POST'])
def home():
    data1 = request.form['halal']
    data2 = request.form['area merokok']
    data3 = request.form['harga']
    data4 = request.form['tempat parkir']

    if data1 == 0:
      data1_1 = 0; data1_2 = 1
    else :
      data1_1 = 1; data1_2 = 0

    if data2 == 0:
      data2_1 = 0; data2_2 = 1
    else:
      data2_1 = 0; data2_2 = 1

    if data3 == 0 :
      data3_1 =1; data3_2 = 0; data3_3 =0
    elif data3 ==1:
      data3_1 = 0; data3_2 = 1; data3_3 = 0
    else:
      data3_1 = 0; data3_2 = 0; data3_3 = 1

    if data4 == 0:
      data4_1 = 1; data4_2 = 0
    else:
      data4_1 =0; data4_2 =1
    arr = [data1_1, data1_2, data2_1, data2_2,  data3_1, data3_2, data3_3, data4_1,data4_2]
    prediksi = rf_clf.predict([arr])[0]

    model = CountVectorizer(
      tokenizer=lambda i: i.split(' '),  # -> cari split karakter yang unik
      analyzer='word'
    )
    matrix_kriteria = model.fit_transform(warung['kriteria'])
    score = cosine_similarity(matrix_kriteria)
    warung_fav = prediksi
    index_fav = warung[warung['Nama_warung'] == warung_fav].index.values[0]
    all_warung = list(enumerate(score[index_fav]))
    warung_similar = sorted(all_warung, key=lambda i: i[1], reverse=True)
    warung_recom = []
    for i in warung_similar:
      if i[1] > 0.8:
        warung_recom.append(i)
      else:
        pass
    rekomendasi = random.choices(warung_recom, k=5)

    list_rekom = []
    for i in rekomendasi:
      ambil_rekom = {}
      ambil_rekom['Nama_warung'] = warung.iloc[i[0]]['Nama_warung'],
      ambil_rekom['Halal'] = warung.iloc[i[0]]['Halal'],
      ambil_rekom['Area_merokok'] = warung.iloc[i[0]]['Area_merokok'],
      ambil_rekom['Harga'] = warung.iloc[i[0]]['Harga'],
      ambil_rekom['Tempat_parkir'] = warung.iloc[i[0]]['Tempat_parkir'],
      ambil_rekom['Latitude'] = warung.iloc[i[0]]['Latitude'],
      ambil_rekom['Longitude'] = warung.iloc[i[0]]['Longitude']

      list_rekom.append(ambil_rekom)

      # creat map

      # map = folium.Map(location=[list_rekom[0]['Latitude'], list_rekom[0]['Longitude']], zoom_start=14)
      # tooltip = 'Klik untuk informasi lebih lanjut'

      # creat marker
      # folium.Marker(
      #   [list_rekom[0]['Latitude'], list_rekom[0]['Longitude']],
      #   popup=list_rekom[0]['Nama_warung'][0],
      #   tooltip=tooltip
      # ).add_to(map)
      #
      # folium.Marker(
      #   [list_rekom[1]['Latitude'], list_rekom[1]['Longitude']],
      #   popup=list_rekom[1]['Nama_warung'][0],
      #   tooltip=tooltip
      # ).add_to(map)
      #
      # folium.Marker(
      #   [list_rekom[2]['Latitude'], list_rekom[2]['Longitude']],
      #   popup=list_rekom[2]['Nama_warung'][0],
      #   tooltip=tooltip
      # ).add_to(map)
      #
      # folium.Marker(
      #   [list_rekom[3]['Latitude'], list_rekom[3]['Longitude']],
      #   popup=list_rekom[3]['Nama_warung'][0],
      #   tooltip=tooltip
      # ).add_to(map)
      #
      # folium.Marker(
      #   [list_rekom[4]['Latitude'], list_rekom[4]['Longitude']],
      #   popup=list_rekom[4]['Nama_warung'][0],
      #   tooltip=tooltip
      # ).add_to(map)
      #
      # # generate map
      # map.save('templates/map.html')


    return render_template('nyoba.html', data=arr,rekom = list_rekom)

@app.route('/map')
def show_map():
    return render_template('map.html')
if __name__ == "__main__":
    app.run(debug=True)
