import praw #reddit
import pyowm #informaciono meteorologica
import random
import time
import datetime
import traceback #para logear los errores
import login #informacion personal para log in del bot

def update_log(id, log_path): #para los comentarios que ya respondi
	with open(log_path, 'a') as myLog:
		myLog.write(id + "\n")

def load_log(log_path): #para los comentarios que ya respondi
	with open(log_path) as myLog:
		log = myLog.readlines()
		log = [x.strip('\n') for x in log]
		return log

def output_log(text): #lo uso para ver el output del bot
	output_log_path = "/home/pi/Downloads/lluviaBot/output_log.txt"
	with open(output_log_path, 'a') as myLog:
		s = "[" +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
		s = s + text +  "\n"
		myLog.write(s)

def check_condition(c): #llamaron al bot?
	text = c.body
	if "!talloViendo" in text:
		return True

def check_rain(): #llueve en Montevideo?
	observation = owm.weather_at_place("Montevideo,UY")
	w = observation.get_weather()
	status = w.get_status()
	output_log('Status: ' + status)
	if status  == 'Rain':
		return True

def get_reply_llueve():
	replies = [	"[Tallo Viendo gurisxs!](https://pbs.twimg.com/media/ChydlIsUYAALxhj.jpg)",
				"[Con tortas fritas cantare bajo la lluvia!](https://youtu.be/PIYiK1Qnbjc?t=59)",
				"[Metan la ropa burise!](https://ak4.picdn.net/shutterstock/videos/732994/thumb/8.jpg)"
				"[Los agentes de campo me confirmaron la lluvia.](http://jp6.r0tt.com/l_1e51ec40-cfc9-11e1-b4fb-039dd9a00006.jpg)",
				"[La lluvia cae sobre Montevideo.](https://www.youtube.com/watch?v=eWJmdiiTdR0)  \nHoy como ayer.  \nnaranana **ESPECIAL**",
				"[Rain rain rain.](https://www.youtube.com/watch?v=N8jwzaidy7c)",
				"[Llueve.](https://www.youtube.com/watch?v=RwAHQEaQ4BY).  \nAgonia de que no te tengo\n  Y cada gota representa un beso.\n  Los que me dabas en esos momentos.",
				"[Vean el agua](https://youtu.be/-UI3i8cN8Wc?t=10)",
				"Queridos amigos, cada vez llueve mas y mas en la ciudad de Montevideo. Es un diluvio, **UN DILUVIO**. Las calles estan inundandose. La gente anda con dos paraguas. Hay personas que tienen cuatro paraguas en vez de un paraguas. [Ahora les voy a mostrar.](https://youtu.be/MySumLLNYTc)"
				]
	return random.choice(replies)

def get_reply_no_llueve():
	replies = [ "Por que me despertas si no llueve? Te hice algo?",
				"No llueve. Gracias por ilusionarme, che. Muy productiva esta sesion.",
				"No seas malo, mira por la ventana. A vos te parece que llueve?",
				"Basta chicos! Todos sabemos que no llueve!",
				"Bueno, tenemos un gracioso aca. No, nene, no llueve.",
				"[Estoy durmiendo, no jodas. Molestalos a ellos, no a mi.](https://inumet.gub.uy/)",
				"Sali a la calle y decime vos. Ugh!",
				"Esta lloviendo.^/s \n\nJodete por creerle a un bot",
				]
	return random.choice(replies)

if __name__ == "__main__":
	comment_log_path = "/home/pi/Downloads/lluviaBot/log.txt"
	while True:
		try:
			output_log("Comenzando el script")
			log = load_log(comment_log_path)
			reddit = praw.Reddit(	client_id = login.client_id,
									client_secret = login.client_secret,
									password = login.password,
									user_agent = "tescript for /u/talloViendoBot",
									username = login.username)
			output_log("Login to reddit as: " + reddit.user.me().name)
			owm = pyowm.OWM(login.owm_key)

			for comment in reddit.subreddit('uruguay+test').stream.comments():
				if check_condition(comment) and comment.id not in log:
					body_ascii = unicodedata.normalize('NFKD', comment.body).encode('ascii', 'ignore') #esto porque me daba pila de problemas los comentarios unicode 
					output_log("{" + body_ascii + "}")
					if check_rain():
						reply = get_reply_llueve()
					else:
						reply = get_reply_no_llueve()
					s = "\n\n*****\n\n *Por ahora solo funciono en Montevideo, no sean crueles.*"
					comment.reply(reply + s)
					output_log("{" +  reply + "}")
					log.append(comment.id)
					update_log(comment.id, comment_log_path)
					#time.sleep(10 * 60)
		except Exception as exception:
			output_log(str(exception))
			output_log(traceback.format_exc())
