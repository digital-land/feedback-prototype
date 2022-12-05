from flask import Blueprint, render_template, request

designs = Blueprint("designs", __name__, template_folder="templates")


def template_path(template_name):
    return f"designs/{template_name}"


def get_param_val(query_param):
    return request.args.get(query_param) if request.args.get(query_param) else False


@designs.route("/designs/provider", strict_slashes=False)
@designs.route("/designs/provider/<provider>/")
def provider(provider):
    return render_template(
        template_path("provider.html"),
        page_data={
            "organisation": {
                "name": provider if provider else "Borchester Borough Council"
            },
            "title": get_param_val("title")
            if get_param_val("title")
            else provider
            if provider
            else "Borchester Borough Council",
            "caption": get_param_val("caption") if get_param_val("caption") else False,
            "summary": {"show": True},
            "query_string": request.args.to_dict(),
            "status": ["Provided", "Unavailable", "Not found", "Problem collecting"],
        },
    )


@designs.route("/designs/provider/<provider>/<dataset>")
def provider_dataset(provider, dataset):
    return render_template(
        template_path("provider-dataset.html"),
        page_data={
            "organisation": {
                "name": provider if provider else "Borchester Borough Council"
            },
            "dataset": {"name": dataset},
            "title": dataset if dataset else "Dataset name",
            "lede": "Data provided by " + provider
            if provider
            else "Borchester Borough Council",
            "summary": {"show": True},
            "query_string": request.args.to_dict(),
            "status": ["Provided", "Unavailable", "Not found", "Problem collecting"],
        },
    )
