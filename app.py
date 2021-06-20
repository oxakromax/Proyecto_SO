import flask
from flask import Flask

app=flask.Flask(__name__)

app.config["DEBUG"]=True

@app.route('/',methods=['GET'])

def devoler():
    return "home: /"



@app.route('/elpepe/<nombre>')
def Esta_en_AD(nombre):
  #returns the username
  return {
      "response":f'Hola: {nombre} {2*2}'
  }





