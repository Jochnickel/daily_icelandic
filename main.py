print("running")
import requests
import json

preURL = "https://api.telegram.org/bot"
offsetFile = "offset.txt"
tokenFile = "token.txt"
dictFile = "dictionary.txt"
userFile = "userdata.txt"
logFile = "log.txt"
readBuff = 1000000

def read(path, len):
	try: fd = open(path,"r")
	except:	return None
	else:
		out = fd.read(len)
		fd.close()
		return out
def readjson(path):
	try: fd = open(path,'r')
	except: return
	else:
		out = fd.read()
		fd.close()
		return json.loads(out)

def write(path, s):
	fd = open(path,"w")
	fd.write(str(s))
	fd.close()
def writejson(path, j):
	fd = open(path,'w')
	json.dump(j,fd)
	fd.close()
def log(txt):
	fd = open(logFile,"a")
	fd.write(txt)
	fd.write("\n")
	fd.close()
def useridStr(userid):
	userid = str(userid)
	if None==users:
		log("useridStr: None==Users")
		return
	if not userid in users:
		log("useridStr: userid not in users")
		return
	return users[userid]
def getRandomVoc():
	if None==dict: return
	if 1>len(dict): return
	return random.choice(dict)

def sendMessage(chat_id, msg):
	requests.post("%s%s/sendMessage?chat_id=%s&text=%s"%(preURL,token,chat_id,msg))

def printVocable(userid):
	user = useridStr(userid)
	if not user: return
	vocab = getRandomVoc()
	if vocab:
		sendMessage(userid,"%s : %s"%(vocab[0],vocab[1]))
	else:
		sendMessage(userid,"no vocables learnt yet :(")

def addVocable(words,userid):
	if None==dict:
		log("addVocable: None==dict ")
		return
	user = useridStr(userid)
	if not user: return
	if 'administrator' in user:
		print("admin adding Voc")
	elif not 'votes' in user:
		sendMessage(userid,"vote 10 times first.")
		return
	elif 10>users[userid]['votes']:
		sendMessage(userid,"Get 10 votes. Having: %s"%(user['votes']))
		return
	if 2==len(words):
		dict[words[0]] = dict[words[0]] or {}
		dict[words[0]][words[1]] = dict[words[0]][words[1]] or {}
		dict[words[0]][words[1]][userid] = True
		sendMessage(userid,"thanks")
	else:
		sendMessage(userid,"didn't read 2 words ")
def rateVocable(userid):
	user = useridStr(userid)
	if not userid: return
	if None==dict:
		log("rateVocable None==dict")
		return
	if 'banned' in user:
		sendMessage(userid,"You can't vote anymore :(")
		return
	print(users)
	sendMessage(userid,"rate the vocble!")
def banUser(boss,victim,banBool):
	boss = useridStr(boss)
	if not boss: return
	if 'moderator' in boss:
		if not victim in users: users[victim] = {}
		if banBool:
			users[victim]['banned'] = banBool
		else:
			del users[victim]['banned']
	else:
		print("non mod tried to ban:%s"%(boss))
def modUser(boss,victim,modBool):
	boss = str(boss)
	if None==users:
		log("None==users: banUser(%s,%s)"%(boss,victim))
		return
	if not boss in users:
		log("modUser not boss %s in users"%(boss))
		return
	if 'administrator' in users[boss]:
		if not victim in users: users[victim] = {}
		if modBool:
			users[victim]['moderator'] = modBool
		else:
			del users[victim]['moderator']
	else:
		print("non admin tried to mod:%s"%(boss))


token = read(tokenFile,46)
offset = read(offsetFile,10) or 0
dict = readjson(dictFile)
print(dict)
users = readjson(userFile) or {'452549370' : {'administrator': 'True'}}

j = requests.get("%s%s/getUpdates?offset=%s"%(preURL,token,offset)).json()
if ('result' in j):
	for update in j['result']:
		message = ('message' in update) and update['message']
		if (message):
#			print(message)
			userid = update['message']['from']['id']
			if (not str(userid) in users):
				print("creating user %s"%(userid))
				users[userid] = {}
			if ('entities' in message):
				e = update['message']['entities'][0]
				o = e['offset']
				l = e['length']
				command = update['message']['text'][o:(o+l)]
				params = update['message']['text'][(o+l):].split()
				if '/vocable'==command:
					if 0==len(params): printVocable(userid)
					else: addVocable(params,userid)
				elif '/vote'==command:
					rateVocable(userid)
				elif '/ban'==command:
					for u in params:
						banUser(userid,u,True)
				elif '/unban'==command:
					for u in params:
						banUser(userid,u,False)
				elif '/mod'==command:
					for u in params:
						modUser(userid,u,True)
				elif '/unmod'==command:
					for u in params:
						modUser(userid,u,False)
				elif '/catvideo'==command:
					sendMessage(userid,"feature coming soon ;)")
				else:
					sendMessage(userid,"unknown command :(")
				print(userid,command,params)
			offset = update['update_id']+1

writejson(dictFile,dict)
writejson(userFile,users)

write(offsetFile,offset)

print("")
