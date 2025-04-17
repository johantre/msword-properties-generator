from msword_properties_generator.utils.util_config import config  # importing centralized config
from email.message import EmailMessage
from email.utils import formataddr
import logging
import smtplib
import os
import re


def sanitize_filename(filename_part):
    return re.sub(r'[*<>:"/\\|?]', '_', filename_part).strip()

def safe_get(row, column_name, default='unknown'):
    return sanitize_filename(str(row[column_name]).strip()) if column_name in row else default

def send_email(generated_files, email_address, provider_replacements, customer_replacements):
    # Email setup (fill properly!)
    sender_password = os.getenv("APP_PASS_MAIL")
    if sender_password is None:
        raise EnvironmentError("❗ APP_PASS_MAIL environment variable is not set. "
                               "Please set this environment variable locally or via GitHub Secrets, or on your local environment as an environment variable.")

    leverancier_naam = safe_get(provider_replacements, "LeverancierNaam")
    klant_naam = safe_get(customer_replacements, "KlantNaam")
    klant_job_title = safe_get(customer_replacements, "KlantJobTitle")
    klant_job_reference = safe_get(customer_replacements, "KlantJobReference")
    base_document = f"{config['paths']['base_document_name']} - {leverancier_naam} - {klant_naam} - {klant_job_title} - {klant_job_reference}"

    email_subject = f"Recht om te vertegenwoordigen documents for '{klant_naam}' for '{klant_job_title}' ({klant_job_reference})"
    email_message = EmailMessage()
    email_message['Subject'] = email_subject
    email_message['From'] = formataddr(("Github Actions", config['mail']['mail_sender_email']))
    email_message['To'] = email_address
    email_message.set_content(return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference), subtype='html')

    for filepath in generated_files:
        abs_full_path = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.debug(f"✉️ℹ️ File at location '{filepath}' found, at absolute path {abs_full_path}")
        else:
            logging.warning(f"✉️⚠️ File at location '{filepath}' not found, at absolute path {abs_full_path}!")

        file_basename = os.path.basename(filepath)
        with open(abs_full_path, 'rb') as file:
            file_data = file.read()

            # Choosing the right MIME type explicitly for each file
            if filepath.endswith('.xlsx'):
                maintype, subtype = 'application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filepath.endswith('.docx'):
                maintype, subtype = 'application', 'vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filepath.endswith('.pdf'):
                maintype, subtype = 'application', 'pdf'
            else:
                maintype, subtype = 'application', 'octet-stream'

            email_message.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=file_basename
            )
    # Send email securely
    try:
        with smtplib.SMTP(config["mail"]["mail_smtp_server"], config["mail"]["mail_smtp_port"]) as smtp:
            smtp.starttls()
            smtp.login(config["mail"]["mail_sender_email"], sender_password)
            smtp.send_message(email_message)
        logging.info(f"✉️✅ Email successfully sent to {email_message['To']}")
    except Exception as e:
        logging.error('✉️❌ An error occurred:', e)

def return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference):
    return f"""
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">

    <!-- Container aligning content to the left (max-width: 900px, matching tables) -->
    <div style="max-width:900px; margin:0; padding:0;">

        <!-- Header Image aligned with table & h2 -->
        <div style="width:100%; margin:0 0 20px 0; text-align:center;">
            <img src="data:image/png;base64,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"
                 alt="Company Logo"
                 style="width:100%; max-width:500px; height:auto; display:block;">
        </div>

        <!-- Centered H2 within exact table width -->
        <h2 style="margin:0 0 15px 0; text-align:center;">
            Recht om te vertegenwoordigen
        </h2>

        <!-- Left aligned Table -->
        <table style="border-collapse: collapse; width:100%; margin: 0 0 20px 0;">
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    Leverancier Naam
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {leverancier_naam}
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    Klant Naam
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {klant_naam}
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    Klant JobTitle
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {klant_job_title}
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    Klant JobReference
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {klant_job_reference}
                </td>
            </tr>
        </table>

        <!-- Left aligned H3 -->
        <h3 style="margin:0 0 10px 0; text-align:left;">
            Documents Attached:
        </h3>

        <!-- Left Aligned 2nd Table -->
        <table style="border-collapse: collapse; width:100%; margin: 0 0 20px 0;">
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    MSWord
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {base_document}.docx
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding:8px; width:1%; white-space: nowrap; font-weight:bold;">
                    Pdf
                </td>
                <td style="border: 1px solid #ccc; padding:8px;">
                    {base_document}.pdf
                </td>
            </tr>
        </table>

    </div>

</body>
    """
