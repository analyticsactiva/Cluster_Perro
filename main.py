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

x_dummies_cols = ['SEXO_Hombre', 'SEXO_Mujer', 'GSE_POND_ESOMAR_ABC1',
       'GSE_POND_ESOMAR_C2', 'GSE_POND_ESOMAR_C3D', 'ZONA_POND_RM',
       'ZONA_POND_Regiones', 'EDAD_POND_25-34 años', 'EDAD_POND_35 a 44',
       'EDAD_POND_45 a 54', 'EDAD_POND_55+',
       'P5_Es parte integral de la familia, nos preocupamos mucho y le',
       'P5_Es una compañía importante, pero no siempre podemos darle',
       'P5_Es una mascota a la que cuidamos, pero no le dedicamos demas',
       'P5_Es una mascota que está con nosotros, pero no forma parte c',
       'P6_A_A diario/ Varias veces a la semana',
       'P6_A_Nunca/ Casi nunca', 'P6_A_Pocas veces al año',
       'P6_A_Una o dos veces a la semana', 'P6_A_Una o dos veces al mes',
       'P6_A_Una vez cada 2 o 3 meses',
       'P6_B_A diario/ Varias veces a la semana',
       'P6_B_Nunca/ Casi nunca', 'P6_B_Pocas veces al año',
       'P6_B_Una o dos veces a la semana', 'P6_B_Una o dos veces al mes',
       'P6_B_Una vez cada 2 o 3 meses',
       'P6_C_A diario/ Varias veces a la semana',
       'P6_C_Nunca/ Casi nunca', 'P6_C_Pocas veces al año',
       'P6_C_Una o dos veces a la semana', 'P6_C_Una o dos veces al mes',
       'P6_C_Una vez cada 2 o 3 meses',
       'P6_D_A diario/ Varias veces a la semana',
       'P6_D_Nunca/ Casi nunca', 'P6_D_Pocas veces al año',
       'P6_D_Una o dos veces a la semana', 'P6_D_Una o dos veces al mes',
       'P6_D_Una vez cada 2 o 3 meses',
       'P6_E_A diario/ Varias veces a la semana',
       'P6_E_Pocas veces al año', 'P6_E_Una o dos veces a la semana',
       'P6_E_Una o dos veces al mes', 'P6_E_Una vez cada 2 o 3 meses',
       'P6_F_A diario/ Varias veces a la semana',
       'P6_F_Nunca/ Casi nunca', 'P6_F_Pocas veces al año',
       'P6_F_Una o dos veces a la semana', 'P6_F_Una o dos veces al mes',
       'P6_F_Una vez cada 2 o 3 meses',
       'P6_G_A diario/ Varias veces a la semana',
       'P6_G_Nunca/ Casi nunca', 'P6_G_Pocas veces al año',
       'P6_G_Una o dos veces a la semana', 'P6_G_Una o dos veces al mes',
       'P6_G_Una vez cada 2 o 3 meses',
       'P6_H_A diario/ Varias veces a la semana',
       'P6_H_Nunca/ Casi nunca', 'P6_H_Pocas veces al año',
       'P6_H_Una o dos veces a la semana', 'P6_H_Una o dos veces al mes',
       'P6_H_Una vez cada 2 o 3 meses',
       'P6_I_A diario/ Varias veces a la semana',
       'P6_I_Nunca/ Casi nunca', 'P6_I_Pocas veces al año',
       'P6_I_Una o dos veces a la semana', 'P6_I_Una o dos veces al mes',
       'P6_I_Una vez cada 2 o 3 meses',
       'P6_J_A diario/ Varias veces a la semana',
       'P6_J_Nunca/ Casi nunca', 'P6_J_Pocas veces al año',
       'P6_J_Una o dos veces a la semana', 'P6_J_Una o dos veces al mes',
       'P6_J_Una vez cada 2 o 3 meses',
       'P6_K_A diario/ Varias veces a la semana',
       'P6_K_Nunca/ Casi nunca', 'P6_K_Pocas veces al año',
       'P6_K_Una o dos veces a la semana', 'P6_K_Una o dos veces al mes',
       'P6_K_Una vez cada 2 o 3 meses',
       'P6_L_A diario/ Varias veces a la semana',
       'P6_L_Nunca/ Casi nunca', 'P6_L_Pocas veces al año',
       'P6_L_Una o dos veces a la semana', 'P6_L_Una o dos veces al mes',
       'P6_L_Una vez cada 2 o 3 meses',
       'P6_M_A diario/ Varias veces a la semana',
       'P6_M_Nunca/ Casi nunca', 'P6_M_Pocas veces al año',
       'P6_M_Una o dos veces a la semana', 'P6_M_Una o dos veces al mes',
       'P6_M_Una vez cada 2 o 3 meses',
       'P6_N_A diario/ Varias veces a la semana',
       'P6_N_Nunca/ Casi nunca', 'P6_N_Pocas veces al año',
       'P6_N_Una o dos veces a la semana', 'P6_N_Una o dos veces al mes',
       'P6_N_Una vez cada 2 o 3 meses',
       'P6_O_A diario/ Varias veces a la semana',
       'P6_O_Nunca/ Casi nunca', 'P6_O_Pocas veces al año',
       'P6_O_Una o dos veces a la semana', 'P6_O_Una o dos veces al mes',
       'P6_O_Una vez cada 2 o 3 meses',
       'P6_P_A diario/ Varias veces a la semana',
       'P6_P_Nunca/ Casi nunca', 'P6_P_Pocas veces al año',
       'P6_P_Una o dos veces a la semana', 'P6_P_Una o dos veces al mes',
       'P6_P_Una vez cada 2 o 3 meses',
       'P7_1_Sí, lo llevo a la peluquería',
       'P7_2_Sí, lo llevo al veterinario',
       'P7_3_Sí, lo llevo a un especialista que se encarga de su higiene',
       'P7_4_Si, un especialista va mi casa',
       'P7_5_No, su higiene la realiza alguien de mi hogar']

