import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="prompt")
def JakeTest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    result = {
        result: "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a pers    onalized response."
    }
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200
    )
