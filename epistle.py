from email.parser import HeaderParser
import facebooksdk, sqlite3, gobject, getpass, imaplib, smtplib, tweepy, webkit, email, gtk, sys, os

def gmail():
	''' Collect data for Gmail.'''
	gmailuser = raw_input('What is your email username? ')
	password = getpass.getpass('What is your email password? ')
	returned = {'gmailuser':gmailuser, 'password':password}
	return returned

def twitter():
	''' Collect data for Twitter.'''
	auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth_url = auth.get_authorization_url()
	print 'Please authorize: ', auth_url
	pin = raw_input('PIN: ')
	auth.get_access_token(pin)
	#print 'access_key = ', auth.access_token.key
	#print 'access_secret = ', auth.access_token.secret
	return auth

def facebook():
	'''Collect data for Facebook.'''
	pass

class Database:
	''' Checks for existing database and if one does not exist creates the database. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def check(self):
		if sys.platform == 'win32':
			self.checkdb = os.path.exists('C:/Users/' + os.getenv('USERNAME') + '/AppData/Local/epistle.db')
			self.db = sqlite3.connect('C:/Users/' + os.getenv('USERNAME') + '/AppData/Local/epistle.db')
			self.database = self.db.cursor()
		else:
			self.checkdb = os.path.exists('/home/' + os.environ['USER'] + '/.local/share/epistle.db')
			self.db = sqlite3.connect('/home/' + os.environ['USER'] + '/.local/share/epistle.db')
			self.database = self.db.cursor()
		if self.checkdb == False:
			self.Gmail = gmail()
			self.Twitter = twitter()
			#self.Facebook = facebook()
			self.setup()
	def read(self):
		self.database.execute('select * from auth')
		self.Objects = self.database.fetchall()
		self.Gmail = self.Objects[0:1]
		self.Twitter = self.Objects[1:2]
		#self.Facebook = self.Objects[3]
		
		self.database.execute('select * from mail')
		self.Mail = self.database.fetchall()

	def setup(self):
		self.database.execute('''create table auth (main)''')
		self.database.execute('insert into auth (main) values (?)', [self.Gmail['gmailuser']])
		self.database.execute('insert into auth (main) values (?)', [self.Gmail['password']])
		self.database.execute('insert into auth (main) values (?)', [self.Twitter.access_token.key])
		self.database.execute('insert into auth (main) values (?)', [self.Twitter.access_token.secret])
		#self.database.execute('insert into auth (main) values (?)', [self.Facebook])
		
		self.database.execute('''create table mail (main)''')
		self.db.commit()
		self.db.close()


class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def gmail(self):
		''' This function logs the user into their Gmail account. '''
		self.Gmail = gmail()
		return self.Gmail
		
	def twitter(self):
		''' This function logs the user into their Twitter account. '''
		self.Twitter = twitter()
		return self.Twitter

	def facebook(self):
		''' This function logs the user into their Facebook account. '''
		self.Facebook = facebook()
		return self.Facebook

class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		
		gobject.threads_init()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_resizable(False)
		self.window.set_title('Epistle')
		self.window.set_size_request(700, 450)
		self.window.connect('delete_event', self.delete_event)
		self.window.connect('destroy', self.destroy)
		self.window.set_border_width(0)
		self.toolbar = gtk.Toolbar()
		
		#self.refresh_button = gtk.ToolButton(gtk.STOCK_REFRESH)
		#self.refresh_button.connect("clicked", self.refresh)
		
		self.gmail_tab = gtk.Button('Gmail')
		self.gmail_tab.connect('clicked', self.showmail)
		
		self.tweet_tab = gtk.Button('Twitter')
		self.tweet_tab.connect('clicked', self.showtwitter)

	        #self.toolbar.add(self.refresh_button)
		self.toolbar.add(self.gmail_tab)
		self.toolbar.add(self.tweet_tab)
		self.toolbar.set_size_request(700,30)
		#self.search = gtk.Entry()
		#self.search.connect("activate", self.searchdb)

		self.buffer = gtk.TextBuffer()
		self.html = webkit.WebView()
		self.scroll_window = gtk.ScrolledWindow(None, None)
		self.scroll_window.add(self.html)
		
		vbox = gtk.VBox(False, 0)
		hbox = gtk.HBox(False, 0)
		vbox.pack_start(hbox, expand=False, fill=False, padding=0)
		#Edit the interface to how you like it
		hbox.pack_start(self.toolbar, expand=False, fill=False, padding=0)
		#hbox.pack_start(self.search, expand=True, fill=True, padding=0)
		vbox.add(self.scroll_window)
		self.window.add(vbox)
		self.window.show_all()
		
	def delete_event(self, widget, data=None):
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()


	def readmail(self):
		''' This function reads unread messages from Gmail. '''
		self.Gmail = Account().gmail()
		self.Gmail['imap'] = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		self.Gmail['imap'].login(self.Gmail['gmailuser'], self.Gmail['password'])

		label,inbox = self.Gmail['imap'].select('Inbox')
		inbox = int(inbox[0])
		
		unread = len(self.Gmail['imap'].search('Inbox', '(UNSEEN)')[1][0].split())
		print unread
		
		for x in range(((inbox - unread)),inbox):
			resp, data = self.Gmail['imap'].FETCH(x, '(RFC822)')
			mailitem = email.message_from_string(data[0][1])
			message = HeaderParser().parsestr(data[0][1])
			#print '\n\n'
			#print 'From: ', message['From']
			#print 'To: ', message['To']
			#print 'Subject: ', message['Subject'], '\n\n'
			self.gmailmessage = {}
			self.gmailmessage['From'] = message['From']
			self.gmailmessage['To'] = message['To']
			self.gmailmessage['Subject'] = message['Subject']

			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue	
				message = mailpart.get_payload()
				self.gmailmessage['Body'] = message
				break
		self.Gmail['imap'].logout()

	def sendmail(self):
		self.Gmail = Account().gmail()
		''' This function sends an email using Gmail. '''
		self.Gmail['smtp'] = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		self.Gmail['smtp'].login(self.Gmail['gmailuser'], self.Gmail['password'])
		to = raw_input('To: ')
		subject = raw_input('Subject: ')
		mailmessage = raw_input('Message: ')
		self.Gmail['smtp'].sendmail(self.Gmail['gmailuser'], to, 'Subject: ' + subject + '\n' +mailmessage)
		self.Gmail['smtp'].quit()
	
	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		self.Twitter = Account().twitter()
		self.Twitter['Twitter'] = tweepy.API(self.Twitter['auth'])
		self.twitterupdate = self.Twitter['Twitter'].home_timeline()

	def posttwitter(self):
		''' This function posts a Tweet. '''
		self.Twitter = Account().twitter()
		self.Twitter['Twitter'] = tweepy.API(self.Twitter['auth'])
		tweet = raw_input('Update Twitter: ')
		if len(tweet) >= 140:
			while (len(tweet) >= 140):
				print('The character limit of 140 was exceeded.')
				tweet = raw_input('Update Twitter: ')
		self.Twitter['Twitter'].update_status(tweet)

	def updatefb(self):
		''' This function updates the Facebook stream. '''
		self.Facebook = Account().facebook()
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		pass

	def postfb(self):
		''' This function posts to Facebook. '''
		self.Facebook = Account().facebook()
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		fbstatus = raw_input('Set your Facebook status: ')
		self.Facebook['Facebook'].put_object('me', 'feed', message=fbstatus)


	def showmail(self, widget):
		''' This function displays email messages. '''
		self.readmail()
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('<', '&lt;')
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('>', '&gt;')
		self.gmailmessage['Body'] = self.gmailmessage['Body'].replace('\n', '<br />')
		self.html.load_html_string('<p>Subject: ' + self.gmailmessage['Subject'] + '</p><p>From: ' + self.gmailmessage['From'] + '</p><hr />' + self.gmailmessage['Body'], 'file:///')

	def showtwitter(self, widget):
		''' This function displays the user's Twitter home timeline. '''
		self.updatetwitter()
		self.tweets = ''
		for x in range(0, 19):
			self.tweets = self.tweets + '<p><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img><b>' + self.twitterupdate[x].user.screen_name + '</b>: ' + self.twitterupdate[x].text + '</p><hr />'
		self.html.load_html_string(self.tweets, 'file:///')

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		gtk.main()

#if __name__ == '__main__':
#	app = Epistle()
#	app.main()
Database().check()