import azure.functions as func
import logging
import os
from azure.core import exceptions
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    #ロガーを取得
    # azure. で始まるモジュールのログすべてを取得
    logger = logging.getLogger('azure') 
    #ログレベルを設定
    logger.setLevel(logging.DEBUG)
    # ログメッセージのフォーマットを設定
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ログメッセージをコンソールに出力するハンドラーを作成
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    # ロガーにハンドラーを追加
    logger.addHandler(handler)

    # ログレベルの確認
    logging.info(
        f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, "
        f"WARNING={logger.isEnabledFor(logging.WARNING)}, "
        f"INFO={logger.isEnabledFor(logging.INFO)}, "
        f"DEBUG={logger.isEnabledFor(logging.DEBUG)}"
    )
    #環境変数の設定内容の確認
    logging.info("---環境変数の設定内容---")
    logging.info("AZURE_CLIENT_ID")
    logging.info(os.getenv("AZURE_CLIENT_ID"))
    logging.info("AZURE_CLIENT_SECRET")
    logging.info(os.getenv("AZURE_CLIENT_SECRET"))
    logging.info("AZURE_TENANT_ID")
    logging.info(os.getenv("AZURE_TENANT_ID"))
    logging.info("AZURE_CLIENT_CERTIFICATE_PATH")
    logging.info(os.getenv("AZURE_CLIENT_CERTIFICATE_PATH"))
    logging.info("AZURE_CLIENT_CERTIFICATE_PASSWORD")
    logging.info(os.getenv("AZURE_CLIENT_CERTIFICATE_PASSWORD"))
    logging.info("AZURE_USERNAME")
    logging.info(os.getenv("AZURE_USERNAME"))
    logging.info("AZURE_PASSWORD")
    logging.info(os.getenv("AZURE_PASSWORD"))
    logging.info("blob_service_uri")
    logging.info(os.getenv("blob_service_uri"))
    logging.info("-----------------------")
    try:
        # 認証オブジェクトを取得
        # logging_enable=True で HTTTP のログも出力デバックログを出力
        token_credential = ManagedIdentityCredential(logging_enable=True)
        
        # 取得するトークンのチェック
        # 明示的にトークンを取得 実行しなくてもblob_service_client.list_containers() など
        # 各 Azure リソース側のメソッドが自動的にトークンを呼び出し取得してくれる
        access_token_raw = token_credential.get_token("https://management.azure.com//.default").token
    
        # BlobServiceClient オブジェクトを作成
        #logging_enable=Trueでデバックログも  logging_body=True で HTTP のログも出力
        blob_service_client = BlobServiceClient(
            account_url=os.getenv("blob_service_uri"),
            credential=token_credential,
            logging_body=True,
            logging_enable=True)
        # 全てのコンテナをリストし、それらをコンソールに出力
        container_list = blob_service_client.list_containers()
        #logging.info(container_list)
        output=""
        for container in container_list:
            logging.info(container)
            output += container.name + "\n"

        return func.HttpResponse(
                f"Conainer List:, {output}!",
                status_code=200
        ) 
    except (
    exceptions.ClientAuthenticationError,
    exceptions.HttpResponseError
    ) as e:
        logging.error(e.message)
        return func.HttpResponse(
        "Internal Server Error!",
        status_code=500
        ) 