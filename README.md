uber-explore
=========

A random adventure in the Boston area

Setup
----

```
$ git clone https://github.com/carolinevdh/uber-explore.git
$ cd uber-explore
$ virtualenv env
New python executable in test/bin/python2.7
Also creating executable in test/bin/python
Installing setuptools, pip...done.
$ source env/bin/activate
$ pip install flask
```

The app requires a `config.json` file that contains information
(secrets) obtained from developer.uber.com for your app:

```
{"token": <developer token>,
"client_id": <developer client_id>
```

This config file should be placed in the main `uber-code/` directory,
the same directory which contains `application.py`.  These secrets
should not be checked into the repo!

Running the app
------

```
$ python application.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Open a browser to `http://127.0.0.1:5000/` and enjoy your adventure!