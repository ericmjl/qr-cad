# Creating QR Codes with Flask

In the first two parts of this blog series, I showed you how to (1) create WiFi access QR codes programmatically with Python, and 3D print them, and (2) design and build a command-line interface (CLI) program that will let you make QR codes by typing a few prompts at the terminal.

In this blog post, I'd like to show you how to build a web app that creates QR codes from WiFi information that an end-user can input. Having built this app, you will hopefully come to the same realization as I did: command line apps and web apps are just text-based endpoints to arbitrary Python code.

## Structuring a Flask App

To build a Flask app, you need the following minimal directory structure:

```
project
├── templates
└── app.py
```

In `app.py`, we write our Flask app. In the `templates/` directory, we store the HTML templates that our Flask app will use to display to the end user.

In our previous blog post, we had the following structure:

```
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   ├── functions.py
│   └── templates
│       ├── index.html.j2
│       ├── qr.html.j2
│       └── template.html.j2
└── setup.py
```

We already have a `functions.py` file that we can take advantage of that little bit of engineering that we did earlier on, and use that to help us build our Flask app.

Following the previous blog post's convention, whenever I will be talking about a particular file, I will place asterisks on those files/directories.

## Building the Flask App

Let's start with `app.py`. As with the previous post, I'll build your intuition bit-by-bit, and then I'll put together a final copy/pastable segment of code that you can run.

```
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── app.py **
│   ├── cli.py
│   ├── functions.py
│   └── templates
│       ├── index.html.j2
│       ├── qr.html.j2
│       └── template.html.j2
└── setup.py
```

```python
from flask import Flask, render_template, request

from qrwifi.functions import wifi_qr


app = Flask(__name__)
```

The first line of imports contain the most commonly-used set of Flask objects and functions that we will be using. The second line of imports lets us import the `wifi_qr` function from our `qrwifi.functions` module, which itself is installable. Finally, the third line lets us create a Flask object, to which we assign it the variable name `app`.

Once this basic infrastructure is in place, we can get to work defining what Flask calls "view functions".

### View Functions

The way to think about view functions is that they are the functions that are called when you type a URL into your browser. Let's see an example of this:

```python
@app.route("/")
def home():
    return render_template("index.html.j2")
```

Here, we've defined the `home()` function, which is called when we enter the routing string after our hostname in the URL bar of our browser. That sounded like much jargon, so let me unpack that.

### Routing string?

If you go to your browser and type the following URL:

```
http://kite.com/blog
```

you will be brought to the Kite blog. `kite.com` is the string that points us to the server that is hosting the blog, and `/blog` is the routing string that tells us where to go. Together, they form the URI, a "uniform resource indicator".

With Flask apps, we only have to specify the routing string and the appropriate function that gets called when the routing string is entered into the user's browser. In this case, `/`, which canonically routes to the homepage of the website, is assigned to call on the `home()` function, which returns a function call to `render_template`.

What `render_template` is doing is telling the Flask app to fill in whatever is needed in the template, and then return the resulting HTML page to the browser.

`home()` is not particularly interesting, because we are simply rendering an HTML template that has no variable regions in it. Let's take a look at that template.

### HTML Template

```
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   ├── functions.py
│   └── templates
│       ├── index.html.j2 **
│       ├── qr.html.j2
│       └── template.html.j2
└── setup.py
```

```html
{% extends "template.html.j2" %}


{% block body %}

<div class="row">
  <div class="col-12">
    <h1>WiFi QR Code Creator</h1>
  </div>
  <div class="col-12">
    <form action="/create" method="post">
      <div class="form-group">
        <label for="ssid">SSID</label>
        <input class="form-control" type="text" name="ssid" id="ssid" placeholder="My WiFi Network Name">
      </div>

      <div class="form-group">
        <label for="security">Security Mode</label>
        <select class="form-control" name="security" id="security">
          <option value="WPA">WPA</option>
          <option value="WEP">WEP</option>
          <option value="">None</option>
        </select>
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input class="form-control" type="password" name="password" id="password" placeholder="Protection is good!">
      </div>

      <div class="form-group">
        <button class="btn btn-lg btn-success" type="submit">Create QR Code!</button>
      </div>

    </form>
  </div>
</div>

{% endblock %}
```

