# flake8: noqa: E501
#
# En este dataset se desea pronosticar el default (pago) del cliente el próximo
# mes a partir de 23 variables explicativas.
#
#   LIMIT_BAL: Monto del credito otorgado. Incluye el credito individual y el
#              credito familiar (suplementario).
#         SEX: Genero (1=male; 2=female).
#   EDUCATION: Educacion (0=N/A; 1=graduate school; 2=university; 3=high school; 4=others).
#    MARRIAGE: Estado civil (0=N/A; 1=married; 2=single; 3=others).
#         AGE: Edad (years).
#       PAY_0: Historia de pagos pasados. Estado del pago en septiembre, 2005.
#       PAY_2: Historia de pagos pasados. Estado del pago en agosto, 2005.
#       PAY_3: Historia de pagos pasados. Estado del pago en julio, 2005.
#       PAY_4: Historia de pagos pasados. Estado del pago en junio, 2005.
#       PAY_5: Historia de pagos pasados. Estado del pago en mayo, 2005.
#       PAY_6: Historia de pagos pasados. Estado del pago en abril, 2005.
#   BILL_AMT1: Historia de pagos pasados. Monto a pagar en septiembre, 2005.
#   BILL_AMT2: Historia de pagos pasados. Monto a pagar en agosto, 2005.
#   BILL_AMT3: Historia de pagos pasados. Monto a pagar en julio, 2005.
#   BILL_AMT4: Historia de pagos pasados. Monto a pagar en junio, 2005.
#   BILL_AMT5: Historia de pagos pasados. Monto a pagar en mayo, 2005.
#   BILL_AMT6: Historia de pagos pasados. Monto a pagar en abril, 2005.
#    PAY_AMT1: Historia de pagos pasados. Monto pagado en septiembre, 2005.
#    PAY_AMT2: Historia de pagos pasados. Monto pagado en agosto, 2005.
#    PAY_AMT3: Historia de pagos pasados. Monto pagado en julio, 2005.
#    PAY_AMT4: Historia de pagos pasados. Monto pagado en junio, 2005.
#    PAY_AMT5: Historia de pagos pasados. Monto pagado en mayo, 2005.
#    PAY_AMT6: Historia de pagos pasados. Monto pagado en abril, 2005.
#
# La variable "default payment next month" corresponde a la variable objetivo.
#
# El dataset ya se encuentra dividido en conjuntos de entrenamiento y prueba
# en la carpeta "files/input/".
#
# Los pasos que debe seguir para la construcción de un modelo de
# clasificación están descritos a continuación.
#
#
# Paso 1.
# Realice la limpieza de los datasets:
# - Renombre la columna "default payment next month" a "default".
# - Remueva la columna "ID".
# - Elimine los registros con informacion no disponible.
# - Para la columna EDUCATION, valores > 4 indican niveles superiores
#   de educación, agrupe estos valores en la categoría "others".
# - Renombre la columna "default payment next month" a "default"
# - Remueva la columna "ID".
#
#
# Paso 2.
# Divida los datasets en x_train, y_train, x_test, y_test.
#
#
# Paso 3.
# Cree un pipeline para el modelo de clasificación. Este pipeline debe
# contener las siguientes capas:
# - Transforma las variables categoricas usando el método
#   one-hot-encoding.
# - Ajusta un modelo de bosques aleatorios (rando forest).
#
#
# Paso 4.
# Optimice los hiperparametros del pipeline usando validación cruzada.
# Use 10 splits para la validación cruzada. Use la función de precision
# balanceada para medir la precisión del modelo.
#
#
# Paso 5.
# Guarde el modelo (comprimido con gzip) como "files/models/model.pkl.gz".
# Recuerde que es posible guardar el modelo comprimido usanzo la libreria gzip.
#
#
# Paso 6.
# Calcule las metricas de precision, precision balanceada, recall,
# y f1-score para los conjuntos de entrenamiento y prueba.
# Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# Este diccionario tiene un campo para indicar si es el conjunto
# de entrenamiento o prueba. Por ejemplo:
#
# {'dataset': 'train', 'precision': 0.8, 'balanced_accuracy': 0.7, 'recall': 0.9, 'f1_score': 0.85}
# {'dataset': 'test', 'precision': 0.7, 'balanced_accuracy': 0.6, 'recall': 0.8, 'f1_score': 0.75}
#
#
# Paso 7.
# Calcule las matrices de confusion para los conjuntos de entrenamiento y
# prueba. Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# de entrenamiento o prueba. Por ejemplo:
#
# {'type': 'cm_matrix', 'dataset': 'train', 'true_0': {"predicted_0": 15562, "predicte_1": 666}, 'true_1': {"predicted_0": 3333, "predicted_1": 1444}}
# {'type': 'cm_matrix', 'dataset': 'test', 'true_0': {"predicted_0": 15562, "predicte_1": 650}, 'true_1': {"predicted_0": 2490, "predicted_1": 1420}}
#

