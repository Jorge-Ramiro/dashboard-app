import os
import shutil
import zipfile
import pandas as pd

if os.path.exists('dataset-zip/denue_00_31-33_csv.zip'):
    with zipfile.ZipFile("dataset-zip/denue_00_31-33_csv.zip", 'r') as zip_ref:
        zip_ref.extractall("dataset-zip/")

    with open("dataset-zip/conjunto_de_datos/denue_inegi_31-33_.csv", encoding="latin-1") as file:
            with open("dataset-zip/denue_inegi.csv", "w+", encoding="utf-8") as new_file:
                for line in file:
                    new_file.write(line)

    if not os.path.exists('data'):
        os.mkdir('data')
        cols_to_use = ['codigo_act', 'nombre_act', 'cve_ent', 'entidad', 'fecha_alta']
        df = pd.read_csv('dataset-zip/denue_inegi.csv', usecols=cols_to_use)
        df.to_csv('data/denue_inegi.csv', encoding='UTF-8', index=False)

        shutil.rmtree('dataset-zip/conjunto_de_datos')
        shutil.rmtree('dataset-zip/diccionario_de_datos')
        shutil.rmtree('dataset-zip/metadatos')
        os.remove('dataset-zip/denue_inegi.csv')

else:
    raise FileNotFoundError('File Missing "datos-zip/denue_00_31-33_csv.zip"')