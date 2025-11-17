import great_expectations as gx
from great_expectations.core.yaml_handler import YAMLHandler
from typing import Any

yaml = YAMLHandler()

def configurar_checkpoint(context: Any) -> str:
    checkpoint_name = "techcommerce_checkpoint"
    checkpoint_config_str = f"""
name: {checkpoint_name}
config_version: 1.0
class_name: SimpleCheckpoint
run_name_template: "%Y%m%d-%H%M%S-validation"
validations:
  - batch_request:
      datasource_name: techcommerce_source
      data_asset_name: clientes_clean
    expectation_suite_name: clientes_suite
  - batch_request:
      datasource_name: techcommerce_source
      data_asset_name: produtos_clean
    expectation_suite_name: produtos_suite
  - batch_request:
      datasource_name: techcommerce_source
      data_asset_name: vendas_clean
    expectation_suite_name: vendas_suite
  - batch_request:
      datasource_name: techcommerce_source
      data_asset_name: logistica_clean
    expectation_suite_name: logistica_suite
action_list:
  - name: store_validation_result
    action:
      class_name: StoreValidationResultAction
  - name: update_data_docs
    action:
      class_name: UpdateDataDocsAction
  - name: send_alert_on_failure
    action:
      class_name: CustomAlertAction
"""
    context.add_or_update_checkpoint(**yaml.load(checkpoint_config_str))
    print(f"Checkpoint '{checkpoint_name}' configurado.")
    return checkpoint_name
