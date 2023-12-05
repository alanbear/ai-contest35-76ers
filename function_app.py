import azure.functions as func
import logging
import json
import dataclasses
import openai
import requests
import os


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class OpenAiConfig:
    api_type: str
    api_version: str
    api_key: str
    api_base_url: str
    deployment_id: str

    def __repr__(self):
        return f"OpenAiConfig(api_type={self.api_type}, api_version={self.api_version}, api_key='***', api_base_url={self.api_base_url}, deployment_id={self.deployment_id})"

    def __str__(self):
        return self.__repr__()


@dataclasses.dataclass
class AiSearchConfig:
    search_endpoint: str
    search_key: str
    search_index: str

    def __repr__(self):
        return f"AiSearchConfig(search_endpoint={self.search_endpoint}, search_key='***', search_index={self.search_index})"

    def __str__(self):
        return self.__repr__()


@dataclasses.dataclass
class AiSearchInput:
    description: str


@dataclasses.dataclass
class AiSearchResult:
    result: str


def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter(),
    )

    openai.requestssession = session


@app.route(route="prompt")
def JakeTest(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    apikey = os.environ["api_key"]
    searchkey = os.environ["search_key"]
    logger.info("api_key: %s, search_key: %s", apikey, searchkey)
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


def get_openai_config() -> OpenAiConfig:
    return OpenAiConfig(
        api_type=os.environ["OPENAI_API_TYPE"],
        api_version=os.environ["OPENAI_API_VERSION"],
        api_key=os.environ["OPENAI_API_KEY"],
        api_base_url=os.environ["OPENAI_API_BASE_URL"],
        deployment_id=os.environ["OPENAI_DEPLOYMENT_ID"],
    )


def get_ai_search_config() -> AiSearchConfig:
    return AiSearchConfig(
        search_endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        search_key=os.environ["AZURE_SEARCH_KEY"],
        search_index=os.environ["AZURE_SEARCH_INDEX"],
    )


def setup_byod(deployment_id: str) -> None:
    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter(),
    )

    openai.requestssession = session


def setup_openai(open_ai_config: OpenAiConfig) -> None:
    openai.api_type = open_ai_config.api_type
    openai.api_key = open_ai_config.api_key
    openai.api_base = open_ai_config.api_base_url
    openai.api_version = open_ai_config.api_version


def query_openai(input_str: AiSearchInput) -> AiSearchResult:
    logger.info("Input: %s", input_str)
    if is_running_in_azure_function():
        logger.info("Running in Azure Function. No need to load .env file")
    else:
        logger.info("Running locally. Loading .env file")
        try:
            import dotenv

            dotenv.load_dotenv(".env")
        except Exception:
            logger.exception("Failed to load .env file")
    open_ai_config = get_openai_config()
    ai_search_config = get_ai_search_config()
    setup_openai(open_ai_config)
    setup_byod(open_ai_config.deployment_id)
    message_text = [
        {
            "role": "user",
            "content": "have we seen the file in the dataset? C:\\Users\\charles123\\Downloads\\adjuntos_13_06 (1).html , reply in the following format : 'answer', 'file sha1', 'date', 'rule id', 'industry', 'status tag' and the 'reason' of your analysis.",
        }
    ]

    logger.info("open_ai_config: %s", open_ai_config)
    logger.info("ai_search_config: %s", ai_search_config)
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=open_ai_config.deployment_id,
        dataSources=[  # camelCase is intentional, as this is the format the API expects
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": ai_search_config.search_endpoint,
                    "key": ai_search_config.search_key,
                    "indexName": ai_search_config.search_index,
                },
            }
        ],
    )
    logger.info("Completion: %s", completion)
    result = completion.choices[0].message.content
    logger.info("Result: %s", result)
    return AiSearchResult(result=result)


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
