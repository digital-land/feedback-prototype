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
            "organisation": {
                "name": get_param_val("organisation")
                if get_param_val("organisation")
                else "Borchester Borough Council"
            },
            "title": get_param_val("title")
            if get_param_val("title")
            else "Borchester Borough Council",
            "caption": get_param_val("caption")
            if get_param_val("caption")
            else "Data Provider",
            "summary": {"show": True},
            "query_string": request.args.to_dict(),
            "status": ["Provided", "Unavailable", "Not found", "Problem collecting"],
        },
    )
