## cintel-05-cintel

Module 5 involves working with deques and reactive values to add live data to a pyshiny project.

# Create and Activate Project Virtual Environment

```shell
py -m venv .venv
.venv\Scripts\Activate
```

# Install and update packages from requirements.txt

```shell
py -m pip install --upgrade -r requirements.txt
```

# Freeze requirements

```shell
py -m pip freeze > requirements.txt
```

# Install websockets
```shell
py -m pip install websocket-client
py -m pip install websockets==10.4 
```

# Build Client-Side App

```shell
shiny static-assets remove
shinylive export dashboard docs
py -m http.server --directory docs --bind localhost 8008
```

Open web browser (I use Chrome) and navigate to http://localhost:8008

# Update GitHub Repository

```shell
git add .
git commit -m "Update GitHub Repository with local build and add to Pages"
git push -u origin main
```

