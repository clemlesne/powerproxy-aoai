"""Declares a plugin to log usage infos to a CSV file."""

# pylint: disable=invalid-name,too-many-arguments,import-error,no-name-in-module,too-few-public-methods

from azure.identity import ChainedTokenCredential, ClientSecretCredential, ManagedIdentityCredential
from azure.monitor.ingestion import LogsIngestionClient
from helpers.dicts import QueryDict
from plugins.LogUsage.LogUsageBase import LogUsageBase


class LogUsageToLogAnalytics(LogUsageBase):
    """Logs Azure OpenAI usage info to a Log Analytics table."""

    log_ingestion_endpoint = None
    credential_tenant_id = None
    credential_client_id = None
    credential_client_secret = None
    data_collection_rule_id = None
    stream_name = None

    log_analytics_client = None

    def __init__(self, app_configuration, plugin_configuration: QueryDict):
        """Constructor."""
        super().__init__(app_configuration, plugin_configuration)

        self.log_ingestion_endpoint = plugin_configuration.get("log_ingestion_endpoint")
        self.credential_tenant_id = plugin_configuration.get("credential_tenant_id")
        self.credential_client_id = plugin_configuration.get("credential_client_id")
        self.credential_client_secret = plugin_configuration.get("credential_client_secret")
        self.data_collection_rule_id = plugin_configuration.get("data_collection_rule_id")
        self.stream_name = plugin_configuration.get("stream_name")

        print()
        print(f"Log ingestion endpoint          : {self.log_ingestion_endpoint}")
        print(f"Credential Tenant ID            : {self.credential_tenant_id}")
        print(f"Credential Client ID            : {self.credential_client_id}")
        print(f"Data Collection Rule ID         : {self.data_collection_rule_id}")
        print(f"Stream Name                     : {self.stream_name}")

    def on_plugin_instantiated(self):
        """Run directly after the new plugin instance has been instantiated."""
        super().on_plugin_instantiated()

        self.log_analytics_client = LogsIngestionClient(
            endpoint=self.log_ingestion_endpoint,
            credential=ChainedTokenCredential(
                ManagedIdentityCredential(),
                ClientSecretCredential(
                    tenant_id=self.credential_tenant_id,
                    client_id=self.credential_client_id,
                    client_secret=self.credential_client_secret,
                ),
            ),
            logging_enable=True,
        )

    def _append_line(
        self,
        # pylint: disable=unused-argument
        request_start_minute,
        # pylint: enable=unused-argument
        request_start_minute_utc,
        client,
        is_streaming,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        openai_processing_ms,
        openai_region,
    ):
        """Append a new line with the given infos."""
        # pylint: disable=no-value-for-parameter
        self.log_analytics_client.upload(
            rule_id=self.data_collection_rule_id,
            stream_name=self.stream_name,
            logs=[
                {
                    "Client": client,
                    "RequestStartMinute": request_start_minute_utc,
                    "IsStreaming": is_streaming,
                    "PromptTokens": prompt_tokens,
                    "CompletionTokens": completion_tokens,
                    "TotalTokens": total_tokens,
                    "OpenAIProcessingMS": openai_processing_ms,
                    "OpenAIRegion": openai_region,
                }
            ],
        )
        # pylint: enable=no-value-for-parameter
