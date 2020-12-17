from flask import Flask , render_template , request

app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def hello():
    if request.method =='POST':
        if request.values['send']=='Search':
            return render_template('index.html',name=request.values['user'])
    return render_template("index.html",name="")

if __name__ == '__main__':
    print("start run")
    app.run() #啟動伺服器