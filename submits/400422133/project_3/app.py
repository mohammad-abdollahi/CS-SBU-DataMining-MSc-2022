import json
import pandas as pd
from flask import Flask, request, jsonify
from utils.common import response_message, read_json_time_series
from utils.interpolation_methods import linear_interpolation, custom_interpolation, service2_interpolation
from utils.outlier_detection import outlier_detection
from utils.imbalanced import handle_imbalanced
from flasgger import Swagger


app = Flask(__name__)
# swagger config
swagger = Swagger(app)

@app.route('/', methods=['GET', 'POST'])
def isup():
    return response_message('API is active')

@app.route('/service1', methods=['POST'])
def interpolation():
    """
    Interpolate a time series dataframe
      This module gets a dataframe which includes time and volume and tries to interpolate missing data.
      I have implemented several methods for interpolation (service1-interpolation). 
    ---
    parameters:
      - name: data
        in: body
        description: The dataframe we want to interpolate.
        schema:
          type: object
          properties:
            time:
              type: array
              items:
                $ref: "#/definitions/service1-time"
            vol:
              type: array
              items:
                $ref: "#/definitions/service1-vol"
      - name: config
        in: body
        description: The specified config for interpolation.
        schema:
          type: object
          properties:
            type:
              $ref: "#/definitions/service1-type"
            interpolation:
              $ref: "#/definitions/service1-interpolation"
            time:
              $ref: "#/definitions/service1-config-time"
    responses:
      200:
        description: return the interpolated dataframe
        schema:
          type: object
          properties:
            time:
              type: array
              items:
                $ref: "#/definitions/service1-result-time"
            vol:
              type: array
              items:
                $ref: "#/definitions/service1-result-vol"
    definitions:
      service1-config-time:
        description: time scale
        type: string
        enum: ['monthly', 'daily']
        default: 'monthly'
      service1-interpolation:
        description: interpolation methods
        type: string
        enum: ['linear', 'index', 'values', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'barycentric', 'krogh',  'piecewise_polynomial', 'from_derivatives', 'pchip', 'akima', 'polynomial', 'spline']
        default: 'linear'
      service1-type:
        description: calender type
        type: string
        enum: ['shamsi', 'miladi']
        default: 'miladi'
      service1-time:
        type: object
        properities:
          id:string
          date:string
        example:
          "0": "2020-01-01"
          "1": "2020-02-01"
          "2": "2020-04-01"
      service1-vol:
        type: object
        properities:
          id:string
          vol:integer
        example:
          "0": 20
          "1": 40
          "2": 100
      service1-result-time:
        type: object
        properities:
          id:string
          date:string
        example:
          "0": "2020-01-01"
          "1": "2020-02-01"
          "2": "2020-03-01"
          "3": "2020-04-01"
      service1-result-vol:
        type: object
        properities:
          id:string
          vol:integer
        example:
          "0": 20
          "1": 40
          "2": 70
          "3": 100
    """
    
    req = request.get_json()
    data = req['data']
    config = req['config']

    data = read_json_time_series(json.dumps(data), config['type'])

    if config['interpolation'] == 'linear':
        result = linear_interpolation(data, config)
        return jsonify({"data": result})
    else:
        result = custom_interpolation(data, config)
        return jsonify({"data": result})