import os
import json
import zipfile
import gzip
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import precision_score, recall_score, f1_score, balanced_accuracy_score


def load_data_train():
    with zipfile.ZipFile('files/input/train_data.csv.zip', 'r') as file:
        # print(file.namelist())
        with file.open('train_default_of_credit_card_clients.csv') as f:
            data = pd.read_csv(f)
    return data

def load_data_test():
    with zipfile.ZipFile('files/input/test_data.csv.zip', 'r') as file:
        # print(file.namelist())
        with file.open('test_default_of_credit_card_clients.csv') as f:
            data = pd.read_csv(f)
    return data

def clean_data(data):
    data = data.rename(columns={'default payment next month': 'default'})
    data = data.drop(columns='ID')
    data = data.dropna()
    data.loc[data['EDUCATION'] > 4, 'EDUCATION'] = 4
    return data

def split_data(data):
    x = data.drop(columns='default')
    y = data['default']
    return x, y

def create_pipeline():
    categorical = ["SEX", "EDUCATION", "MARRIAGE"]
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(), categorical)
            ],
        remainder='passthrough'
            )
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
        ])
    
    return model_pipeline

def optimize_hyperparameters(model, x, y):
    param_grid = {
        'classifier__n_estimators': [200],
        'classifier__max_depth': [None],
        'classifier__min_samples_split': [10],
        'classifier__min_samples_leaf': [1, 2],
        'classifier__max_features': ['sqrt']
    }

    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=10,
        scoring="balanced_accuracy",
        n_jobs=-1,
        verbose=2,
        refit=True
    )

    grid_search.fit(x, y)

    return grid_search

def save_model(model):
    os.makedirs('files/models', exist_ok=True)
    with gzip.open('files/models/model.pkl.gz', 'wb') as file:
        pickle.dump(model, file)

def calculate_metrics(model, x_train, y_train, x_test, y_test):
    metrics = []
    
    for dataset, x, y in zip(['train', 'test'], [x_train, x_test], [y_train, y_test]):
        y_pred = model.predict(x)
        
        metrics.append({
            'dataset': dataset,
            'accuracy': model.score(x, y),
            'precision': precision_score(y, y_pred, average='weighted'),
            'recall': recall_score(y, y_pred, average='weighted'),
            'f1_score': f1_score(y, y_pred, average='weighted'),
            'balanced_accuracy': balanced_accuracy_score(y, y_pred)
        })
    
    return metrics

def calculate_confusion_matrix(model, x_train, y_train, x_test, y_test):
    cm_matrix = []
    for dataset, x, y in zip(['train', 'test'], [x_train, x_test], [y_train, y_test]):
        y_pred = model.predict(x)
        cm = pd.crosstab(y, y_pred, rownames=['True'], colnames=['Predicted'], margins=True)
        cm_matrix.append({
            'type': 'cm_matrix',
            'dataset': dataset,
            'true_0': {"predicted_0": cm[0][0], "predicted_1": cm[0][1]},
            'true_1': {"predicted_0": cm[1][0], "predicted_1": cm[1][1]}
        })
    return cm_matrix



if __name__ == "__main__":
    data_train = load_data_train()
    data_train = clean_data(data_train)
    x_train, y_train = split_data(data_train)

    data_test = load_data_test()
    data_test = clean_data(data_test)
    x_test, y_test = split_data(data_test)

    model = create_pipeline()
    model = optimize_hyperparameters(model, x_train, y_train)
    save_model(model)

    metrics = calculate_metrics(model, x_train, y_train, x_test, y_test)
    os.makedirs('files/output', exist_ok=True)
    with open('files/output/metrics.json', 'w') as file:
        json.dump(metrics, file)

    cm_matrix = calculate_confusion_matrix(model, x_train, y_train, x_test, y_test)
    os.makedirs('files/output', exist_ok=True)
    with open('files/output/confusion_matrix.json', 'w') as file:
        json.dump(cm_matrix, file)