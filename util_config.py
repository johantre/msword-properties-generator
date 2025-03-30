from jproperties import Properties
import logging
import os


# Fetch properties
def load_config_values(properties_path="env/prod.properties"):
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
            "db_path": os.path.join(resource_path, configs.get("db.file").data),
            "resource_path": resource_path,
            "output_path": output_path,
            "image_file_path": os.path.join(resource_path, configs.get("path.resource.image_signature").data),
            "word_template_path": os.path.join(resource_path, f"{template_name}.docx"),
            "base_output_document_path": os.path.join(output_path, template_name),
            "xls_offers_log": os.path.join(resource_path, configs.get("base.excel.offers.log").data),
            "xls_offers_log_sheetname": configs.get("base.excel.offers.log.sheetname").data,
            "xls_offers_provider": os.path.join(resource_path, configs.get("base.excel.offers.provider").data),
            "xls_offers_provider_sheetname": configs.get("base.excel.offers.provider.sheetname").data,
            "xls_offers_customer": os.path.join(resource_path, configs.get("base.excel.offers.customer").data),
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
