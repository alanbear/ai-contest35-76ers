import azure.functions as func
import logging
import json
import os


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


@app.route(route="prompt")
def JakeTest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    message = req.get_json()
    logging.info("body:" + message)
    result = {
        "result": "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a pers    onalized response."
    }
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200,
    )


def is_running_in_azure_function() -> bool:
    return "fUNCTIONS_WORKER_RUNTIME" in os.environ
