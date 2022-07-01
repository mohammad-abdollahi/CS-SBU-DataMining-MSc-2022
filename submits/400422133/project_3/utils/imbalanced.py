import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN, BorderlineSMOTE


def handle_imbalanced(data:pd.DataFrame, config:dict) -> dict:
    """ module to handle imbalanced dataset

    Args:
        data (pd.DataFrame): our imbalanced dataset
        config (dict): configs for handling imbalanced dataset including method, minor class, major class

    Returns:
        dict: balanced dataset
    """    
    if config['method'] == 'undersampling':
        y = data['class']
        x = data.drop(['class'], axis=1)
        undersample = RandomUnderSampler(sampling_strategy='majority')
        X_over, y_over = undersample.fit_resample(x, y)
        return pd.concat([X_over, y_over], axis=1, join='inner').to_dict()
    
    elif config['method'] == 'oversampling':
        y = data['class']
        x = data.drop(['class'], axis=1)
        oversample = RandomOverSampler(sampling_strategy='minority')
        X_over, y_over = oversample.fit_resample(x, y)
        return pd.concat([X_over, y_over], axis=1, join='inner').to_dict()

    elif config['method'] == 'SMOTE':
        if data[data['class'] == config['minor_class']]['class'].count() == 1:
            data = pd.concat([data, data[data['class'] == config['minor_class']]])
        y = data['class']
        x = data.drop(['class'], axis=1)

        if data[data['class'] == config['minor_class']]['class'].count() <= 6:
            oversample = SMOTE(k_neighbors=data[data['class'] == config['minor_class']]['class'].count()-1)
        else:
            oversample = SMOTE()
        
        X_over, y_over = oversample.fit_resample(x, y)
        return pd.concat([X_over, y_over], axis=1, join='inner').to_dict()
    
    elif config['method'] == 'ADASYN':
        if data[data['class'] == config['minor_class']]['class'].count() == 1:
            data = pd.concat([data, data[data['class'] == config['minor_class']]])
        y = data['class']
        x = data.drop(['class'], axis=1)

        if data[data['class'] == config['minor_class']]['class'].count() <= 6:
            oversample = ADASYN(n_neighbors=data[data['class'] == config['minor_class']]['class'].count()-1)
        else:
            oversample = ADASYN()
        
        X_over, y_over = oversample.fit_resample(x, y)
        return pd.concat([X_over, y_over], axis=1, join='inner').to_dict()
    
    elif config['method'] == 'BorderlineSMOTE':
        if data[data['class'] == config['minor_class']]['class'].count() == 1:
            data = pd.concat([data, data[data['class'] == config['minor_class']]])
        y = data['class']
        x = data.drop(['class'], axis=1)

        if data[data['class'] == config['minor_class']]['class'].count() <= 6:
            k_neighbors=data[data['class'] == config['minor_class']]['class'].count()-1
        else:
            k_neighbors==5
        if y.size <= 10:
            m_neighbor = y.size - 1
        else:
            m_neighbor = 10
        oversample = BorderlineSMOTE(k_neighbors=k_neighbors, m_neighbors=m_neighbor)
        X_over, y_over = oversample.fit_resample(x, y)
        return pd.concat([X_over, y_over], axis=1, join='inner').to_dict()    
    