Contains APIs for starting a drip campaign. User can sign in from their gmail account.

1. Install redis : sudo apt-get install redis-server
2. Install all the dependencies : pip install -r requirements.txt
3. For storing users token : http://localhost:5000/authorize?email=john_doe@gmail.com
4. Curl request to schedule a campaign:

	recipients : list of recipients to send the email to
	
	camp_title : campaign title
	
	templates : User defined templates
	
	vars : values which will be replaces for each matching template
	
	wait_days : days gap between each follow up mail
	
	stages : number of follow up emails
	
	email: User's email

	curl -X POST \
	  http://localhost:5000/schedule_campaign \
	  -H 'Cache-Control: no-cache' \
	  -H 'Content-Type: application/json' \
	  -H 'Postman-Token: fa8390a1-0c01-f2a5-ecdd-dbc5df945e3c' \
	  -d '{
	  "recipients" : ["recipent1@gmail.com","recipent2@gmail.com"],
	  "camp_title" : "3 discount",
	  "templates":["There is a discount %FIRSTNAME% %LASTNAME%.","There is a discount.",
	  "There is no discount.","There is a discount.","There is a discount."],
	  "temp_vars": [{"%FIRSTNAME%":"John","%LASTNAME%":"Doe"},{},{},{},{}],
	  "wait_days" : 10,
	  "stages" : 5,
	  "email":"john_doe@gmail.com"
	}'
