from jproperties import Properties
from pathlib import Path
import logging


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROD_PROPERTIES_FILE = PROJECT_ROOT / "env" / "prod.properties"


# Fetch properties
def load_config_values(properties_path=PROD_PROPERTIES_FILE):
    configs = Properties()
    try:
        with open(properties_path, 'rb') as read_prop:
            configs.load(read_prop)
    except (FileNotFoundError, Exception) as e:
        logging.error(f"❌ Error reading properties file: {e}")
        raise SystemExit(e)

    resource_path = configs.get("path.resource").data
    output_path = configs.get("path.output").data
    template_name = configs.get("base.word.template").data

    return {
        "paths": {
            "db_path": PROJECT_ROOT / resource_path / configs.get("db.file").data,
            "resource_path": resource_path,
            "output_path": output_path,
            "image_signature_folder": PROJECT_ROOT / resource_path / configs.get("path.resource.image_signature_folder").data,
            "word_template_path": PROJECT_ROOT / resource_path / f"{template_name}.docx",
            "base_output_document_path": PROJECT_ROOT / output_path / template_name,
            "xls_offers_log": PROJECT_ROOT / resource_path / configs.get("base.excel.offers.log").data,
            "xls_offers_log_sheetname": configs.get("base.excel.offers.log.sheetname").data,
            "xls_offers_provider": PROJECT_ROOT / resource_path / configs.get("base.excel.offers.provider").data,
            "xls_offers_provider_sheetname": configs.get("base.excel.offers.provider.sheetname").data,
            "xls_offers_customer": PROJECT_ROOT / resource_path / configs.get("base.excel.offers.customer").data,
            "xls_offers_customer_sheetname": configs.get("base.excel.offers.customer.sheetname").data,
            "base_document_name": configs.get("base.word.template").data
        },
        "namespaces": {
            'cp': configs.get("base.word.namespace.cp").data,
            'vt': configs.get("base.word.namespace.vt").data,
        },
        "alt_texts": {
            "left": configs.get("base.word.template.image_alt_text_left").data,
            "right": configs.get("base.word.template.image_alt_text_right").data
        },
        "mail": {
            "mail_smtp_port": configs.get("mail.smtp_port").data,
            "mail_smtp_server": configs.get("mail.smtp_server").data,
            "mail_sender_email": configs.get("mail.sender_email").data
        },
        "dropbox": {
            "dropbox_destination_folder": configs.get("path.dropbox.destination.folder").data
        }
    }

# Global configuration loaded explicitly once when imported
config = load_config_values()