I won't go too deep into HTML here, as HTML is not the main focus of the blog post, but you just have to know that we get back an HTML page with a form on it that allows users to input their SSID, security type, and password. Do know, though, that knowing HTML is a preprequisite for building useful things on the web.

The other thing that will be useful for you to pick up is `jinja2` syntax. In this blog post, we used the `jinja2` templating syntax to organize our HTML code.

### View Functions (continued)

Let's go back to the view functions in `app.py`.

From the homepage, we have served up an HTML form that an end-user can input their WiFi information into. We now need a view function that will display back the resulting QR code. Let's call it `create()`, which points to the routing string `/create`.

```python
@app.route("/create", methods=["POST"])
def create():
    res = request.form
    qr = wifi_qr(ssid=res["ssid"], password=res["password"], security=res["security"])
    qr_b64 = qr.png_data_uri(scale=10)
    return render_template("qr.html.j2", qr_b64=qr_b64)
```

In the `create()` function, we do a few things.

Firstly, we get the submitted data from the form. It is a dictionary that we can key into. Then, we pass that information into the `wifi_qr` function which we imported from `functions.py`. Finally, we create the base64-encoded version of the QR code, which will let us display the QR code in the `qr.html.j2` template.

### QR Code Display Template

Let's now take a look at that particular template.

```html
{% extends "template.html.j2" %}

{% block body %}
<div class="row">
    <div class="col-12">
        <h1>WiFi QR Code Creator</h1>
        <p>Here is your QR Code!</p>
        <img src="{{ qr_b64|safe }}">
    </div>
</div>
{% endblock %}
```

Here, I hope the importance of the templating engine comes to shine. We caninsert the base64-encoded PNG version of the QR code into the HTML page by passing the `qr_b64` variable into the `render_template()` function, which then gets inserted inside the `<img>` tag. The base64-encoded QR code is going to vary, but the HTML tags surrounding it remain constant, so we only have to set it as a variable in the HTML template.

### Back to the View Function

Finally, let's introduce the final part of `app.py`.

```python
def run():
    app.run(debug=True, port=5690, host="0.0.0.0")

if __name__ == "__main__":
    run()
```

Here, the essence of what we've done is to serve the Flask app on port 5690 on our localhost. I opted to use a wrapper similar to the CLI app so that we can also launch the Flask app from the command-line!

### Putting it all together

With that, let's see the entirety of `app.py` together:

```python
from flask import Flask, render_template, request

from qrwifi.functions import wifi_qr


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html.j2")


@app.route("/create", methods=["POST"])
def create():
    res = request.form
    print(res)
    qr = wifi_qr(ssid=res["ssid"], password=res["password"], security=res["security"])
    qr_b64 = qr.png_data_uri(scale=10)
    return render_template("qr.html.j2", qr_b64=qr_b64)


def run():
    app.run(debug=True, port=5690, host="0.0.0.0")

if __name__ == "__main__":
    run()
```

## Using the QR Code Creator

If you type at the terminal:

```bash
$ python app.py
```

you can then go to your browser, and input `localhost:5690`, and your Flask app will be live!

## Concluding Thoughts

I hope that this blog series has been illuminating for you, just as it has been illuminating for me bilding the app.

At the end of the day, there's one take-home concept I hope you've come to realize too: CLIs and web apps are nothing more than text-based front-ends to arbitrary code in the backend. It's been liberating for me when learning new things to have this thought framework supporting behind.

If you'd like to read the code in more detail, you can go to a [GitHub repository][gh] that I set up.

[gh]: https://github.com/ericmjl/qr-cad