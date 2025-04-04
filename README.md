# msword-properties-generator

This repo will facilitate in generating a MSWord document and update its Custom properties and generate an accompanying .pdf.
The user can provide a Dropbox, Google Drive or MS OneDrive link to a signature image to include in the document. 
- MSWord template document (containing Custom properties).
- Link to signature image

Either 2 types of information that will be consumed to insert in the document;   
  - Customer information in two ways: 
    - By means of an MSExcel workbook containing the Customer Custom Properties ([OffersCustomer.xlsx](res%2FOffersCustomer.xlsx)).  
     Multiple Customers are possible. For each Customer an MSWord and pdf pair will be generated and send to you. 
    - By means of filling out a GitHub Actions form.<br>
  - Provider information:  
    - By means of filling out a GitHub Actions form.<br>
    That information will be encrypted and stored in this repo for you to later use again.<br>

At the moment of writing, depending of your choice, the above actions will result in:
- Sending a mail to the provided mail of the provider with the generated documents 
- Uploading the documents to the Dropbox of the owner of this repository.
- Customer data will not be stored. 
- Provider data will be stored in this Repo, encrypted to protect your privacy.

## Resources 
[offers_provider.db](res/offers_provider.db) All Providers are stored and encrypted in here with their hashed mail as key. \
[Recht om te vertegenwoordigen.docx](res/Recht%20om%20te%20vertegenwoordigen.docx) MSWord template containing the Custom properties.\
[OffersCustomer.xlsx](res/OffersCustomer.xlsx) Main xlsx to use as a vehicle to provide single or multiple Customer data to set into the .docx file above.\
[prod.properties](env/prod.properties) Properties for this logic to run containing all file names, folder locations.

## Future enhancements
- Removing a Provider from this repo functionality to stay GDPR compliant.
- Some code cleanup 

## Usage
In order to have a proper generated documents we need our Customer and Provider data. Below how to do that.  

### Provider data
Provider data doesn't change that much over time. Hence, since it's about quite some fields, that data is stored in this repo. 
How to provide? 
- GitHub Actions > Select "Subscribe provider" workflow > "Run workflow" to add yourself as a Provider to the [offers_provider.db](res/offers_provider.db).<br>
Your data will be encrypted to protect your privacy.<br>
The last field you can provide an URL to Dropbox, Google Drive or OneDrive to a signature image.< 
<br><a href="assets/img_1.png"><img src="assets/img_1.png" width="200"></a><br>
Take into account a white background so it matches the background color of the document.  
In order for this to work, you'll need to share the image with permissions to "everyone that has the link".<br>
Once this process is done, you can remove that permission again.<br>
The image will be encrypted and stored in this repo under a hashed name to protect your privacy. 


### Customer data
Customer data changes frequently. Every time you need documents to be generated these parameters are different, and are only a few fields. 
How to provide? 2 options: 
- Update the [OffersCustomer.xlsx](res/OffersCustomer.xlsx) locally, Git commit & Push it back to this Repo. (Requires some Git knowledge) 
- GitHub Actions > Select "Generate, Send and add to Dropbox" workflow > "Run workflow"<br>to generate the documents and have them send to you.<br><a href="assets/img.png"><img src="assets/img.png" width="200"></a>

