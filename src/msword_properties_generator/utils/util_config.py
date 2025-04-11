from jproperties import Properties
from pathlib import Path
import logging


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROD_PROPERTIES_FILE = PROJECT_ROOT / "env" / "prod.properties"


def get_property_value(configs, key):
    """
    Safely get a property value from the configs object.
    
    Args:
        configs: The Properties object containing the configuration
        key: The key to look up
        
    Returns:
        The property value if found
        
    Raises:
        SystemExit: If the property is not found
    """
    prop = configs.get(key)
    if prop is None:
        error_msg = f"❌ Required property '{key}' is missing in the properties file"
        logging.error(error_msg)
        raise SystemExit(error_msg)
    return prop.data


# Fetch properties
def load_config_values(properties_path=PROD_PROPERTIES_FILE):
    configs = Properties()
    try:
        with open(properties_path, 'rb') as read_prop:
            configs.load(read_prop)
    except (FileNotFoundError, Exception) as e:
        logging.error(f"❌ Error reading properties file: {e}")
        raise SystemExit(e)

    # Get all required properties
    resource_path = get_property_value(configs, "path.resource")
    output_path = get_property_value(configs, "path.output")
    template_name = get_property_value(configs, "base.word.template")
    db_file = get_property_value(configs, "db.file")
    image_signature_folder = get_property_value(configs, "path.resource.image_signature_folder")
    xls_offers_log = get_property_value(configs, "base.excel.offers.log")
    xls_offers_log_sheetname = get_property_value(configs, "base.excel.offers.log.sheetname")
    xls_offers_provider = get_property_value(configs, "base.excel.offers.provider")
    xls_offers_provider_sheetname = get_property_value(configs, "base.excel.offers.provider.sheetname")
    xls_offers_customer = get_property_value(configs, "base.excel.offers.customer")
    xls_offers_customer_sheetname = get_property_value(configs, "base.excel.offers.customer.sheetname")
    namespace_cp = get_property_value(configs, "base.word.namespace.cp")
    namespace_vt = get_property_value(configs, "base.word.namespace.vt")
    alt_text_left = get_property_value(configs, "base.word.template.image_alt_text_left")
    alt_text_right = get_property_value(configs, "base.word.template.image_alt_text_right")
    mail_smtp_port = get_property_value(configs, "mail.smtp_port")
    mail_smtp_server = get_property_value(configs, "mail.smtp_server")
    mail_sender_email = get_property_value(configs, "mail.sender_email")
    dropbox_destination_folder = get_property_value(configs, "path.dropbox.destination.folder")

    return {
        "paths": {
            "db_path": PROJECT_ROOT / resource_path / db_file,
            "resource_path": resource_path,
            "output_path": output_path,
            "image_signature_folder": PROJECT_ROOT / resource_path / image_signature_folder,
            "word_template_path": PROJECT_ROOT / resource_path / f"{template_name}.docx",
            "base_output_document_path": PROJECT_ROOT / output_path / template_name,
            "xls_offers_log": PROJECT_ROOT / resource_path / xls_offers_log,
            "xls_offers_log_sheetname": xls_offers_log_sheetname,
            "xls_offers_provider": PROJECT_ROOT / resource_path / xls_offers_provider,
            "xls_offers_provider_sheetname": xls_offers_provider_sheetname,
            "xls_offers_customer": PROJECT_ROOT / resource_path / xls_offers_customer,
            "xls_offers_customer_sheetname": xls_offers_customer_sheetname,
            "base_document_name": template_name
        },
        "namespaces": {
            'cp': namespace_cp,
            'vt': namespace_vt,
        },
        "alt_texts": {
            "left": alt_text_left,
            "right": alt_text_right
        },
        "mail": {
            "mail_smtp_port": mail_smtp_port,
            "mail_smtp_server": mail_smtp_server,
            "mail_sender_email": mail_sender_email
        },
        "dropbox": {
            "dropbox_destination_folder": dropbox_destination_folder
        }
    }

# Global configuration loaded explicitly once when imported
config = load_config_values()
