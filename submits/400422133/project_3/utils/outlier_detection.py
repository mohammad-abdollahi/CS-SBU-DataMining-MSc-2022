import pandas as pd
import numpy as np
from adtk.detector import QuantileAD, GeneralizedESDTestAD, PcaAD
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor


def outlier_detection(data:pd.DataFrame, time_series:bool=True)-> dict:
    """ module for outlier detection

    Args:
        data (pd.DataFrame): dataframe which we want to interpolate
        time_series (bool, optional): if our data is time series or not. Defaults to True.

    Returns:
        dict: interpolated dataframe, outliers have true label
    """    
    if time_series:
        #times = data['time'].tolist()
        times = data['time'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
        data = data.set_index('time')

        pca_ad = PcaAD(k=1)
        pca_anomalies = pca_ad.fit_detect(data)
        pca_anomalies = pca_anomalies.fillna(False).tolist()

        esd_ad = GeneralizedESDTestAD(alpha=0.3)
        esd_anomalies = esd_ad.fit_detect(data['vol'])
        esd_anomalies = esd_anomalies.fillna(False).tolist()

        quantile_ad = QuantileAD(high=0.95, low=0.05)
        quantile_anomalies = quantile_ad.fit_detect(data['vol'])
        quantile_anomalies = quantile_anomalies.fillna(False).tolist()
        

    
        result = pd.DataFrame(list(zip(times, pca_anomalies, esd_anomalies, quantile_anomalies)), \
            columns=['Time', 'Pca method', 'GeneralizedESDTest method', 'Quantile method'])
        return result.to_dict()
    else:
        iso = IsolationForest(contamination=0.1)
        iso_anomalies = iso.fit_predict(data['feature1'].to_numpy().reshape(-1, 1))
        iso_anomalies = np.where(iso_anomalies==1, False, True)

        OneClassSvm = OneClassSVM(nu=0.01)
        svm_anomalies = OneClassSvm.fit_predict(data['feature1'].to_numpy().reshape(-1, 1))
        svm_anomalies = np.where(iso_anomalies==0, False, True)

        lof = LocalOutlierFactor()
        lof_anomalies = lof.fit_predict(data['feature1'].to_numpy().reshape(-1, 1))
        lof_anomalies = np.where(iso_anomalies==0, False, True)

        result = pd.DataFrame(list(zip(data['id'], iso_anomalies, svm_anomalies, lof_anomalies)), \
            columns=['id', 'Isolation Forest method', 'One-Class SVM method', 'Local Outlier Factor method'])
        return result.to_dict()