import azure.functions as func
import logging
import json
import os


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


@app.route(route="prompt")
def JakeTest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    input_prompt = req.get_json()["prompt"]
    logging.info("input_prompt: " + input_prompt)

    result = {
        "result": "Put openAI result here"
    }
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200,
    )


def is_running_in_azure_function() -> bool:
    return "fUNCTIONS_WORKER_RUNTIME" in os.environ
