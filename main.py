print("running")
import requests
import json
import random
import time

preURL = "https://api.telegram.org/bot"
offsetFile = "offset.txt"
tokenFile = "token.txt"
dictFile = "dictionary.txt"
userFile = "userdata.txt"
logFile = "log.txt"
welcomeMessage = "Welcome! start with /vocable and /interval, stop interval with /stop, unregister with /unsubscribe"
admin = '452549370'

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
	return random.choice(list(dict))

def sendMessage(chat_id, msg):
	requests.post("%s%s/sendMessage?chat_id=%s&text=%s"%(preURL,token,chat_id,msg))

def printVocable(userid):
	user = useridStr(userid)
	if not user: return
	vocab = getRandomVoc()
	if vocab:
		user['last1'] = vocab
		v2 = next(iter(dict[vocab]))
		user['last2'] = v2
		user['lasttime'] = time.time()
		sendMessage(userid,"%s : %s"%(vocab,v2))
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
	elif 'banned' in user:
		sendMessage(userid,"u are banned from adding")
		return
	elif time.time()<1587933347.5322053:
		print("testing time")
	elif not 'votes' in user:
		sendMessage(userid,"vote 10 times first.")
		return
	elif 10>users[userid]['votes']:
		sendMessage(userid,"Get 10 votes. Having: %s"%(user['votes']))
		return
	if 2==len(words):
		if not words[0] in dict: dict[words[0]] = {}
		if not words[1] in dict[words[0]]: dict[words[0]][words[1]] = {}
		dict[words[0]][words[1]][userid] = "creator"
		dict[words[0]][words[1]]['good'] = 0
		dict[words[0]][words[1]]['bad'] = 0
		sendMessage(userid,"thanks")
	else:
		sendMessage(userid,"didn't read 2 words ")
def rateVocable(userid,vote):
	user = useridStr(userid)
	if not user: return
	if not 'last1' in user:
		sendMessage(userid,"Didn't find your last vocable :(")
		return
	if 'good'!=vote and 'bad'!=vote:
		sendMessage(userid,"please vote good or bad")
		return
	if None==dict:
		log("rateVocable None==dict")
		return
	if not user['last1'] in dict: return
	if 'banned' in user:
		sendMessage(userid,"You can't vote anymore :(")
		return
	vocab = dict[user['last1']][user['last2']]
	if str(userid) in vocab:
		sendMessage(userid,"already voted")
		return
	vocab[userid] = vote
	if 'good'==vote:
		print(vocab)
		vocab['good'] = (vocab['good'] or 0) +1
	elif 'bad'==vote:
		vocab['bad'] = (vocab['bad'] or 0) +1
		badVotes = vocab['bad']
		if badVotes>20 and badVotes>vocab['good']:
			for u in vocab:
				if 'creator' in u:
					strikeUser(u)
			del vocab
	if 'votes' in user:
		users[userid]['votes'] += 1
	else:
		users[userid]['votes'] = 1
	sendMessage(userid,"thanks for the rating!")


def strikeUser(userid):
	user = useridStr(userid)
	if not user: return
	if 'strike' in user:
		user['banned'] = True
		del user['strike']
	sendMessage(u,"you received a strike.")

def banUser(boss,victim,banBool):
#	if not userid in users: return
	boss = useridStr(boss)
	if not boss: return
	if 'moderator' in boss:
		if not victim in users: users[victim] = {}
		if banBool:
			users[victim]['banned'] = banBool
			sendMessage(victim,"You have been restricted for some reason. Write /supp help for help")
		else:
			del users[victim]['banned']
			sendMessage(victim,"Your account is normal again")
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
			sendMessage(victim,"You are now a moderator, you can use /ban 123 and /unban 123, knowing the telegram_id of a person")
		else:
			del users[victim]['moderator']
	else:
		print("non admin tried to mod:%s"%(boss))
