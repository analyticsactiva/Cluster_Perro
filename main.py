import pandas as pd
import time
import pickle
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from openpyxl import load_workbook
from io import BytesIO
from pyxlsb import open_workbook as openxlsb
#from xlswriter import Workbook
import yaml
from yaml.loader import SafeLoader

# ----------------------------- Definición de variables -------------------------------------

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


x_columns = ['SEXO','GSE_POND_ESOMAR','ZONA_POND','EDAD_POND','P5',
             'P6_A','P6_B','P6_C','P6_D','P6_E','P6_F','P6_G','P6_H',
             'P6_I','P6_J','P6_K','P6_L','P6_M','P6_N','P6_O','P6_P',
             'P7_1','P7_2','P7_3','P7_4','P7_5']



def cluster_label(cluster):
    dic_cluster = {
        1: 'Cuidador Condicional',
        2: 'Hogareños',
        3: 'Tradicional Cercano',
        4: 'Tradicional Distante',
        5: 'Dog Lovers'
    }
    return dic_cluster[cluster]

def cluster_desc(cluster):
    dic_desc_cluster = {
        1: '28%'+' de la población. \n Madres jóvenes que hacen rendir su presupuesto. La alimentación es práctica, se debe adaptar a una vida con poco tiempo y muchas cosas, y a su vez enfocarla en los más pequeños.',
        2: '24%'+' de la población. \n Jóvenes que viven solos o en pareja. Disfrutan de la vida y dedican tiempo al deporte y vida saludable. La alimentación debe ser práctica, saludable y para disfrute, y en todo momento o lugar.',
        3: '14%'+' de la población. \n Mujeres con hijos ya adultos. Realizan deporte y privilegian la alimentación saludable y respetuosa, que además tenga bajo aporte en calorías. Abiertas a la innovación y tendencias en alimentación. ',
        4: '19%'+' de la Población. \n Hombres, que impulsan una vida y alimentación saludable para ellos y su familia, con marcas de confianza y respetuosas del entorno, y mejor si se adaptan a una vida rápida.',
        5: '16%'+' de la población. \n Viven solos o en hogares pequeños, con un buen presupuesto familiar. Buscan el disfrute, relajarse y lo práctico a la hora de alimentarse, y si es algo sano, que aporta a la salud, mejor aún.'
    }
    return dic_desc_cluster[cluster]

# ---------------------------- Cargar Modelo ----------------------------------

with open('scaler_dog.pkl','rb') as f:
    scaler = pickle.load(f)

# load the model from disk
filename = 'finalized_model_dog.sav'
modelo_svm2 = pickle.load(open(filename, 'rb'))

# modelo random forest

def get_cluster(new_x):
    x_pred = scaler.transform(new_x)

    pred = modelo_svm2.predict(x_pred)

    return int(pred[0])

def get_clusters(new_x):
    x_pred = scaler.transform(new_x)

    pred = modelo_svm2.predict(x_pred)

    return pred


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

hashed_passwords = Hasher(['Baf60255', 'activa1']).generate()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('main', fields = {'Form name': 'Activa Research'})


if st.session_state["authentication_status"]:

    cols = st.columns(4)

    # the 3rd column
    with cols[3]:
        authenticator.logout("Logout", "main")
    #authenticator.logout('Logout', 'main')
    #st.write(f'Bienvenido *{st.session_state["name"]}*')
    #st.title('Some content')

    st.image('logo-activa.svg',width=100)
    # --------------------- Display Barra Lateral -----------------------------------



    # ---------------------------------------- Display Resultado ---------------------------------------------

    progress_text = "Cargando. Por favor espere."
    my_bar = st.progress(0, text=progress_text)


    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()


    #on = st.toggle("Información del modelo")

    #if on:
    #    st.write("Modelo: Maquina de Soporte Vectorial")
    #    st.write('Confiabilidad del modelo en el conjunto de entrenamiento: 84%')

    # ------------------------ Cargar archivo ---------------------------------

    uploaded_file = st.file_uploader("Elegir Archivo", type = 'xlsx')
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        #st.dataframe(df1)

        book = load_workbook(uploaded_file)

        X = df[x_columns]

        X_transform = pd.get_dummies(X)

        pred_clusters = pd.DataFrame(get_clusters(X_transform))
        pred_clusters.rename(columns={0:'Cluster'},inplace=True)
        pred_clusters['Etiqueta_Cluster'] = pred_clusters.Cluster.apply(cluster_label)

        pred_clusters.reset_index(inplace = True)

        pred_clusters.set_index(df.index)

        df_new = pd.concat([df,pred_clusters],axis=1)

        #st.write(uploaded_file)

        #with pd.ExcelWriter(uploaded_file, engine = 'openpyxl') as writer:
                #writer.book = book
                #writer.sheets = dict((ws.title, ws) for ws in book.worksheets)    

                #df_new.to_excel(writer, sheet_name='Cluster_Pred', engine = 'openpyxl',index = False)
                #writer.close()
                #book.save(uploaded_file)
                #book.close()
        #output_file = to_excel(df_new)
        #output_file = df_new.to_excel(index=False, sheet_name='Cluster_Pred', engine='openpyxl')
        output_file = df_new.to_csv(index=False).encode('latin-1')
        st.download_button(label="Descargar", data=output_file,file_name='Cluster.csv')
    #st.write("")
    
    #with cols[3]:
    
    #st.image('logo-activa.svg',width=100)

elif st.session_state["authentication_status"] == False:
    st.error('Usuario/Contraseña incorrecta')
elif st.session_state["authentication_status"] == None:
    st.warning('Por favor ingrese su usuario y contraseña')