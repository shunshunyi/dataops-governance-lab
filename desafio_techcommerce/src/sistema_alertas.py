from great_expectations.checkpoint.actions import ValidationAction


class CustomAlertAction(ValidationAction):
    def __init__(self, data_context, **kwargs):
        super().__init__(data_context)

    def _run(self, validation_result_suite, **kwargs):
        if not validation_result_suite.success:
            suite_name = validation_result_suite.expectation_suite_name
            failed_count = validation_result_suite.statistics.get('unsuccessful_expectations', 0)
            message = (f"🚨 ALERTA: Validação para '{suite_name}' falhou! {failed_count} expectativas não foram atendidas.")
            print("\n" + "="*50 + "\nSIMULAÇÃO DE ALERTA\n" + "="*50 + f"\n{message}\n" + "="*50 + "\n")
