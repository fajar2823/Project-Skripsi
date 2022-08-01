from flask import Flask, render_template, request #redirect, url_for
import joblib
#import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import folium

app = Flask(__name__)
warung = pd.read_csv('dataset/warung.csv')
rf_clf = joblib.load('model_warung')
@app.route('/')
def home():
    return render_template('main.html')
@app.route('/rekomendasi', methods = ["GET",'POST'])
def main():
    global harga_str, area_merokok_str, halal_str, tempat_parkir_str, halal_halal, halal_non_halal, area_merokok_Ada, area_merokok_Tidak, harga_Mahal, harga_Menengah, harga_Murah, tempat_parkir_off_street_parking, tempat_parkir_on_street_parking
    if request.method == 'POST':
      halal= int(request.form['halal'])
      area_merokok= int(request.form['area merokok'])
      harga= int(request.form['harga'])
      tempat_parkir = int(request.form['tempat parkir'])

      #1) option untuk halal
      if halal == 0:
          halal_halal = 0; halal_non_halal = 1
          halal_str = 'non_halal'
      elif halal == 1:
           halal_halal = 0; halal_non_halal = 1
           halal_str = 'halal'
      #2)option area meokok

      if area_merokok == 0:
        area_merokok_Ada = 0; area_merokok_Tidak = 1
        area_merokok_str = 'Tidak'

      elif area_merokok == 1:
        area_merokok_Ada = 1; area_merokok_Tidak = 0
        area_merokok_str = 'Ada'

      #3) Harga
      if harga == 0:
          harga_Mahal = 1; harga_Menengah = 0; harga_Murah = 0
          harga_str = 'Mahal'
      elif harga == 1:
          harga_Mahal = 0; harga_Menengah = 1; harga_Murah = 0
          harga_str = 'Menengah'
      elif harga == 2:
          harga_Mahal = 0; harga_Menengah = 0; harga_Murah = 1
          harga_str = 'Murah'

      #4)Tempat parkir
      if tempat_parkir == 0:
        tempat_parkir_off_street_parking = 1; 	tempat_parkir_on_street_parking = 0
        tempat_parkir_str = 'off_street_parking'
      elif tempat_parkir == 1:
        tempat_parkir_off_street_parking = 0; 	tempat_parkir_on_street_parking = 1
        tempat_parkir_str = 'on_street_parking'

      text = [halal_str, area_merokok_str, harga_str, tempat_parkir_str]

      #machine learning rf_clf & prediction
      fitur = [
        halal_halal, halal_non_halal,
        area_merokok_Ada, area_merokok_Tidak,
        harga_Mahal, harga_Menengah, harga_Murah,
        tempat_parkir_off_street_parking, tempat_parkir_on_street_parking
      ]

      prediksi = rf_clf.predict([fitur])[0]

      #set up recommender
      # warung['kriteria'] = warung['Halal'].str.cat(
      #   warung[['Area_merokok', 'Harga', 'Tempat_parkir']],
      #   sep=' '
      # )

      # count criterias
      model = CountVectorizer(
      tokenizer = lambda i: i.split(' '), # -> cari split karakter yang unik
      analyzer = 'word'
      )
      matrix_kriteria = model.fit_transform(warung['kriteria'])
      # tipe_kriteria = model.get_feature_names()
      # jumlah_criteria = len(tipe_kriteria)

      #cosine similarity
      score  = cosine_similarity(matrix_kriteria)

      #test model
      warung_fav = prediksi

      #take index from warung_fav
      index_fav = warung[warung['Nama_warung'] == warung_fav].index.value[0]

      #list all warung + cosine similarity score
      all_warung = list(enumerate(score[index_fav]))

      #show similar warung, sorted by score
      warung_similar = sorted(all_warung, key =lambda i: i[1],reverse= True)

      #list all resto filter by cosine similarity score > 80%

      warung_recom = []
      for i in warung_similar:
        if i[1] > 0.8:
          warung_recom.append(i)
        else:
          pass
      #show 5 data random
      rekomendasi = random.choices(warung_recom, k = 5)

      list_rekom = []
      for i in rekomendasi:
        ambil_rekom = {}
        j = 0
        while j < 8:
          ambil_rekom['Nama_warung'] = warung.iloc[i[0]]['Nama_warung'].title(),
          ambil_rekom['Halal'] = warung.iloc[i[0]]['Halal'],
          ambil_rekom['Area_merokok'] = warung.iloc[i[0]]['Area_merokok'],
          ambil_rekom['Harga'] = warung.iloc[i[0]]['Harga'],
          ambil_rekom['Tempat_parkir'] = warung.iloc[i[0]]['Tempat_parkir'],
          ambil_rekom['Latitude'] = warung.iloc[i[0]]['Latitude'],
          ambil_rekom['Longitude'] = warung.iloc[i[0]]['Longitude']
          j += 1


        list_rekom.append(ambil_rekom)

        #creat map

        map = folium.Map(location =[list_rekom[0]['Latitude'],list_rekom[0]['Longitude']], zoom_start = 14)
        tooltip = 'Klik untuk informasi lebih lanjut'

        #creat marker
        folium.Marker(
          [list_rekom[0]['Latitude'],list_rekom[0]['Longitude']],
          popup = list_rekom[0]['Nama_warung'][0],
          tooltip = tooltip
        ).add_to(map)

        folium.Marker(
          [list_rekom[1]['Latitude'], list_rekom[1]['Longitude']],
          popup=list_rekom[1]['Nama_warung'][0],
          tooltip=tooltip
        ).add_to(map)

        folium.Marker(
          [list_rekom[2]['Latitude'], list_rekom[2]['Longitude']],
          popup=list_rekom[2]['Nama_warung'][0],
          tooltip=tooltip
        ).add_to(map)

        folium.Marker(
          [list_rekom[3]['Latitude'], list_rekom[3]['Longitude']],
          popup=list_rekom[3]['Nama_warung'][0],
          tooltip=tooltip
        ).add_to(map)

        folium.Marker(
          [list_rekom[4]['Latitude'], list_rekom[4]['Longitude']],
          popup=list_rekom[4]['Nama_warung'][0],
          tooltip=tooltip
        ).add_to(map)

        #generate map
        map.save('templates/map.html')

        return render_template('rekomendasi.html', hasil = text, rekom = list_rekom)



@app.route('/map')
def show_map():
    return render_template('map.html')

if __name__ == '__main__':
   app.run(debug = True)