p6_columns = ['P6_A','P6_B','P6_C','P6_D','P6_E','P6_F','P6_G','P6_H',
             'P6_I','P6_J','P6_K','P6_L','P6_M','P6_N','P6_O','P6_P']

p7_columns = ['P7_1','P7_2','P7_3','P7_4','P7_5']


dic_sexo = {
    1: 'Mujer',
    2: 'Hombre'
}

dic_gse = {
    1: 'ABC1',
    2: 'C2',
    3: 'C3D'
}

dic_zona = {
    1: 'Regiones',
    2: 'RM'
}

dic_edad = {
    1: '25-34 años',
    2: '35 a 44',
    3: '45 a 54',
    4: '55+'
}

dic_p5 = {
    1: 'Es parte integral de la familia, nos preocupamos mucho y le',
    2: 'Es una compañía importante, pero no siempre podemos darle',
    3: 'Es una mascota a la que cuidamos, pero no le dedicamos demas',
    4: 'Es una mascota que está con nosotros, pero no forma parte c'
}

dic_p6 = {
    1: 'A diario/ Varias veces a la semana',
    3: 'Una o dos veces a la semana',
    4: 'Una o dos veces al mes',
    5: 'Una vez cada 2 o 3 meses',
    6: 'Pocas veces al año',
    7: 'Nunca/ Casi nunca'
}

dic_p7 = {
    1: 'Sí, lo llevo a la peluquería',
    2: 'Sí, lo llevo al veterinario',
    3: 'Sí, lo llevo a un especialista que se encarga de su higiene',
    4: 'Si, un especialista va mi casa',
    5: 'No, su higiene la realiza alguien de mi hogar'
}

dic_cluster = {
    1: 'Cuidador Condicional',
    2: 'Hogareños',
    3: 'Tradicional Cercano',
    4: 'Tradicional Distante',
    5: 'Dog Lovers'
}

def relabel(value,dic):
    return dic[value]

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

        X = df[x_columns].copy()

        X['SEXO'] = X['SEXO'].apply(lambda x: relabel(x,dic_sexo))

        X['GSE_POND_ESOMAR'] = X['GSE_POND_ESOMAR'].apply(lambda x: relabel(x,dic_gse))

        X['ZONA_POND'] = X['ZONA_POND'].apply(lambda x: relabel(x,dic_zona))
        
        X['EDAD_POND'] = X['EDAD_POND'].apply(lambda x: relabel(x,dic_edad))

        X['P5'] = X['P5'].apply(lambda x: relabel(x,dic_p5) if pd.notnull(x) else x)

        for col in p6_columns:
            X[col] = X[col].apply(lambda x: relabel(x,dic_p6) if pd.notnull(x) else x)

        for col in p7_columns:
            X[col] = X[col].apply(lambda x: relabel(x,dic_p7) if pd.notnull(x) else x)

        X_transform = pd.get_dummies(X)

        for col in x_dummies_cols:
            if(col not in X_transform):
                X_transform[col] = False

        X_transform = X_transform[x_dummies_cols]

        pred_clusters = pd.DataFrame(get_clusters(X_transform))
        pred_clusters.rename(columns={0:'Cluster'},inplace=True)
        pred_clusters['Etiqueta_Cluster'] = pred_clusters.Cluster.apply(lambda x: relabel(x,dic_cluster))

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
