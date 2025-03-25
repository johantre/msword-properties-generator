from email.message import EmailMessage
from email.utils import formataddr
from jproperties import Properties
import logging
import smtplib
import os
import re




# Fetch properties
try:
    configs = Properties()
    with open('env/prod.properties', 'rb') as read_prop:
        configs.load(read_prop)
except (FileNotFoundError, Exception) as e:
    logging.error(f"❌Error reading properties file: {e}")
    raise SystemExit(e)

# Mail constructions
mail_smtp_port = configs.get("mail.smtp_port").data
mail_smtp_server = configs.get("mail.smtp_server").data
mail_sender_email = configs.get("mail.sender_email").data
# Path constructions
resource_path = configs.get("path.resource").data
output_path = configs.get("path.output").data
base_document_name = configs.get("base.word.template").data

word_template_path =  os.path.join(resource_path, base_document_name + '.docx')
base_output_document_path = os.path.join(output_path, base_document_name)

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
    base_document = f"{base_output_document_path} - {leverancier_naam} - {klant_naam} - {klant_job_title} - {klant_job_reference}"

    email_subject = f"Recht om te vertegenwoordigen documents for '{klant_naam}' for '{klant_job_title}' ({klant_job_reference})"
    email_message = EmailMessage()
    email_message['Subject'] = email_subject
    email_message['From'] = formataddr(("Github Actions", mail_sender_email))
    email_message['To'] = email_address
    email_message.set_content(return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference), subtype='html')

    for filepath in generated_files:
        abs_full_path = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.debug(f"ℹ️File at location '{filepath}' found, at absolute path {abs_full_path}")
        else:
            logging.warning(f"⚠️File at location '{filepath}' not found, at absolute path {abs_full_path}!")

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
        with smtplib.SMTP(mail_smtp_server, mail_smtp_port) as smtp:
            smtp.starttls()
            smtp.login(mail_sender_email, sender_password)
            smtp.send_message(email_message)
        logging.info(f'✅ Email successfully sent to {email_message['To']}')
    except Exception as e:
        logging.error('❗ An error occurred:', e)

def return_html_body(base_document, leverancier_naam, klant_naam, klant_job_title, klant_job_reference):
    return f"""
    <body>
        <h2>Recht om te vertegenwoordigen</h2>
        <table>
            <tr>
                <td><b>Leverancier Naam</b></td>
                <td>{leverancier_naam}</td>
            </tr>
            <tr>
                <td><b>Klant Naam</b></td>
                <td>{klant_naam}</td>
            </tr>
            <tr>
                <td><b>Klant JobTitle</b></td>
                <td>{klant_job_title}</td>
            </tr>
            <tr>
                <td><b>Klant JobReference</b></td>
                <td>{klant_job_reference}</td>
            </tr>
        </table>

        <h3>Documents Attached:</h3>
        <table>
            <tr>
                <td><b>MSWord</b></td>
                <td>{base_document}.docx</td>
            </tr>
            <tr>
                <td><b>Pdf</b></td>
                <td>{base_document}.pdf</td>
            </tr>
        </table>
    </body>
    """



