print("running")
import requests
import json

preURL = "https://api.telegram.org/bot"
offsetFile = "offset.txt"
tokenFile = "token.txt"
dictFile = "dictionary.txt"
userFile = "userdata.txt"

def read(path, len):
	try: fd = open(path,"r")
	except:	return None
	else:
		out = fd.read(len)
		fd.close()
		return out

def write(path, s):
	fd = open(path,"w")
	fd.write(str(s))
	fd.close()
def writejson(path, j):
	fd = open(path,'w')
	json.dump(j,fd)
	fd.close()

token = read(tokenFile,46)
offset = read(offsetFile,10) or 0
dict = json.loads(read(dictFile,100000) or "{}")
asd = requests.get("%s%s/getUpdates?offset=%s"%(preURL,token,offset))
for update in asd.json()['result']:
#	print(update)
	message = ('message' in update) and update['message']
#	print(message)
	if (message and 'entities' in message):
		userid = update['message']['from']['id']
		e = update['message']['entities'][0]
		o = e['offset']
		l = e['length']
		command = update['message']['text'][o:(o+l)]
		params = update['message']['text'][(o+l):]
		requests.get("%s%s/sendMessage?chat_id=%s&text=cooool"%(preURL,token,userid))
		print(userid,command,params)
	offset = update['update_id']+1
writejson(dictFile,dict)
write(offsetFile,offset)
print("")
