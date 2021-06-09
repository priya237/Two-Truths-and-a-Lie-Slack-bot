import os
from aiohttp.client import request
from flask.wrappers import Response
import slack
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask,request, make_response,Response
from slackeventsapi import SlackEventAdapter
import json

from werkzeug.datastructures import ViewItems
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter=SlackEventAdapter(os.environ['SIGNNING_SECRET'],'/slack/events',app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
# global lie
#lie='yu'



@slack_event_adapter.on('member_joined_channel')
def welcome_message(payload):
    event=payload.get('event',{})
    channel_id=event.get('channel')
    user_id=event.get('user')
    client.chat_postEphemeral(channel="#test",user=user_id, text="Hey there,:wave:\n I noticed you joined #twotruth. I'm here to help your teammates get to know each other better by playing two truth and a lie. \n While you're here, you can help out by filling out your truth and lies :smile:\n\nWould you like to play game?",
			attachments=[{
			"text": "",
			"callback_id":"coffee_order_form",
			"color": "#3AA3E3",
			"attachment_type": "default",
			"actions": [{
				"name": "coffee_order",
				"text": "Add My Truth And Lie",
				"type": "button",
				"value": "Add My Truth And Lie",
				"action_id": "actionId-0"
			},{
				"name": "coffee_order",
				"text": "No Thanks",
				"type": "button",
				"value": "No Thanks",
				"action_id": "actionId-1"
			}]
			}])
    print(payload)
	
		
def broadcast(payload):
	if payload["type"]== "view_submission" and payload["view"]["callback_id"] == "coffee_order_form":
		userid=payload["user"]["name"]
		print("user id is", userid)
		payload1=payload["view"]["state"]["values"]
		truth1= payload1["truth_lie1"]["First_truth"]["value"]
		truth2= payload1["truth_lie2"]["Second_truth"]["value"]
		lie= payload1["truth_lie3"]["Lie"]["value"]
		print("Printing Truth 1" ,truth1)
		client.chat_postMessage(channel='#test',text="Hello everyone :wave: \n Today @"+userid+", a new member joined our group so",
			attachments=[{
			"text" :"Which do you think is @"+userid+" lie?\n:one: "+truth1+"\n:two: "+truth2+"\n :three: "+lie,
			"callback_id":"response_from_user",
			"color": "#3AA3E3",
			"attachment_type": "default",
			"actions": [{
				"name": "coffee_order",
				"text": "1",
				"type": "button",
				"value": "1",
				"action_id": "actionId-0"
			},{
				"name": "coffee_order",
				"text": "2",
				"type": "button",
				"value": "2",
				"action_id": "actionId-1"
			},{
				"name": "coffee_order",
				"text": "3",
				"type": "button",
				"value": "3",
				"action_id": "actionId-1"
			}]
			}]
			)
		
		
		return make_response("", 200)



def response_to_user(payload):
	if payload["type"]== "view_submission" and payload["view"]["callback_id"] == "coffee_order_form":
		payload1=payload["view"]["state"]["values"]
		global lie
		lie= payload1["truth_lie3"]["Lie"]["value"]

	print("in second loop\n\n\n ",lie)
	if payload['type'] == "interactive_message" and payload['callback_id'] == 'response_from_user':
		print(payload)
		user_idr=payload['user']['id']
		print(user_idr)
		if payload['actions'][0]['value'] == '3':
			client.chat_postEphemeral(channel="#test",user=user_idr, text='Yes you are correct, the lie is '+lie+" \n :shushing_face:\nPlease don't tell these to other member let them guess")
		else:
			client.chat_postEphemeral(channel="#test",user=user_idr, text='Sorry You are wrong, the lie is '+lie+" \n :shushing_face:\nPlease don't tell these to other member let them guess")
	return make_response("", 200)

		

@app.route('/slack/truth_and_lie', methods=['POST'])
def truth_and_lie():

	payload = json.loads(request.form['payload'])
	#print(payload)
	#user_id = truth_and_lie['user']['id']
	if payload['type'] == "interactive_message" and payload['actions'][0]['value'] == 'Add My Truth And Lie':
		
		client.views_open(
			trigger_id = payload['trigger_id'],
			view = {
				"type": "modal",
				"callback_id":"coffee_order_form",
				"title": {
					"type": "plain_text",
					"text": "Two Truth and Lie",
					"emoji": True
				},
				"submit": {
					"type": "plain_text",
					"text": "Submit",
					"emoji": True
				},
				"close": {
					"type": "plain_text",
					"text": "Cancel",
					"emoji": True
				},
				"blocks": [
					{
						"type": "input",
						"block_id":"truth_lie1",
						"element": {
							"type": "plain_text_input",
							"action_id": "First_truth"
						},
						"label": {
							"type": "plain_text",
							"text": "First Truth",
							"emoji": True
						}
					},
					{
						"type": "input",
						"block_id":"truth_lie2",
						"element": {
							"type": "plain_text_input",
							"action_id": "Second_truth"
						},
						"label": {
							"type": "plain_text",
							"text": "Second Truth",
							"emoji": True
						}
					},
					{
						"type": "input",
						"block_id":"truth_lie3",
						"element": {
							"type": "plain_text_input",
							"action_id": "Lie"
						},
						"label": {
							"type": "plain_text",
							"text": "Lie",
							"emoji": True
						}
					}
				]
			}
		)
		return make_response("", 200)
	elif payload['type'] == "interactive_message" and payload['actions'][0]['value'] == 'No Thanks' :
		user_id=payload['user']['id']
		channel_id= payload['channel']['id']
		client.chat_postEphemeral(channel=channel_id,user=user_id,text="Okay! Have a nice Journey ahead.")
	if payload["type"]== "view_submission" and payload["view"]["callback_id"] == "coffee_order_form":
		payload1=payload["view"]["state"]["values"]
		global lie
		lie= payload1["truth_lie3"]["Lie"]["value"]

	broadcast(payload)
	print(lie)
	response_to_user(payload)

	return make_response("", 200)	
if __name__=="__main__":
    app.run("localhost",3000)
