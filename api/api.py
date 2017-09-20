# filename: api.py
"""Basic api"""
import hug
import pandas as pd
import numpy as np
from sklearn import ensemble
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
from sklearn import  linear_model
import pickle

retrain = False
model_type = "linear"
data_file = "loto_fin.csv"

xcols = ['nezam', 'loto_pp', 'vhp', 'live', 'regul_misto', 'regul_cas', 'regul_vsude']
ycols = ['podil_obyv_exek']

def retrain_models():
    """Retrains all models"""
    data = pd.read_csv(data_file)
    data = data[data.obyv15 != 0]
    data = data[xcols + ycols].replace([np.inf, -np.inf], np.nan).dropna()

    # GB params
    params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
                'learning_rate': 0.01, 'loss': 'ls'}
    clf_gb = ensemble.GradientBoostingRegressor(**params)

    # fit GB model
    clf_gb.fit(data[xcols], data[ycols[0]])
                                
    fileHandle1 = open('gb_model.pickle', "wb")
    pickle.dump(clf_gb, fileHandle1)
    fileHandle1.close()

    # Linear model

    clf_lm = linear_model.LinearRegression()

    # fit linear model
    clf_lm.fit(data[xcols], data[ycols[0]])

    # Save linear model

    fileHandle2 = open('lm_model.pickle', "wb")
    pickle.dump(clf_lm, fileHandle2)
    fileHandle2.close()

if retrain:
    retrain_models()

if model_type == "linear":
    with open('lm_model.pickle', 'rb') as handle:
        clf = pickle.load(handle)
else:
    with open('gb_model.pickle', 'rb') as handle:
        clf = pickle.load(handle)

# Load data and drop missing and infinite values
data = pd.read_csv(data_file, index_col='ruian', dtype={'ruian': 'int'})[xcols + ycols].replace([np.inf, -np.inf], np.nan).dropna()

def cors_support(response, *args, **kwargs):
    """Support for cross site"""
    response.set_header('Access-Control-Allow-Origin', '*')

@hug.get('/update', requires=cors_support, output=hug.output_format.json)
def update(reload:hug.types.number=0,
           vht:hug.types.float_number=None,
           ivt:hug.types.float_number=None,
           live:hug.types.float_number=None,
           other:hug.types.float_number=None,
           regul_cas:hug.types.float_number=None,
           regul_misto:hug.types.float_number=None,
           regul_vsude:hug.types.float_number=None,
           limit:hug.types.float_number=None):
    """Updates data based on user's input"""

    print("Reload: {}".format(reload*1))
    output = data.copy()
    
    if int(reload) != 1:
        model_data = output.copy()
        if vht is not None and vht != -1:
            output["vht"] = vht
#         if ivt is not None and ivt != -1:
#             output["ivt"] = ivt
        if live is not None and live != -1:
            output["live"] = live
        #if other is not None and other != -1:
            #output["other"] = other
        if regul_misto is not None and regul_misto != -1:
            output["regul_misto"] = regul_misto
        if regul_cas is not None and regul_cas != -1:
            output["regul_cas"] = rcas
        if regul_vsude is not None and regul_vsude != -1:
            output["regul_vsude"] = regul_vsude
        if limit is not None and limit < 100:
            output.loc[(output["loto_10tis"] >= limit), "loto_10tis"] = limit
        output = pd.DataFrame(clf.predict(output[xcols]), columns = ycols, index = output.index)
                
    return output[ycols].to_json(orient='index')
