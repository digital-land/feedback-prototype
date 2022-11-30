from flask import Blueprint, render_template, request

designs = Blueprint("designs", __name__, template_folder="templates")


def template_path(template_name):
    return f"designs/{template_name}"


def get_param_val(query_param):
    return request.args.get(query_param) if request.args.get(query_param) else False


@designs.route("/designs/provider")
def provider():
    return render_template(
        template_path("provider.html"),
        page_data={
            "organisation": {"name": get_param_val("organisation")},
            "title": get_param_val("title"),
            "caption": get_param_val("caption"),
            "summary": {"show": True},
            "query_string": request.args.to_dict(),
        },
    )
