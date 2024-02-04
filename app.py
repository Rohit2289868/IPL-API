from flask import Flask, jsonify, request
import ipl

app = Flask(__name__)

@app.route('/')
def home():
    return "Home Page"

@app.route('/api/teams')
def teams():
    response = ipl.allTeamsAPI()
    return jsonify(response)

@app.route('/api/teamvsteam')
def teamvsteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    response = ipl.teamVSteamAPI(team1, team2)
    return jsonify(response)

@app.route('/api/team-record')
def teamRecord():
    team = request.args.get('team')
    response = ipl.teamAPI(team)
    return jsonify(response)

@app.route('/api/batter')
def batter():
    response = ipl.batterListAPI()
    return jsonify(response)

@app.route('/api/bowler')
def bowler():
    response = ipl.bowlerListAPI()
    return jsonify(response)

@app.route('/api/batsman-record')
def batsmanRecord():
    batsman_name = request.args.get('name')
    response = ipl.batsmanAPI(batsman_name)
    return jsonify(response)

@app.route('/api/bowler-record')
def bowlerRecord():
    bowler_name = request.args.get('name')
    response = ipl.bowlerAPI(bowler_name)
    return jsonify(response)

app.run(debug=True)