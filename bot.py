import praw #reddit
import pyowm #informaciono meteorologica
import random
import time
import datetime
import traceback #para logear los errores
import unicodedata
import login #informacion personal para log in del bot

def update_log(id, log_path): #para los comentarios que ya respondi
	with open(log_path, 'a') as my_log:
		my_log.write(id + "\n")

def load_log(log_path): #para los comentarios que ya respondi
	with open(log_path) as my_log:
		log = my_log.readlines()
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
	if "!talloviendo" in text.lower():
		return True

def get_temperature(w):
	temp_dict = w.get_temperature(unit="celsius")
	output_log('Temperature: ' + str(temp_dict))
	return temp_dict["temp"]

def get_reply_rain():
	replies = [	"[Tallo Viendo gurisxs!](https://pbs.twimg.com/media/ChydlIsUYAALxhj.jpg)",
				"[Con tortas fritas cantare bajo la lluvia!](https://youtu.be/PIYiK1Qnbjc?t=59)",
				"[Metan la ropa burise!](https://ak4.picdn.net/shutterstock/videos/732994/thumb/8.jpg)"
				"[Los agentes de campo me confirmaron la lluvia.](http://jp6.r0tt.com/l_1e51ec40-cfc9-11e1-b4fb-039dd9a00006.jpg)",
				"[La lluvia cae sobre Montevideo.](https://www.youtube.com/watch?v=eWJmdiiTdR0)  \nHoy como ayer.  \nnaranana **ESPECIAL**",
				"[Rain rain rain.](https://www.youtube.com/watch?v=N8jwzaidy7c)",
				"[Llueve.](https://www.youtube.com/watch?v=RwAHQEaQ4BY).  \nAgonia de que no te tengo\n  Y cada gota representa un beso.\n  Los que me dabas en esos momentos.",
				"[Vean el agua](https://youtu.be/-UI3i8cN8Wc?t=10)",
				"Queridos amigos, cada vez llueve mas y mas en la ciudad de Montevideo. Es un diluvio, **UN DILUVIO**. Las calles estan inundandose. La gente anda con dos paraguas. Hay personas que tienen cuatro paraguas en vez de un paraguas. [Ahora les voy a mostrar.](https://youtu.be/MySumLLNYTc)",
				"[Y no para de lloveeer.](https://youtu.be/c91jxN3MV-w?t=90)",
				"[Mirando como llueve el dia pasa lento.](https://youtu.be/yTiCMxNcCkw?t=43)",
				"[Se recomienda salir con paraguas.](http://images.teinteresa.es/mundo/Tormenta-Montevideo-Uruguay_TINIMA20120922_0044_5.jpg)"
				]
	return random.choice(replies)

def get_reply_drizzle():
	replies = [	"Montevideo gris, [llovizna](https://youtu.be/TsRhkwPFxmQ?t=20).",
				"[Llovizna, tranqui.](https://pbs.twimg.com/media/CrggaLdWIAAwcX7.jpg)"
				"Estamos mas o menos [asi](http://static.panoramio.com/photos/large/79137766.jpg)."
				]
	return random.choice(replies)

def get_reply_thunderstorm():
	replies = [	"[Asi estamos](https://www.youtube.com/watch?v=eGj9MozpV1I)",
				"[Bo, la tormenta ya esta arriba](https://www.youtube.com/watch?v=zGljp1TMhg0)",
				"[Esto](https://media.elobservador.com.uy/adjuntos/181/imagenes/000/869/0000869009.jpg) es porque el  cerro quiso separarse.",
				"[En cualquier rato le cae un rayo a presidencia.](https://ugc.kn3.net/i/origin/http://www.lr21.com.uy/wp-content/uploads/2012/02/RayosMontevideoAFP1.jpg)"
				]
	return random.choice(replies)

def get_reply_no_rain(temp):
	replies = [ "Por que me despertas si no llueve? Te hice algo?",
				"No llueve. Gracias por ilusionarme, che. Muy productiva esta sesion.",
				"No seas malo, mira por la ventana. A vos te parece que llueve?",
				"Basta chicos! Todos sabemos que no llueve!",
				"Bueno, tenemos un gracioso aca. No, nene, no llueve.",
				"[Estoy durmiendo, no jodas. Molestalos a ellos, no a mi.](https://inumet.gub.uy/)",
				"Sali a la calle y decime vos. Ugh!",
				"Esta lloviendo.^/s \n\nJodete por creerle a un bot",
				"[No hay agua!](https://www.youtube.com/watch?v=ngVwade2hII)",
				"[HispanTV no pierde vigencia.](https://youtu.be/BUT9MPb_QNE)"
				]
	replies_hot = [	"Con el calor que hace ojala lloviera. " + '%.1f' %temp + "C! A vos te parece!"
					]
	if temp >= 26:
		replies = replies + replies_hot
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
					output_log("{" + unicodedata.normalize('NFKD', comment.body).encode('ascii', 'ignore') + "}") #esto porque me daba pila de problemas los comentarios unicode
					observation = owm.weather_at_place("Montevideo,UY")
					w = observation.get_weather()
					status = w.get_status()
					output_log('Status: ' + status)
					if status == 'Rain':
						reply = get_reply_rain()
					elif status == 'Thunderstorm':
						reply = get_reply_thunderstorm()
					elif status == 'Drizzle':
						reply = get_reply_drizzle()
					else:
						reply = get_reply_no_rain(get_temperature(w))
					s = "\n\n*****"
					s = s + "\n\n *Solo funciono en Montevideo, no sean crueles.*"
					s = s + "\n\n [Source.](https://github.com/dirkgentle/talloViendoBot)"
					comment.reply(reply + s)
					output_log("{" +  reply + "}")
					log.append(comment.id)
					update_log(comment.id, comment_log_path)
		except Exception as exception:
			output_log(str(exception))
			output_log(traceback.format_exc())
