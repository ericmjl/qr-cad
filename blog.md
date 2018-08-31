# How to create a CLI with Click

a.k.a. "crash course in Click, by example"

## Introduction

In my previous blog post, I showed you how to create a QR code and its corresponding 3D model using Python.

In this blog post, I'd like to leverage that code base to share with you some epiphanies that helped me see commonalities between command-line interfaces (CLIs) and web apps. Specifically:

> CLIs and web apps are nothing more than text end points to arbitrary code.

To do this, we're going to take the functions that we built in the last blog post, and create a command-line interface around them. In the next blog post, we'll do another crash course, except for building simple web apps with Flask!

## Building a Command-Line Interface (CLI)

Let's start with the CLI. This is an interface that lets you access a program from the command line, say, the Linux/macOS `bash` shell or a Windows command prompt.

An advantage of a command-line interface is that it is scriptable. In our case, this means that we can harness the CLI to programatically create many QR codes with a single command.

A disadvantage of a command-line interface is that it requires the end user to be familiar with the text commands that are supported. This can feel somewhat like memorizing incantations to perform magic (well, this does seem to jive with [Clarke's law](https://en.wikipedia.org/wiki/Clarke%27s_three_laws#Variants_of_the_third_law)). Thus, this motivates why we might want to build web/graphical user interfaces.

### Preparation to build a CLI

In the name of "good software engineering", we are going to first organize our functions a bit, and prepare to build this into a Python package that can be easily distributed. The final directory structure we are targeting is as follows:

```
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   ├── functions.py **
│   └── templates
│       ├── index.html.j2
│       ├── qr.html.j2
│       └── template.html.j2
└── setup.py
```

From this point onwards, I will highlight with askterisks (`*`) the file we should be editing.

### Functions Library

Let's start by creating `functions.py`. It should house the functions that we can import and call on.

```python

import numpy as np
import pyqrcode as pq


def wifi_qr(ssid: str, security: str, password: str):
    """
    Creates the WiFi QR code object.
    """
    qr = pq.create(f"WIFI:S:{ssid};T:{security};P:{password};;")
    return qr


def qr2array(qr):
    """
    Convert a QR code object into its array representation.
    """
    arr = []
    for line in qr.text().split("\n"):
        if len(line) != 0:
            arr.append([int(bit) for bit in line])
    return np.vstack(arr)


def png_b64(qr, scale: int = 10):
    """
    Return the base64 encoded PNG of the QR code.
    """
    return qr.png_data_uri(scale=scale)

```

### CLI Module

To build a CLI, we are going to use the Python package, [`Click`](http://click.pocoo.org/6/). You can install it using:

```
$ pip install click
```

What `click` provides is a clean and composable way of building command line interfaces to your Python code.

```bash
$ tree
.
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── cli.py **
│   └── functions.py
└── setup.py
```

Let's now build `cli.py`. (From this point on, I will highlight the file that we will be editing with a double asterisk (`**`)). This will contain our package's command line module. We'll architect it such that a user can use it as such:

```
$ qrwifi --ssid ${SSID_NAME} --security ${SECURITY} --password ${PASSWORD} [terminal|png --filename ${FILEPATH}]
```

To clarify, we would replace all of the `${...}` with appropriate strings, without the `$` symbol, without the `{}` braces.

I'll build your intuition bit-by-bit, and then we can take a look at everything together at the end. **For the full `cli.py`, scroll down beyond the explanations for a copy/pastable full file.**


```python
import numpy as np

import pyqrcode as pq

import click

from .functions import wifi_qr, qr2array


@click.group()
@click.option("--ssid", help="WiFi network name.")
@click.option("--security", type=click.Choice(["WEP", "WPA", ""]))
@click.option("--password", help="WiFi password.")
@click.pass_context
def main(ctx, ssid: str, security: str = "", password: str = ""):
    qr = wifi_qr(ssid=ssid, security=security, password=password)
    ctx.obj["qr"] = qr
```

We first start by importing the necessary packages, and begin with the `main()` function. According to its function signature, the `main()` function a `ctx` object (`ctx` is short for "context", more on this later), as well as the standard string fields that we need for putting together our WiFi QR code.

In the body of `main()`, we call on the `wifi_qr()` function defined in `functions.py`, and then assign the resulting `qr` object to `ctx.obj` (the context's object dictionary). If you're still wondering what this "context" object is all about, hang tight - I'm going to get there soon.

Apart from the function definition, you'll notice that we have decorated the function with `click` functions. This is where `click`'s magic comes into play. By decorating `main()` with `@click.group()`, we can now expose `main()` at the command line and call it from there! To expose its options to the command line as well, we have to decorate the function with `@click.option()`, and provide it with the appropriate "flag" that has to be added.

You'll also notice that there's this decorator, `@click.pass_context`. This is perhaps a good time to introduce the "context" object.

You'll notice that our CLI is architected such that we can output it to the terminal or to a PNG file on disk. In order to architect the program this way, we could have added another flag, but that would introduce extra complexity to the `main()` function. Thus, we need to have a "child" function of `main()`, which knows about what has been set up in `main()`.

In order to enable this, `@click.pass_context` decorates a function that accepts, as its first argument, a "context" object, whose child `.obj` attribute is a glorified dictionary. Well, in Python, everything is a dictionary so... Anyways, using this programming pattern, "child" functions can act on the context object and do whatever it needs. It's basically like passing state from the parent function to the child function.

Let's go on to build the "child" functions, which are named `terminal()` and `png()`.


```python
@main.command()
@click.pass_context
def terminal(ctx):
    """Print QR code to the terminal."""
    print(ctx.obj["qr"].terminal())


@main.command()
@click.option("--filename", help="full path to the png file")
@click.pass_context
def png(ctx, filename, scale: int = 10):
    """Create a PNG file of the QR code."""
    ctx.obj["qr"].png(filename, scale)
```

Both of our functions are decorated with `@main.command()`, which indicates to `click` that this is a "child" command of the `main()` function.

For `terminal()`, it does not have any options, because we want it printed directly to the terminal.

For the `png()` command, we want it saved to disk at some pre-specified path. Thus, it has another `@click.option()` attached to it.

```python

def start():
    main(obj={})


if __name__ == "__main__":
    start()

```

Finally, we have the `start()` function, which calls on the `main()` function. One thing we do when calling on the `main()` function is pass in an empty dictionary to the `obj` keyword. BUT WAIT! There's no `obj` keyword in our `main()` function; the first keyword is `ctx`, isn't it?

If you thought that, how astute of you! While I am not 100% sure as to why this works, here is my best guess: `click.pass_context` expects to see an `obj` keyword passed into the function call, and that in turn returns a context object that is passed into `main()` function.

Finally, we tell the Python interpreter to call on the `start()` function when we run the app. Some may question the design decision - why not just call on `main(obj={})`? I again don't have a good answer for this, except that when structured as shown below way, the code works as a command line app, but doesn't work otherwise.

### `cli.py` in full

As promised, here's the full `cli.py` that you can copy/paste.

```python
import numpy as np

import pyqrcode as pq

import click

from .functions import wifi_qr, qr2array


@click.group()
@click.option("--ssid", help="WiFi network name.")
@click.option("--security", type=click.Choice(["WEP", "WPA", ""]))
@click.option("--password", help="WiFi password.")
@click.pass_context
def main(ctx, ssid: str, security: str = "", password: str = ""):
    qr = wifi_qr(ssid=ssid, security=security, password=password)
    ctx.obj["qr"] = qr
    ctx.obj["ssid"] = ssid
    ctx.obj["security"] = security
    ctx.obj["password"] = password


@main.command()
@click.pass_context
def terminal(ctx):
    print(ctx.obj["qr"].terminal())


@main.command()
@click.option("--filename", help="full path to the png file")
@click.pass_context
def png(ctx, filename, scale: int = 10):
    ctx.obj["qr"].png(filename, scale)


def start():
    main(obj={})


if __name__ == "__main__":
    start()
```

### `qrwifi` at the Command Line

How does this look like at the command line? Let's see:

```bash
$ python cli.py --help
Usage: python cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --ssid TEXT            WiFi network name.
  --security [WEP|WPA|]
  --password TEXT        WiFi password.
  --help                 Show this message and exit.

Commands:
  png
  terminal
```

Look at that!! We didn't have to do any `argparse` tricks to make this gorgeous output show up! We even got a "help menu" for free, complete with the "help" text that we specified at the command line.

You'll notice that there's the Options section, with all of the options attached to the `main()` function, as well as a Commands section, with the child functions (`png()` and `terminal()`) available. The function name is exactly the command name at the CLI.

We're still not done though, because this `cli.py` is only accessible if we know where the file is. If we're distributing this as a package, we'd ideally like to abstract away the location of `cli.py`, instead having our end user call on a memorable name, say, `qrwifi`.

### Create a `setup.py`

To do this, we need another file, the `setup.py` file.

```bash
$tree
.
├── environment.yml
├── qrwifi
│   ├── __init__.py
│   ├── cli.py
│   └── functions.py
└── setup.py **
```

Let's take a look at the structure of the `setup.py` file. (You can also copy/paste this in full.)

```python
from setuptools import setup, find_packages

setup(
      # mandatory
      name="qrwifi",
      # mandatory
      version="0.1",
      # mandatory
      author_email="username@email.address",
      packages=['qrwifi'],
      package_data={},
      install_requires=['pyqrcode', 'SolidPython', 'numpy', 'Flask', 'click'],
      entry_points={
        'console_scripts': ['qrwifi = qrwifi.cli:start']
      }
)
```

In here, we specify a package `name`, `version`, and `author_email` (which I consider to be the most basic information that we need).

Under `packages`, we specify with a list of strings the directories that contain our Python package. In this case, it's a simple package that only has one directory, `qrwifi`. There are no other supplementary datasets that need to be packaged together, so we can leave it as an empty dictionary.

Under `install_requires`, we specify the packages that our Python package needs. When installing, Python will install those packages and their specified dependencies.

The final magical incantation that we have is the `entry_points` keyword. Here, we specify that we want to access qrwifi at the terminal with the `qrwifi` command. Thus, we pass in a dictionary that has a key `console_scripts` mapped to a list of `=`-delimited commands. Here, we map the string `qrwifi` to `qrwifi.cli:start` (or more generically: `package.name:function`).

If we save `setup.py` to disk, we can install the package from our current directory:

```bash
$ python setup.py develop
```

I have chosen `develop` instead of `install`, because in development mode, we can edit the source directly in the same directory, and immediately test changes. With `install`, the our files under `qrwifi` will be copied into your Python package directory.

### `qrwifi` at the Command Line: Retake!

Now, we can access the app from the command line, having only to call `qrwifi`.

```bash
$ qrwifi --help
Usage: qrwifi [OPTIONS] COMMAND [ARGS]...

Options:
  --ssid TEXT            WiFi network name.
  --security [WEP|WPA|]
  --password TEXT        WiFi password.
  --help                 Show this message and exit.

Commands:
  png
  terminal
```

An example usage of this CLI app to display a QR code at the terminal would be:

```bash
$ qrwifi --ssid "Kite Guest Network" --security "WPA" --password "vrilhkjasdf" terminal
```

And to save a PNG file to disk:

```bash
$ qrwifi --ssid "Kite Guest Network" --security "WPA" --password "vrilhkjasdf" png --filename ./kiteguest.png
```

## Conclusions

Hopefully, this blog post has shown you one useful example of how to build a command line app using Click. Click is powerful and easy-to-use - I consider it a rare feat of good software design! Big kudos to the pocoo group that makes Click for doing such a wonderful job with this package.

It also hopefully illustrates the point that I made above:

> CLIs and web apps are nothing more than text end points to arbitrary code.

Stay tuned for the next blog post, in which we add a web interface to create QR codes, using Flask!