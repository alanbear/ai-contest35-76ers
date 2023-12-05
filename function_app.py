import azure.functions as func
import logging
import json
import dataclasses
import os


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AiSearchInput:
    description: str


@dataclasses.dataclass
class AiSearchResult:
    result: str


@app.route(route="prompt")
def JakeTest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    message = req.get_json()
    if not message or "prompt" not in message:
        logger.error("Bad Request")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Please pass a description on the query string or in the request body"
                }
            ),
            mimetype="application/json",
            status_code=400,
        )
    input_prompt = message["prompt"]
    logger.info("input_prompt: %s", input_prompt)
    result = query_openai(AiSearchInput(description=input_prompt))
    return func.HttpResponse(
        json.dumps({"result": result.result}),
        mimetype="application/json",
        status_code=200,
    )


def is_running_in_azure_function() -> bool:
    return "fUNCTIONS_WORKER_RUNTIME" in os.environ


def query_openai(input_str: AiSearchInput) -> AiSearchResult:
    logger.info("Input: %s", input_str)
    if is_running_in_azure_function():
        logger.info("Running in Azure Function. No need to load .env file")
    else:
        logger.info("Running locally. Loading .env file")
        try:
            import dotenv

            dotenv.load_dotenv()
        except Exception:
            logger.exception("Failed to load .env file")
    return AiSearchResult(result="This is the result of the search")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        # need line number and a time and file
        # [] the time and level
        format="[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
    )

    # function all the patched function
    # I do not know how to invoke this function
    # from unittest import mock
    # print(
    #     JakeTest(
    #         mock.Mock(
    #             get_json=mock.Mock(return_value={"description": "This is a test"})
    #         )
    #     )
    # )

    # call the inner function instead
    print(query_openai(AiSearchInput(description="This is a test")))
