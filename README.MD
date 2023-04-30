# Requirements
- docker compose, for MongoDB
- requirements.txt

# Instructions
1. Build your attack inside the text_attack module; 
you only need to modify the exploit function.
You can use the decorator @local_test for localhost
or @nop_test to attack the nop_team. Please avoid 
using _db functions.
2. When everything is working, make sure to only keep
the necessary log.info and remove all print. Consider
switching them to log.debug. Edit every function printing to stdout
so that it is surrounded by l.acquire() and l.release().
Copy your exploit() and all auxiliary functions in a new file inside config/exploits.
Give it a meaningful name and make sure the file and the exploit function 
have the same name. Take a look at config/exploits/example.py for a reference of the imports
3. Done! if deploy.py is already running it will automatically reload all exploits in the next
tick, so you don't need to do anything else.