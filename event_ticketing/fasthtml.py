from fasthtml import FastHTML

fasthtml = FastHTML()

@fasthtml.route("/")
def index():
    return "Hello, World!"

fasthtml.run()