def setInterval(userid,int):
	int = float(int)
	if not int: int = 1
	intSec = int*86400
	user = useridStr(userid)
	if not user: return
	user['interval'] = intSec
	sendMessage(userid,"interval set to %s days"%(int))

def newUser(userid):
	userid = str(userid)
	if userid in users: return
	users[userid] = {'subscribed' : True}
	sendMessage(userid,welcomeMessage)

def delUser(userid):
	userid = str(userid)
	if userid in users:
		if 'banned' in users[userid]:
			userid[users] = {'banned' : True}
		else:
			del users[userid]
		sendMessage(userid,"You unsubsribed!")

def setCronInterval(userid,int):
	user = useridStr(userid)
	if not user: return
	if not 'administrator' in user: return
	write('background.sh','while true; do python3 main.py; sleep %s; done'%(int))
	sendMessage(userid,"Cron interval set to %s"%(int))
def adminMessage(userid,who,msg):
	user = useridStr(userid)
	if not user: return
	if not 'administrator' in user: return
	to = {str(who) : {'subscribed': True}}
	print(to)
	if 'all'==who: to = users
	for u in to:
		if 'subscribed' in to[u]:
			sendMessage(u,msg)

token = read(tokenFile,46)
offset = read(offsetFile,10) or 0
dict = readjson(dictFile)
users = readjson(userFile)
if not dict: sendMessage(admin,"dict kaputt")
if not users: sendMessage(admin,"users kaputt")

j = requests.get("%s%s/getUpdates?offset=%s"%(preURL,token,offset)).json()
if ('result' in j):
	for update in j['result']:
		message = ('message' in update) and update['message']
		if (message):
#			print(message)
			userid = update['message']['from']['id']
			newUser(userid)
			if ('entities' in message):
				e = update['message']['entities'][0]
				o = e['offset']
				l = e['length']
				command = update['message']['text'][o:(o+l)]
				paramText = update['message']['text'][(o+l):]
				params = paramText.split()
				if '/vocable'==command:
					if 0==len(params): printVocable(userid)
					else: addVocable(params,userid)
				elif '/vote_good'==command:
					rateVocable(userid, 'good')
				elif '/vote_bad'==command:
					rateVocable(userid, 'bad')
				elif '/interval'==command:
					setInterval(userid, params and params[0] or 1)
				elif '/stop'==command:
					setInterval(userid, -1)
				elif '/unsubscribe'==command:
					delUser(userid)
				elif '/size'==command:
					sendMessage(userid,"We have collected %s words"%(len(dict)))
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
				elif '/cron'==command:
					setCronInterval(userid,params and params[0] or 30)
				elif '/msg'==command:
					if 2==len(params): adminMessage(userid,params[0],params[1])
				elif '/supp'==command:
					sendMessage(admin,"%s needs help: %s"%(userid,paramText))
				else:
					sendMessage(userid,"unknown command :(")
				print(userid,command,params)
			else:
				print(message)
		elif 'inline_query' in update:
			print(update['inline_query'])
			iq_id = update['inline_query']['id']
			voc = getRandomVoc()
			print(iq_id,voc)
			if voc:
				vocStr = "%s : %s"%(voc,next(iter(dict[voc])))
				print(vocStr)
				res = {'type':'article','id':str(int(iq_id)%1000000),'title':voc,'input_message_content':{'message_text':vocStr}}
				print(requests.post("%s%s/answerInlineQuery?inline_query_id=%s&results=%s"%(preURL,token,iq_id,json.dumps([res]))).json())
		else:
			print(update)
		offset = update['update_id']+1

for u in users:
	if 'interval' in users[u]:
		if users[u]['interval']>0:
			if not 'lasttime' in users[u]: users[u]['lasttime'] = 0
			if users[u]['lasttime']+users[u]['interval']<time.time():
				printVocable(u)

writejson(dictFile,dict)
writejson(userFile,users)

write(offsetFile,offset)
