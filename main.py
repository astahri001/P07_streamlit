import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import streamlit as st
import streamlit.components.v1 as components

model_load = pickle.load(open('banking_model.md', 'rb'))
shap_values = pickle.load(open('shap_values', 'rb'))

features = ['EXT_SOURCE_3', 'AMT_REQ_CREDIT_BUREAU_QRT', 'AMT_REQ_CREDIT_BUREAU_YEAR', 'EXT_SOURCE_2',
            'DAYS_EMPLOYED', 'DAYS_LAST_PHONE_CHANGE', 'OBS_30_CNT_SOCIAL_CIRCLE', 'REGION_POPULATION_RELATIVE',
            'CNT_FAM_MEMBERS', 'DAYS_ID_PUBLISH', 'AMT_ANNUITY']
best_parameters = {'colsample_by_tree': 0.6000000000000001,
                   'learning_rate': 0.026478707430398492,
                   'max_depth': 28.0,
                   'n_estimators': 1000.0,
                   'num_leaves': 4.0,
                   'reg_alpha': 0.8,
                   'reg_lambda': 0.7000000000000001,
                   'solvability_threshold': 0.25,
                   'subsample': 0.8}

st.write('''
# Welcome to the bank loan analysis

###### This application gives the bank's decision for a loan request 
''')

st.sidebar.header("customer's ID")

# Load Dataframe

input_id = st.sidebar.text_input("Please enter the customer's id", '272011')
input_id = int(input_id)


@st.cache  # mise en cache de la fonction pour exécution unique
def get_data(df):
    dataframe = pd.read_csv(df, index_col=0)
    return dataframe


def get_green_color(text):
    st.markdown(f'<h1 style="color:#23b223;font-size:20px;">{text}</h1>',
                unsafe_allow_html=True)



def get_red_color(url):
    st.markdown(f'<h1 style="color:#ff3333;font-size:20px;">{url}</h1>',
                unsafe_allow_html=True)


def predict(model, id_client, df):
    data_1 = df.drop('TARGET', axis=1)
    prediction_result = model.predict_proba(pd.DataFrame(data_1.loc[id_client]).transpose())[:, 1]
    prediction_bool = np.array((prediction_result > best_parameters['solvability_threshold']) > 0) * 1
    if prediction_bool == 0:
        prediction_decision = 'Loan approved'
    else:
        prediction_decision = 'Loan refused'
    return prediction_decision, prediction_result


def get_mean(feature, df, id):
    data_1 = df[df['TARGET'] == 1]
    data_0 = df[df['TARGET'] == 0]
    mean_accepted = data_0[feature].mean()
    mean_denided = data_1[feature].mean()
    feature_client = df[feature][id]

    fig, ax = plt.subplots()
    fig_1 = sns.barplot(x=['mean_accepted', 'mean_refused', 'feature_client'],
                        y=[mean_accepted, mean_denided, feature_client])
    fig_1.set_xticklabels(labels=['mean_accepted', 'mean_refused', 'feature_client'],
                          rotation=45)

    return st.pyplot(fig)


def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)


def get_shap_fig(id_c):
    data_1 = data.drop('TARGET', axis=1)
    id_i = {}
    i = 0
    for idx in data_1.index:
        id_i[idx] = i
        i += 1
    figure_3 = shap.force_plot(shap_values[id_i[id_c]])
    return figure_3


# Appel des fonstion définies:

data = get_data('Data.csv')
bank_decision, probability = predict(model_load, input_id, data)
st.subheader(f'Bank decision for customer with ID: {input_id}')

# Décision de la banque et score:
st.write(f'##### Probability of default: {round(probability[0] * 100, 1)} (%)')
if bank_decision == 'Loan approved':
    get_green_color(f'Bank decision: {bank_decision}')
else:
    get_red_color(f'Bank decision: {bank_decision}')

# Affichage des graphes shap pour l'explicabilité du modèle:

st.subheader("Features importance")
st_shap(get_shap_fig(input_id), 600)

# Comparaison du client avec la moyenne positif et négatif:
st.subheader("More details for costumer:")
st.text('We will now compare the value of each feature with mean accepted and mean refused')
features_options = st.selectbox('Choose the feature you want to compare:', features)
get_mean(features_options, data, input_id)


#st_shap(shap.force_plot(shap_values), 600)
# st_shap(shap.plots.beeswarm(shap_values))
