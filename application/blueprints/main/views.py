from flask import Blueprint, render_template

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/")
def index():
    return render_template("homepage.html")


@main.route("/organisation/<organisation>")
def organisation(organisation):
    return render_template(
        "organisation.html", routeData={"organisation": organisation}
    )