@app.route('/service2', methods=['POST'])
def interpolation2():
    """
    Interpolate a time series dataframe
      This module gets a dataframe which includes gregorian time and volumes and tries to interpolate missing data with jalali dates.
      I have implemented several ways to interpolate missing data.(service2-interpolation)
      Also, I have implemented skip_holiday option which allows you to skip fridays and thursdays through interpolatio.(service2-skip_holiday)
    ---
    parameters:
      - name: data
        in: body
        description: The dataframe we want to interpolate.
        schema:
          type: object
          properties:
            time:
              type: array
              items:
                $ref: "#/definitions/service2-time"
            vol:
              type: array
              items:
                $ref: "#/definitions/service2-vol"
      - name: config
        in: body
        description: The specified config for interpolation.
        schema:
          type: object
          properties:
            skip_holiday:
              $ref: "#/definitions/service2-skip_holiday"
            interpolation:
              $ref: "#/definitions/service2-interpolation"
            time:
              $ref: "#/definitions/service2-config-time"
    responses:
      200:
        description: return the interpolated dataframe
        schema:
          type: object
          properties:
            time:
              type: array
              items:
                $ref: "#/definitions/service2-result-time"
            vol:
              type: array
              items:
                $ref: "#/definitions/service2-result-vol"
    definitions:
      service2-config-time:
        description: time scale
        type: string
        enum: ['monthly', 'daily']
        default: 'monthly'
      service2-interpolation:
        description: interpolation method
        type: string
        enum: ['linear', 'index', 'values', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'barycentric', 'krogh',  'piecewise_polynomial', 'from_derivatives', 'pchip', 'akima', 'polynomial', 'spline']
        default: 'linear'
      service2-skip_holiday:
        description: If true, we will skip firdays and thursdays. I have implemented it in a way just to skip weekends not all holidays.
        type: boolean
        default: False
      service2-time:
        type: object
        properities:
          id:string
          date:string
        example:
          "0": "2020-01-01"
          "1": "2020-02-01"
          "2": "2020-04-01"
      service2-vol:
        type: object
        properities:
          id:string
          vol:integer
        example:
          "0": 20
          "1": 40
          "2": 100
      service2-result-time:
        type: object
        properities:
          id:string
          date:string
        example:
          "0": "1398-11-01"
          "1": "1398-12-01"
          "2": "1399-01-01"
          "3": "1399-02-01"
      service2-result-vol:
        type: object
        properities:
          id:string
          vol:integer
        example:
          "0": 20
          "1": 40
          "2": 70
          "3": 100
    """

    req = request.get_json()
    data = req['data']
    config = req['config']

    data = read_json_time_series(json.dumps(data), 'miladi')
    result = service2_interpolation(data, config)

    return jsonify({"data": result})

@app.route('/service3', methods=['POST'])
def outlier_service():
    """Find outliers in a feature list
      This module recieves a feature list and tries to detect outlier within that feature. our feature can be a uni-variate time series or list. 
      I have implemented three methods for time-series data outlier detection: 1.QuantileAD 2.GeneralizedESDTestAD 3.PcaAD
      and three methods for the other case: 1.IsolationForest 2.OneClassSVM 3.LocalOutlierFactor
    ---
    parameters:
      - name: data
        in: body
        description: The dataframe we want to detect its outliers.
        schema:
          type: object
          properties:
            id:
              type: array
              items:
                $ref: "#/definitions/service3-id"
            feature1:
              type: array
              items:
                $ref: "#/definitions/service3-feature1"
      - name: config
        in: body
        description: The specified config for outlier detection.
        schema:
          type: object
          properties:
            time_series:
              $ref: "#/definitions/service3_time_series"
    responses:
      200:
        description: return a dataframe that contains if a data point is outlier or not based on our three methods for outlier detection
        schema:
          type: object
          properties:
            id:
              type: array
              items:
                $ref: "#/definitions/service3-result-id"
            Isolation Forest method:
              type: array
              items:
                $ref: "#/definitions/service3-method1"
            Local Outlier Factor method:
              type: array
              items:
                $ref: "#/definitions/service3-method2"
            One-Class SVM method:
              type: array
              items:
                $ref: "#/definitions/service3-method3"
    definitions:
      service3-id:
        type: object
        properities:
          index: string
          id: integer
        example:
          "0": 1
          "1": 2
          "2": 3
          "3": 4
          "4": 5
          "5": 6
      service3-feature1:
        type: object
        properities:
          index: string
          feature: integer
        example:
          "0": 100
          "1": 20
          "2": 35
          "3": 67
          "4": 89
          "5": 90
      service3_time_series:
        type: boolean
        default: false
      service3-result-id:
        type: object
        properities:
          index: string
          id: integer
        example:
          "0": 1
          "1": 2
          "2": 3
          "3": 4
          "4": 5
          "5": 6
      service3-method1:
        type: object
        properities:
          index: string
          Isolation Forest method: boolean
        example:
          "0": false,
          "1": true,
          "2": false,
          "3": false,
          "4": false,
          "5": false
      service3-method2:
        type: object
        properities:
          index: string
          Local Outlier Factor method: boolean
        example:
          "0": false
          "1": true
          "2": false
          "3": false
          "4": false
          "5": false
      service3-method3:
        type: object
        properities:
          index: string
          One-Class SVM method: boolean
        example:
          "0": false
          "1": true
          "2": false
          "3": false
          "4": false
          "5": false
    """
    req = request.get_json()
    data = req['data']
    config = req['config']

    if config['time_series']:
        data = read_json_time_series(json.dumps(data), 'miladi')
    else:
        print(type(data))
        data = pd.DataFrame.from_dict(data)
    
    result = outlier_detection(data, config['time_series'])
    return jsonify({"data": result})

