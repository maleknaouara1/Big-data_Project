import pickle
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from datetime import datetime

app = Flask(__name__)

# Connect to the Elasticsearch cluster
es = Elasticsearch(["http://localhost:9200"])  # Adjust as per your Elasticsearch setup

# Load the model
model = pickle.load(open('model.pkl', 'rb'))
try: 
    if es.ping():
         print("Elasticsearch is connected")
    else: 
        print("Failed to connect to Elasticsearch") 
except Exception as e: print(f"Error connecting to Elasticsearch: {e}")

def index_data(input_data, prediction_result):
    """ Index input data and prediction result into Elasticsearch """
    doc = {
        'input_data': input_data,
        'prediction_result': prediction_result,
        'timestamp': datetime.now().isoformat()
    }
    res = es.index(index="covid-prediction-index", body=doc)
    return res


@app.route("/", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        
        input_data = {
            'breathing_problem': 1 if 'breathingProblemYes' in request.form else 0,
            'fever': 1 if 'feverYes' in request.form else 0,
            'dry_cough': 1 if 'dryCoughYes' in request.form else 0,
            # Add the rest of your form fields here in a similar manner
            # 'sore_throat': 1 if 'soreThroatYes' in request.form else 0,
            'sore_throat': 1 if 'soreThroatYes' in request.form  else 0,
            'running_nose':1 if'runningNoseYes' in  request.form else 0,
            'headache':1 if'headacheYes'in  request.form else 0,
            'fatigue':1 if'fatigueYes'in  request.form else 0,
             'gastrointestinal':1 if'gastrointestinalYes' in  request.form else 0,

            'asthma':1 if'asthmaYes' in  request.form else 0,
            'chronic_lung_disease' :1 if'chronicLungDiseaseYes'in  request.form else 0,
            'heart_disease' :1 if'heartDiseaseYes' in  request.form else 0,
            'diabetes' :1 if'diabetesYes'in  request.form else 0,
            'hypertension' :1 if 'hyperTensionYes' in  request.form else 0,

            'abroad_travel': 1 if'abroadTravelYes' in  request.form else 0,
            'contact_with_covid_patient' : 1 if'contactWithCovidPatientYes' in  request.form else 0,
            'attended_large_gathering': 1 if'attendedLargeGatheringYes' in  request.form else 0,
            'visited_public_exposed_places' : 1 if 'visitedPublicExposedPlacesYes' in  request.form else 0,
            'family_working_in_public_places' : 1 if 'familyWorkingInPublicPlacesYes' in  request.form else 0,
        }

        # Convert input data to list for the model
        model_input = list(input_data.values())

        # Predict using the model
        prediction = model.predict([model_input])
        prediction_result = 'Positive' if prediction[0] == 1 else 'Negative'

        # Index data into Elasticsearch
        index_data(input_data, prediction_result)

        return render_template("index.html", prediction_result=prediction)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)