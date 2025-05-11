from msword_properties_generator.utils.utils_config import config  # importing centralized config
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
    email_message['From'] = formataddr(("Dreamlead Github Actions", config['mail']['mail_sender_email']))
    email_message['To'] = email_address
    email_message.set_content(return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference), subtype='html')

    for filepath in generated_files:
        abs_full_path = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.debug(f"✉️ℹ️ File at location 'file name omitted for privacy' found, at absolute path 'file name omitted for privacy'")
        else:
            logging.warning(f"✉️⚠️ File at location 'file name omitted for privacy' not found, at absolute path 'file name omitted for privacy'!")

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
        logging.info(f"✉️✅ Email successfully sent to 'mail omitted for privacy'")
    except Exception as e:
        logging.error('✉️❌ An error occurred:', e)

def return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference):
    return f"""
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
    <div style="max-width:900px; margin:0 0 20px 0;">
        Dear {leverancier_naam},
        
        Here is the document you requested for {klant_naam} in the role of {klant_job_title} ({klant_job_reference}).
        The documents are attached as msword and pdf.
    </div>

    <!-- Container aligning content to the left (max-width: 900px, matching tables) -->
    <div style="max-width:900px; margin:0; padding:0;">

        <!-- Header Image aligned with table & h2 -->
        <div style="width:100%; margin:0 0 20px 0; text-align:center;">
            <img src="https://johantre.github.io/msword-properties-generator/logo.png" alt="Dreamlead" style="width:100%; max-width:500px; max-height: 50px; height:auto; display:block; margin: auto;">
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
        <div style="margin-top: 20px;">
            Yours sincerely,<br>
            Dreamlead Team<br><br>
            <small style="color: #666;">
                This is an automated email. Please do not reply to this email.
            </small>
        </div>

    </div>

</body>
    """