@app.route('/service4', methods=['POST'])
def imbalanced_service():
    """Handle imbalanced dataset
      This module recieves an imbalanced dataset and a specific method, then tries to handle imbalanced dataset based on the desired method. 
      I have implemented 5 methods for hanlding imbalanced data.(service4_method)
    ---
    parameters:
      - name: data
        in: body
        description: The dataframe we want to handle.
        schema:
          type: object
          properties:
            id:
              type: array
              items:
                $ref: "#/definitions/service4-id"
            feature1:
              type: array
              items:
                $ref: "#/definitions/service4-feature1"
            class:
              type: array
              items:
                $ref: "#/definitions/service4-class"
      - name: config
        in: body
        description: The specified config for handling imbalanced data.
        schema:
          type: object
          properties:
            method:
              $ref: "#/definitions/service4_method"
            major_class:
              type: integer
              example: 1
            minor_class:
              type: integer
              example: 0
    responses:
      200:
        description: Returns a balanced dataframe.
        schema:
          type: object
          properties:
            id:
              type: array
              items:
                $ref: "#/definitions/service4-result-id"
            feature1:
              type: array
              items:
                $ref: "#/definitions/service4-result-feature1"
            class:
              type: array
              items:
                $ref: "#/definitions/service4-result-class"
    definitions:
      service4-id:
        type: object
        properities:
          index: string
          id: integer
        example:
          "0": 1
          "1": 2
          "2": 3
          "3": 4
          "4": 5
          "5": 6
          "6": 7
      service4-feature1:
        type: object
        properities:
          index: string
          feature1: integer
        example:
          "0": 50
          "1": 12
          "2": 50
          "3": 500
          "4": 60
          "5": 12
          "6": 30
      service4-class:
        type: object
        properities:
          index: string
          class: integer
        example:
          "0": 1
          "1": 1
          "2": 1
          "3": 1
          "4": 1
          "5": 0
          "6": 0
      service4_method:
        type: string
        description: The method to handle imbalanced data.
        enum: ['SMOTE', 'undersampling', 'oversampling', 'ADASYN', 'BorderlineSMOTE']
        default: 'SMOTE'
      service4-result-id:
        type: object
        properities:
          index: string
          id: integer
        example:
          "0": 1
          "1": 2
          "2": 3
          "3": 4
          "4": 5
          "5": 6
          "6": 7
          "7": 6
          "8": 6
          "9": 6
      service4-result-feature1:
        type: object
        properities:
          index: string
          feature1: integer
        example:
          "0": 50
          "1": 12
          "2": 50
          "3": 500
          "4": 60
          "5": 12
          "6": 30
          "7": 19
          "8": 28
          "9": 16
      service4-result-class:
        type: object
        properities:
          index: string
          class: integer
        example:
          "0": 1
          "1": 1
          "2": 1
          "3": 1
          "4": 1
          "5": 0
          "6": 0
          "7": 0
          "8": 0
          "9": 0
    """

    req = request.get_json()
    data = req['data']
    config = req['config']

    data = pd.DataFrame.from_dict(data)
    result = handle_imbalanced(data, config)
    
    return jsonify({"data": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
